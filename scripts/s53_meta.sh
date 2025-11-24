#!/usr/bin/env bash
# S53 meta-script: register–semantic robustness + bias tests
# Runs directly on PhaseS/out/s50_folio_register_matrix.tsv

set -euo pipefail

echo "[S53-meta] Register–semantic robustness suite"

# Resolve BASE as the project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTD="$BASE/PhaseS/out"
REG_MATRIX="$OUTD/s50_folio_register_matrix.tsv"

echo "[S53-meta] BASE:     $BASE"
echo "[S53-meta] OUTD:     $OUTD"
echo "[S53-meta] REG_FILE: $REG_MATRIX"

if [ ! -s "$REG_MATRIX" ]; then
  echo "[S53-meta] ERROR: $REG_MATRIX not found or empty" >&2
  exit 1
fi

python - "$REG_MATRIX" "$OUTD" << 'PY'
import sys, math, random
from pathlib import Path

import pandas as pd

reg_path = Path(sys.argv[1])
out_dir = Path(sys.argv[2])

print(f"[S53-meta] Using register matrix: {reg_path}")
df = pd.read_csv(reg_path, sep="\t")

required_cols = [
    "folio",
    "known_semantic_tokens",
    "proc_frac",
    "bot_frac",
    "bio_frac",
    "register",
    "dominant_semantic_register",
    "section",
    "currier",
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"[S53-meta] ERROR: missing required columns in {reg_path}: {missing}", file=sys.stderr)
    sys.exit(1)

# Restrict to folios where we actually have semantics and a register label
df_use = df.copy()
df_use = df_use[df_use["register"].isin(["REGISTER_A", "REGISTER_B"])]
df_use = df_use[df_use["known_semantic_tokens"] > 0]
for col in ["proc_frac", "bot_frac", "bio_frac"]:
    df_use = df_use[df_use[col].notna()]

if df_use.empty:
    print("[S53-meta] ERROR: no usable rows after filtering (A/B + semantic coverage).", file=sys.stderr)
    sys.exit(1)

print(f"[S53-meta] Usable folios (A/B + semantic coverage): {len(df_use)}")

def assign_dom(row, t_proc, t_bot, t_bio):
    """Recompute dominant semantic register with thresholds and a MIXED fallback."""
    pf = float(row["proc_frac"])
    bf = float(row["bot_frac"])
    bif = float(row["bio_frac"])
    scores = {"PROC": pf, "BOT": bf, "BIO": bif}
    winner = max(scores, key=scores.get)
    if winner == "PROC" and pf >= t_proc:
        return "PROC_DOM"
    if winner == "BOT" and bf >= t_bot:
        return "BOT_DOM"
    if winner == "BIO" and bif >= t_bio:
        return "BIO_DOM"
    return "MIXED"

def contingency_and_v(df_local, label_col):
    """Compute contingency table and Cramér's V for register × semantic label."""
    regs = ["REGISTER_A", "REGISTER_B"]
    dom_cats = ["BOT_DOM", "BIO_DOM", "PROC_DOM", "MIXED"]

    # Build observed table
    obs = []
    for r in regs:
        row_counts = []
        for d in dom_cats:
            row_counts.append(int(((df_local["register"] == r) & (df_local[label_col] == d)).sum()))
        obs.append(row_counts)

    # Flatten + totals
    total = sum(sum(row) for row in obs)
    if total == 0:
        return 0.0, 0.0, 0, 0, obs, None

    # Row / column sums
    row_sums = [sum(row) for row in obs]
    col_sums = [sum(obs[i][j] for i in range(len(obs))) for j in range(len(obs[0]))]

    # Expected + chi^2
    chi2 = 0.0
    expected = []
    for i in range(len(obs)):
        erow = []
        for j in range(len(obs[0])):
            e = row_sums[i] * col_sums[j] / total if total > 0 else 0.0
            erow.append(e)
            if e > 0:
                chi2 += (obs[i][j] - e) ** 2 / e
        expected.append(erow)

    # Cramér's V
    r = len(obs)
    c = len(obs[0])
    k = min(r, c)
    if k <= 1:
        V = 0.0
    else:
        V = math.sqrt(chi2 / (total * (k - 1)))

    # Off-diagonal w.r.t. “ideal” mapping:
    # REGISTER_A should align with BOT_DOM/BIO_DOM,
    # REGISTER_B with PROC_DOM.
    # Everything else counts as off-diagonal.
    # Index mapping: dom_cats = [BOT, BIO, PROC, MIXED]
    idx_bot = dom_cats.index("BOT_DOM")
    idx_bio = dom_cats.index("BIO_DOM")
    idx_proc = dom_cats.index("PROC_DOM")

    aligned = obs[0][idx_bot] + obs[0][idx_bio] + obs[1][idx_proc]
    offdiag = total - aligned

    return chi2, V, total, offdiag, obs, expected

def write_table(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")

# -----------------------------
# 1. Baseline using existing dominant_semantic_register
# -----------------------------
baseline_df = df_use.copy()
# Keep only BOT/BIO/PROC for the main 2×3 view (drop MIXED/other for baseline V)
baseline_df = baseline_df[baseline_df["dominant_semantic_register"].isin(["BOT_DOM", "BIO_DOM", "PROC_DOM"])]

if baseline_df.empty:
    print("[S53-meta] WARNING: no BOT/BIO/PROC-only rows for baseline; skipping baseline contingency.")
else:
    chi2_base, V_base, N_base, offdiag_base, obs_base, exp_base = contingency_and_v(
        baseline_df.rename(columns={"dominant_semantic_register": "dom_base"}),
        "dom_base",
    )
    print(f"[S53-meta] Baseline (existing dom labels): N={N_base}, chi2={chi2_base:.4f}, V={V_base:.4f}, offdiag={offdiag_base}")

    # Write baseline contingency + expected
    regs = ["REGISTER_A", "REGISTER_B"]
    dom_cats = ["BOT_DOM", "BIO_DOM", "PROC_DOM", "MIXED"]
    # For baseline, there should be no MIXED actually, but we keep shape consistent.
    baseline_cont_path = out_dir / "s53_meta_baseline_contingency.tsv"
    rows = []
    for i, r in enumerate(regs):
        for j, d in enumerate(dom_cats):
            if j >= len(obs_base[0]):
                continue
            rows.append([r, d, obs_base[i][j]])
    write_table(baseline_cont_path, ["register", "dom_class", "count"], rows)

    # Expected frequencies (only for BOT/BIO/PROC columns)
    if exp_base is not None:
        exp_rows = []
        for i, r in enumerate(regs):
            for j, d in enumerate(dom_cats[: len(exp_base[0])]):
                exp_rows.append([r, d, exp_base[i][j]])
        exp_path = out_dir / "s53_meta_expected_frequencies.tsv"
        write_table(exp_path, ["register", "dom_class", "expected_count"], exp_rows)

# -----------------------------
# 2. Threshold sweep robustness (S53b)
# -----------------------------
print("[S53-meta] Running threshold sweep (S53b)...")

thresholds = [x / 100.0 for x in range(40, 81, 5)]  # 0.40..0.80
rows_sweep = []

for t_proc in thresholds:
    for t_bot in thresholds:
        for t_bio in thresholds:
            tmp = df_use.copy()
            tmp["dom_recomputed"] = [
                assign_dom(row, t_proc, t_bot, t_bio) for _, row in tmp.iterrows()
            ]

            # We look at non-MIXED for a “high-confidence” table
            sub = tmp[tmp["dom_recomputed"] != "MIXED"].copy()
            N = len(sub)
            if N < 10:
                continue

            chi2, V, N2, offdiag, obs, exp = contingency_and_v(sub, "dom_recomputed")
            rows_sweep.append(
                [t_proc, t_bot, t_bio, N2, offdiag, V, chi2]
            )

sweep_path = out_dir / "s53_meta_threshold_sweep.tsv"
write_table(
    sweep_path,
    ["t_proc", "t_bot", "t_bio", "N", "offdiag_count", "cramers_V", "chi2"],
    rows_sweep,
)
print(f"[S53-meta] Threshold sweep written: {sweep_path}")

# -----------------------------
# 3. Mixed-case inclusion (S53c) at a baseline threshold (0.5)
# -----------------------------
print("[S53-meta] Computing mixed-case contingency (S53c)...")

t_proc = t_bot = t_bio = 0.5
tmp = df_use.copy()
tmp["dom_t05"] = [assign_dom(row, t_proc, t_bot, t_bio) for _, row in tmp.iterrows()]

chi2_mix, V_mix, N_mix, offdiag_mix, obs_mix, exp_mix = contingency_and_v(tmp, "dom_t05")
print(f"[S53-meta] Mixed-inclusive: N={N_mix}, chi2={chi2_mix:.4f}, V={V_mix:.4f}, offdiag={offdiag_mix}")

regs = ["REGISTER_A", "REGISTER_B"]
dom_cats = ["BOT_DOM", "BIO_DOM", "PROC_DOM", "MIXED"]

mix_cont_path = out_dir / "s53_meta_mixed_contingency.tsv"
rows = []
for i, r in enumerate(regs):
    for j, d in enumerate(dom_cats):
        rows.append([r, d, obs_mix[i][j]])
write_table(mix_cont_path, ["register", "dom_class", "count"], rows)

# -----------------------------
# 4. Randomization baseline (S53g-style)
# -----------------------------
print("[S53-meta] Running randomization baseline...")

# Use the t=0.5 classification and restrict to non-MIXED to build a "gold" alignment.
sub_gold = tmp[tmp["dom_t05"] != "MIXED"].copy()
if sub_gold.empty:
    print("[S53-meta] WARNING: no non-MIXED folios at t=0.5; skipping randomization.")
    rand_rows = []
else:
    labels = list(sub_gold["dom_t05"].values)
    R = 200
    rand_rows = []
    for r_id in range(R):
        shuffled = labels[:]
        random.shuffle(shuffled)
        sub_gold["dom_rand"] = shuffled
        chi2_r, V_r, N_r, offdiag_r, obs_r, exp_r = contingency_and_v(sub_gold, "dom_rand")
        rand_rows.append([r_id, V_r, chi2_r, N_r, offdiag_r])

rand_path = out_dir / "s53_meta_randomization_baseline.tsv"
write_table(rand_path, ["run_id", "cramers_V", "chi2", "N", "offdiag_count"], rand_rows)
print(f"[S53-meta] Randomization results written: {rand_path}")

# -----------------------------
# 5. Selection / coverage summary + short human-readable report
# -----------------------------
total_folios = len(df)
n_reg_AB = (df["register"].isin(["REGISTER_A", "REGISTER_B"])).sum()
n_semantic = (df["known_semantic_tokens"] > 0).sum()
n_use = len(df_use)

report_path = out_dir / "s53_meta_report.txt"
with report_path.open("w", encoding="utf-8") as f:
    f.write("S53 meta-report: Register–semantic robustness & bias tests\n")
    f.write(f"Source file: {reg_path}\n\n")
    f.write(f"Total folios in matrix: {total_folios}\n")
    f.write(f"Folios with REGISTER_A/REGISTER_B: {n_reg_AB}\n")
    f.write(f"Folios with known_semantic_tokens>0: {n_semantic}\n")
    f.write(f"Folios used for A/B + semantic analyses (df_use): {n_use}\n\n")

    if baseline_df is not None and not baseline_df.empty:
        f.write("Baseline (existing dominant_semantic_register, BOT/BIO/PROC only):\n")
        f.write(f"  N = {N_base}\n")
        f.write(f"  chi^2 = {chi2_base:.4f}\n")
        f.write(f"  Cramer's V = {V_base:.4f}\n")
        f.write(f"  off-diagonal count (w.r.t A↔BOT/BIO, B↔PROC) = {offdiag_base}\n\n")

    f.write("Mixed-inclusive classification at thresholds t_proc=t_bot=t_bio=0.5:\n")
    f.write(f"  N = {N_mix}\n")
    f.write(f"  chi^2 = {chi2_mix:.4f}\n")
    f.write(f"  Cramer's V = {V_mix:.4f}\n")
    f.write(f"  off-diagonal count = {offdiag_mix}\n\n")

    if rand_rows:
        Vs = [row[1] for row in rand_rows]
        mean_V = sum(Vs) / len(Vs)
        f.write("Randomization baseline (shuffle semantic labels among non-MIXED folios):\n")
        f.write(f"  runs = {len(rand_rows)}\n")
        f.write(f"  mean Cramer's V (null) = {mean_V:.4f}\n")
        f.write("  min/max V(null) = {:.4f}/{:.4f}\n".format(min(Vs), max(Vs)))
        f.write("  (Compare this to observed baseline V above.)\n")

print(f"[S53-meta] Report written: {report_path}")
PY

echo "[S53-meta] Done. Outputs in $OUTD:"
echo "  - s53_meta_baseline_contingency.tsv"
echo "  - s53_meta_expected_frequencies.tsv"
echo "  - s53_meta_threshold_sweep.tsv"
echo "  - s53_meta_mixed_contingency.tsv"
echo "  - s53_meta_randomization_baseline.tsv"
echo "  - s53_meta_report.txt"
