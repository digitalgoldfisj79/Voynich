#!/data/data/com.termux/files/usr/bin/sh
# S56 – Stem-level register divergence (shared stems only)
# Uses:
#   PhaseS/out/p6_folio_tokens.tsv
#   PhaseS/out/s50_folio_register_matrix.tsv
#   PhaseS/out/s46_stem_semantic_envelopes.tsv

set -eu

echo "[S56] Stem-level register divergence (shared stems only)"

BASE="$(pwd)"
OUTD="$BASE/PhaseS/out"

P6_TOKENS="$OUTD/p6_folio_tokens.tsv"
REG_MATRIX="$OUTD/s50_folio_register_matrix.tsv"
S46_ENVELOPES="$OUTD/s46_stem_semantic_envelopes.tsv"

OUT_PROFILES="$OUTD/s56_shared_stem_semantic_profiles.tsv"
OUT_SUMMARY="$OUTD/s56_shared_stem_semantic_summary.tsv"
OUT_REPORT="$OUTD/s56_stem_register_divergence_report.txt"

echo "[S56] BASE:        $BASE"
echo "[S56] OUTD:        $OUTD"
echo "[S56] P6 tokens:   $P6_TOKENS"
echo "[S56] Reg matrix:  $REG_MATRIX"
echo "[S56] S46 env:     $S46_ENVELOPES"

# basic existence checks
for f in "$P6_TOKENS" "$REG_MATRIX" "$S46_ENVELOPES"; do
  if [ ! -s "$f" ]; then
    echo "[S56] ERROR: missing or empty $f" >&2
    exit 1
  fi
done

python3 << EOF_PY
import pandas as pd
from pathlib import Path
from collections import Counter

p6_path = Path("$P6_TOKENS")
reg_path = Path("$REG_MATRIX")
s46_path = Path("$S46_ENVELOPES")

out_profiles = Path("$OUT_PROFILES")
out_summary = Path("$OUT_SUMMARY")
out_report = Path("$OUT_REPORT")

print(f"[S56] Loading tokens from: {p6_path}")
p6 = pd.read_csv(p6_path, sep="\\t")

print(f"[S56] Loading register matrix from: {reg_path}")
reg = pd.read_csv(reg_path, sep="\\t")

print(f"[S56] Loading semantic envelopes from: {s46_path}")
s46 = pd.read_csv(s46_path, sep="\\t")

# --- normalise folio ids in p6 to match s50 (strip '>' and anything after) ---
if "folio" not in p6.columns:
    raise ValueError("[S56] p6 file missing 'folio' column")

p6["folio_id"] = p6["folio"].astype(str).str.extract(r'^(f[0-9rv]+)')
# stem = full token string at this level
p6["stem"] = p6["token"].astype(str)

# register matrix already has folio ids like f1r
if "folio" not in reg.columns or "register" not in reg.columns:
    raise ValueError("[S56] register matrix missing 'folio' or 'register' columns")

reg_small = reg[["folio", "register"]].rename(columns={"folio": "folio_id"})

tokens_reg = p6.merge(reg_small, on="folio_id", how="inner")

if tokens_reg.empty:
    raise ValueError("[S56] No tokens after joining tokens with register matrix")

print(f"[S56] Tokens after join: {len(tokens_reg)}")

# prepare semantics for stems
if "token" in s46.columns and "semantic_family" in s46.columns:
    s46 = s46.rename(columns={"token": "stem"})
elif "stem" not in s46.columns or "semantic_family" not in s46.columns:
    raise ValueError("[S56] s46 file must have columns 'token' or 'stem' and 'semantic_family'")

stem_sem = s46[["stem", "semantic_family"]].copy()

tokens_reg = tokens_reg.merge(stem_sem, on="stem", how="left")

# classify semantic domain per token (PROC / BOT / BIO / OTHER/UNKNOWN)
def sem_domain(sf):
    if pd.isna(sf):
        return "UNKNOWN"
    if sf == "F_PROC_CORE":
        return "PROC"
    if sf == "F_BOTANICAL_CORE":
        return "BOT"
    if sf == "F_BIO_CORE":
        return "BIO"
    return "OTHER"

tokens_reg["sem_dom"] = tokens_reg["semantic_family"].map(sem_domain)

# --- aggregate per (stem, register) ---
grp = tokens_reg.groupby(["stem", "register"], as_index=False)

agg = grp.agg(
    total_tokens=("token", "size"),
    proc_tokens=("sem_dom", lambda x: (x == "PROC").sum()),
    bot_tokens=("sem_dom", lambda x: (x == "BOT").sum()),
    bio_tokens=("sem_dom", lambda x: (x == "BIO").sum()),
)

# fraction columns
for col in ["proc_tokens", "bot_tokens", "bio_tokens"]:
    agg[col + "_frac"] = agg[col] / agg["total_tokens"]

# stems with any A/B usage
mask_eval = agg["register"].isin(["REGISTER_A", "REGISTER_B"])
agg_eval = agg[mask_eval].copy()

stems_counts = agg_eval.groupby("stem")["register"].nunique()
shared_stems = stems_counts[stems_counts >= 2].index

print(f"[S56] Total stems with any A/B usage: {len(stems_counts)}")
print(f"[S56] Shared stems (A>0 & B>0):      {len(shared_stems)}")

shared = agg_eval[agg_eval["stem"].isin(shared_stems)].copy()

if shared.empty:
    raise ValueError("[S56] No shared stems with both REGISTER_A and REGISTER_B")

# pivot into A/B columns
pivot = shared.pivot(index="stem", columns="register", values="total_tokens").fillna(0)
pivot = pivot.rename(columns={"REGISTER_A": "n_A_tokens", "REGISTER_B": "n_B_tokens"})

# bring per-register semantic fractions across
frac_cols = ["proc_tokens_frac", "bot_tokens_frac", "bio_tokens_frac"]
for col in frac_cols:
    tmp = shared.pivot(index="stem", columns="register", values=col).fillna(0)
    tmp = tmp.rename(
        columns={
            "REGISTER_A": f"{col}_A",
            "REGISTER_B": f"{col}_B",
        }
    )
    pivot = pivot.join(tmp, how="left")

pivot = pivot.reset_index()

# add overall semantic_family from s46 (lexical semantics)
pivot = pivot.merge(
    stem_sem.drop_duplicates("stem"),
    on="stem",
    how="left"
)

# compute simple flags
pivot["total_tokens"] = pivot["n_A_tokens"] + pivot["n_B_tokens"]
pivot["A_dominant"] = pivot["n_A_tokens"] > pivot["n_B_tokens"]
pivot["B_dominant"] = pivot["n_B_tokens"] > pivot["n_A_tokens"]
pivot["balanced_AB"] = pivot["n_A_tokens"] == pivot["n_B_tokens"]

# semantic "difference" flags: do PROC/BOT/BIO fractions differ meaningfully?
def frac_diff_flag(row, base_col):
    a = row[f"{base_col}_A"]
    b = row[f"{base_col}_B"]
    if pd.isna(a) or pd.isna(b):
        return "UNKNOWN"
    diff = abs(a - b)
    if diff < 0.1:
        return "STABLE"
    if diff < 0.3:
        return "MILD_SHIFT"
    return "STRONG_SHIFT"

for base in ["proc_tokens_frac", "bot_tokens_frac", "bio_tokens_frac"]:
    pivot[f"{base}_shift"] = pivot.apply(frac_diff_flag, axis=1, base_col=base)

# write profiles
pivot_cols = [
    "stem",
    "semantic_family",
    "n_A_tokens",
    "n_B_tokens",
    "total_tokens",
    "A_dominant",
    "B_dominant",
    "balanced_AB",
    "proc_tokens_frac_A",
    "proc_tokens_frac_B",
    "proc_tokens_frac_shift",
    "bot_tokens_frac_A",
    "bot_tokens_frac_B",
    "bot_tokens_frac_shift",
    "bio_tokens_frac_A",
    "bio_tokens_frac_B",
    "bio_tokens_frac_shift",
]

pivot[pivot_cols].to_csv(out_profiles, sep="\\t", index=False)

# summary stats
n_shared = len(pivot)
n_A_dom = pivot["A_dominant"].sum()
n_B_dom = pivot["B_dominant"].sum()
n_bal = pivot["balanced_AB"].sum()

def count_shift(col, label):
    return (pivot[col] == label).sum()

summary_rows = [
    ("n_shared_stems", n_shared),
    ("n_A_dominant", n_A_dom),
    ("n_B_dominant", n_B_dom),
    ("n_balanced_AB", n_bal),
    ("proc_strong_shift", count_shift("proc_tokens_frac_shift", "STRONG_SHIFT")),
    ("proc_mild_shift",   count_shift("proc_tokens_frac_shift", "MILD_SHIFT")),
    ("proc_stable",       count_shift("proc_tokens_frac_shift", "STABLE")),
    ("bot_strong_shift",  count_shift("bot_tokens_frac_shift", "STRONG_SHIFT")),
    ("bot_mild_shift",    count_shift("bot_tokens_frac_shift", "MILD_SHIFT")),
    ("bot_stable",        count_shift("bot_tokens_frac_shift", "STABLE")),
    ("bio_strong_shift",  count_shift("bio_tokens_frac_shift", "STRONG_SHIFT")),
    ("bio_mild_shift",    count_shift("bio_tokens_frac_shift", "MILD_SHIFT")),
    ("bio_stable",        count_shift("bio_tokens_frac_shift", "STABLE")),
]

summary_df = pd.DataFrame(summary_rows, columns=["metric", "value"])
summary_df.to_csv(out_summary, sep="\\t", index=False)

with open(out_report, "w", encoding="utf-8") as f:
    f.write("S56 – Stem-level register divergence (shared stems only)\\n")
    f.write("=======================================================\\n\\n")
    f.write(f"Total stems with any REGISTER_A/REGISTER_B usage: {len(stems_counts)}\\n")
    f.write(f"Shared stems (used in both A and B):              {n_shared}\\n\\n")
    f.write("Dominance counts (shared stems only):\\n")
    f.write(f"  A_dominant:     {n_A_dom}\\n")
    f.write(f"  B_dominant:     {n_B_dom}\\n")
    f.write(f"  balanced_AB:    {n_bal}\\n\\n")

    def line(label, col):
        f.write(f"{label}:\\n")
        f.write(f"  STRONG_SHIFT: {count_shift(col, 'STRONG_SHIFT')}\\n")
        f.write(f"  MILD_SHIFT:   {count_shift(col, 'MILD_SHIFT')}\\n")
        f.write(f"  STABLE:       {count_shift(col, 'STABLE')}\\n")
        f.write(f"  UNKNOWN:      {(pivot[col] == 'UNKNOWN').sum()}\\n\\n")

    line("PROC fractions (per shared stem)", "proc_tokens_frac_shift")
    line("BOT fractions (per shared stem)", "bot_tokens_frac_shift")
    line("BIO fractions (per shared stem)", "bio_tokens_frac_shift")

print(f"[S56] Wrote shared-stem profiles to: {out_profiles}")
print(f"[S56] Wrote summary to:              {out_summary}")
print(f"[S56] Wrote report to:               {out_report}")

EOF_PY

