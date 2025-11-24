#!/data/data/com.termux/files/usr/bin/bash
# S59 – Register–valency tests (S42 Herbal_A vs Proc_B)
# Uses section-specific valency summaries:
#   - s42_valency_suffix_summary_HERBAL_A_merged.tsv (≈ REGISTER_A / Herbal-A)
#   - s42_valency_suffix_summary_PROC_B_merged.tsv   (≈ REGISTER_B / Proc-B)
# to test whether valency-class distributions differ between the two registers.

set -eu
set -o pipefail

echo "[S59] Register–valency tests (S42 Herbal_A vs Proc_B)"

# ----------------------------------------------------------------------
# 1. Paths
# ----------------------------------------------------------------------

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"
OUTD="$BASE/PhaseS/out"

A_FILE="$OUTD/s42_valency_suffix_summary_HERBAL_A_merged.tsv"
B_FILE="$OUTD/s42_valency_suffix_summary_PROC_B_merged.tsv"

OUT_CONT="$OUTD/s59_register_valency_contingency.tsv"
OUT_EX="$OUTD/s59_register_valency_examples.tsv"
OUT_REP="$OUTD/s59_register_valency_report.txt"

echo "[S59] BASE:    $BASE"
echo "[S59] OUTD:    $OUTD"
echo "[S59] A_FILE:  $A_FILE"
echo "[S59] B_FILE:  $B_FILE"
echo "[S59] OUT_CONT:$OUT_CONT"
echo "[S59] OUT_EX:  $OUT_EX"
echo "[S59] OUT_REP: $OUT_REP"

mkdir -p "$OUTD"

if [ ! -s "$A_FILE" ]; then
  echo "[S59][ERROR] Missing or empty Herbal_A valency summary (S42): $A_FILE" >&2
  exit 1
fi

if [ ! -s "$B_FILE" ]; then
  echo "[S59][ERROR] Missing or empty Proc_B valency summary (S42): $B_FILE" >&2
  exit 1
fi

# ----------------------------------------------------------------------
# 2. Python analysis
# ----------------------------------------------------------------------

export A_FILE B_FILE OUT_CONT OUT_EX OUT_REP

python3 << 'PYEOF'
import os
import math
import numpy as np
import pandas as pd

A_FILE = os.environ["A_FILE"]
B_FILE = os.environ["B_FILE"]
OUT_CONT = os.environ["OUT_CONT"]
OUT_EX = os.environ["OUT_EX"]
OUT_REP = os.environ["OUT_REP"]

print(f"[S59(py)] Loading Herbal_A valency summary from: {A_FILE}")
a = pd.read_csv(A_FILE, sep="\t", dtype=str)
print("[S59(py)] Herbal_A columns:", list(a.columns))

print(f"[S59(py)] Loading Proc_B valency summary from: {B_FILE}")
b = pd.read_csv(B_FILE, sep="\t", dtype=str)
print("[S59(py)] Proc_B columns:", list(b.columns))

# --------------------------------------------------------------
# 2.1 Detect valency-class and count columns
# --------------------------------------------------------------

def pick_col(df, label, candidates, default=None):
    cols = [c for c in df.columns if isinstance(c, str)]
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in lower:
            chosen = lower[cand]
            print(f"[S59(py)] Using {label} column: {chosen}")
            return chosen
    if default is not None:
        print(f"[S59(py)] No explicit {label} column found, falling back to: {default}")
        return default
    raise ValueError(f"[S59] Could not find {label} column; tried: {candidates}, available: {cols}")

val_cand = ["valency_class", "primary_valency_class", "valency_band", "valency_id"]
# IMPORTANT: include total_hits / n_folios as possible count columns
cnt_cand = ["total_hits", "n_instances", "count", "freq", "total", "n", "n_folios"]

val_col_a = pick_col(a, "valency-class (Herbal_A)", val_cand)
val_col_b = pick_col(b, "valency-class (Proc_B)", val_cand)

cnt_col_a = pick_col(a, "count (Herbal_A)", cnt_cand, default=None)
cnt_col_b = pick_col(b, "count (Proc_B)", cnt_cand, default=None)

# If no explicit count column, treat each row as count 1
def get_counts(df, cnt_col):
    if cnt_col in df.columns:
        s = pd.to_numeric(df[cnt_col], errors="coerce").fillna(0.0)
        return s
    else:
        return pd.Series(1.0, index=df.index)

a["valency_class"] = a[val_col_a].astype(str).str.strip()
b["valency_class"] = b[val_col_b].astype(str).str.strip()
a["count"] = get_counts(a, cnt_col_a)
b["count"] = get_counts(b, cnt_col_b)

# Drop empty valency classes
a = a[a["valency_class"] != ""].copy()
b = b[b["valency_class"] != ""].copy()

# --------------------------------------------------------------
# 2.2 Build long-form table with register labels
# --------------------------------------------------------------

a_l = a[["valency_class", "count"]].copy()
a_l["register"] = "REGISTER_A"

b_l = b[["valency_class", "count"]].copy()
b_l["register"] = "REGISTER_B"

df = pd.concat([a_l, b_l], ignore_index=True)
df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0.0)

# Filter out non-positive counts
df = df[df["count"] > 0].copy()

if df.empty:
    raise ValueError("[S59] No positive counts after filtering Herbal_A/Proc_B valency tables.")

print(f"[S59(py)] Total weighted rows (Herbal_A + Proc_B): {len(df)}")

# --------------------------------------------------------------
# 2.3 Build contingency table (REGISTER × valency_class)
# --------------------------------------------------------------

reg_cats = ["REGISTER_A", "REGISTER_B"]
val_cats = sorted(df["valency_class"].unique().tolist())

cont = df.pivot_table(
    index="register",
    columns="valency_class",
    values="count",
    aggfunc="sum",
    fill_value=0.0,
).reindex(index=reg_cats, columns=val_cats, fill_value=0.0)

cont.to_csv(OUT_CONT, sep="\t", index=True)
print(f"[S59(py)] Wrote contingency table to: {OUT_CONT}")

obs = cont.values.astype(float)
rows, cols = obs.shape
N = obs.sum()

if N <= 0:
    raise ValueError("[S59] Contingency table has zero total count.")

row_sums = obs.sum(axis=1, keepdims=True)
col_sums = obs.sum(axis=0, keepdims=True)
expected = (row_sums @ col_sums) / N

mask = expected > 0
chi2 = ((obs - expected) ** 2 / np.where(mask, expected, 1.0)).sum()

df_chi = (rows - 1) * (cols - 1)
min_dim = min(rows - 1, cols - 1)
if min_dim <= 0:
    cramer_v = 0.0
else:
    cramer_v = math.sqrt(chi2 / (N * min_dim))

print(f"[S59(py)] chi² = {chi2:.4f}, df = {df_chi}, N = {N:.0f}, Cramer's V = {cramer_v:.4f}")

# --------------------------------------------------------------
# 2.4 Permutation baseline (shuffling register labels)
#    We expand counts into individual 'tokens' to keep it simple.
# --------------------------------------------------------------

# Build flat arrays of size N with valency labels and register labels
val_list = []
reg_list = []
for (valc, regc), sub in df.groupby(["valency_class", "register"]):
    w = int(round(sub["count"].sum()))
    if w <= 0:
        continue
    val_list.extend([valc] * w)
    reg_list.extend([regc] * w)

val_arr = np.array(val_list, dtype=object)
reg_arr = np.array(reg_list, dtype=object)

N_flat = len(val_arr)
print(f"[S59(py)] Expanded to {N_flat} token-level observations for permutation baseline.")

if N_flat == 0:
    v_null = np.array([0.0])
else:
    rng = np.random.default_rng(seed=59)
    n_iter = 200
    v_null = []

    for _ in range(n_iter):
        shuffled_regs = rng.permutation(reg_arr)
        cont_null = pd.crosstab(
            shuffled_regs,
            val_arr
        ).reindex(index=reg_cats, columns=val_cats, fill_value=0.0)

        obs_n = cont_null.values.astype(float)
        N_n = obs_n.sum()
        if N_n <= 0 or min_dim <= 0:
            v_null.append(0.0)
            continue

        rs_n = obs_n.sum(axis=1, keepdims=True)
        cs_n = obs_n.sum(axis=0, keepdims=True)
        exp_n = (rs_n @ cs_n) / N_n
        mask_n = exp_n > 0
        chi2_n = ((obs_n - exp_n) ** 2 / np.where(mask_n, exp_n, 1.0)).sum()
        v_null.append(math.sqrt(chi2_n / (N_n * min_dim)))

    v_null = np.array(v_null, dtype=float)

v_mean = float(v_null.mean())
v_std = float(v_null.std(ddof=1)) if len(v_null) > 1 else 0.0
v_p95 = float(np.quantile(v_null, 0.95)) if len(v_null) > 1 else 0.0

print(f"[S59(py)] Null Cramer's V: mean={v_mean:.4f}, sd={v_std:.4f}, 95th={v_p95:.4f}")

# --------------------------------------------------------------
# 2.5 Example rows: top-valency classes per register
# --------------------------------------------------------------

examples_rows = []
for regc in reg_cats:
    sub = df[df["register"] == regc]
    if sub.empty:
        continue
    ranked = sub.groupby("valency_class")["count"].sum().sort_values(ascending=False)
    for valc, cnt in ranked.head(10).items():
        examples_rows.append({
            "register": regc,
            "valency_class": valc,
            "total_count": int(round(cnt))
        })

examples = pd.DataFrame(examples_rows)
examples.to_csv(OUT_EX, sep="\t", index=False)
print(f"[S59(py)] Wrote example valency classes to: {OUT_EX}")

# --------------------------------------------------------------
# 2.6 Human-readable report
# --------------------------------------------------------------

with open(OUT_REP, "w", encoding="utf-8") as f:
    f.write("S59 – Register–valency tests (S42 Herbal_A vs Proc_B)\n")
    f.write("=====================================================\n\n")
    f.write(f"Input Herbal_A valency summary (S42): {A_FILE}\n")
    f.write(f"Input Proc_B valency summary (S42):   {B_FILE}\n\n")

    f.write("Contingency table: register × valency_class\n")
    f.write("(rows = register, columns = valency_class)\n\n")
    cont.to_csv(f, sep="\t")
    f.write("\n")

    f.write("Expected frequencies (same layout as contingency):\n\n")
    exp_df = pd.DataFrame(expected, index=cont.index, columns=cont.columns)
    exp_df.to_csv(f, sep="\t", float_format="%.3f")
    f.write("\n")

    f.write("Chi-square and association metrics:\n")
    f.write(f"  chi^2 = {chi2:.4f}\n")
    f.write(f"  df    = {df_chi}\n")
    f.write(f"  N     = {int(N)}\n")
    f.write(f"  Cramer's V = {cramer_v:.4f}\n\n")

    f.write("Permutation baseline (shuffling token-level register labels):\n")
    f.write(f"  iterations      = {len(v_null)}\n")
    f.write(f"  mean V_null     = {v_mean:.4f}\n")
    f.write(f"  sd V_null       = {v_std:.4f}\n")
    f.write(f"  95th pct V_null = {v_p95:.4f}\n\n")

    f.write("Interpretation hooks:\n")
    f.write("  * This test compares the valency-class distribution of stems/suffix\n")
    f.write("    in Herbal_A (REGISTER_A proxy) vs Proc_B (REGISTER_B proxy).\n")
    f.write("  * A strong Cramer's V that stands well above the permutation baseline\n")
    f.write("    supports the claim that the two registers deploy different valency\n")
    f.write("    profiles, not just different lexemes.\n")
    f.write("  * This complements S57 (stem–suffix bias) and S58 (valency proxies)\n")
    f.write("    by using the earlier S42 valency work in the new register framework.\n\n")

    f.write("Limitations:\n")
    f.write("  * Restricted to the Herbal_A and Proc_B subcorpora; Astronomical and\n")
    f.write("    low-density Herbal folios remain outside this test.\n")
    f.write("  * Valency classes are taken as given from S42; any uncertainty in\n")
    f.write("    S42 propagates here.\n")
    f.write("  * Token-level expansion for permutations assumes counts in S42 can be\n")
    f.write("    treated as independent instances.\n")

print(f"[S59(py)] Wrote report to: {OUT_REP}")
PYEOF

echo "[S59] Done."
