#!/usr/bin/env sh
# S54 – Second batch of semantic tests
# Stable version with fixed directory paths

set -eu

# ***** FIXED BASE DIRECTORY *****
BASE="$HOME/Voynich/Voynich_Reproducible_Core"
export BASE
# ********************************

OUTD="$BASE/PhaseS/out"

S46="$OUTD/s46_stem_semantic_envelopes.tsv"
S51="$OUTD/s51_hand_semantic_profiles.tsv"

OUT_SECTION_PROFILES="$OUTD/s54_section_semantic_profiles.tsv"
OUT_SECTION_CONTING="$OUTD/s54_section_semantic_contingency.tsv"
OUT_HAND_COPY="$OUTD/s54_hand_semantic_profiles_copy.tsv"
OUT_EXPECTED="$OUTD/s54_section_expected_frequencies.tsv"
OUT_REPORT="$OUTD/s54_semantic_batch2_report.txt"

echo "[S54] Second batch of semantic tests"
echo "[S54] BASE:  $BASE"
echo "[S54] OUTD:  $OUTD"
echo "[S54] S46:   $S46"
echo "[S54] S51:   $S51"

missing=0
for f in "$S46" "$S51"; do
  if [ ! -s "$f" ]; then
    echo "[S54] ERROR: missing or empty input: $f" >&2
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "[S54] Aborting."
  exit 1
fi

python3 << 'PY'
import pandas as pd
import numpy as np
import math
import os
from pathlib import Path

BASE = Path(os.environ["BASE"])
OUTD = BASE / "PhaseS" / "out"

S46 = OUTD / "s46_stem_semantic_envelopes.tsv"
S51 = OUTD / "s51_hand_semantic_profiles.tsv"

OUT_SECTION_PROFILES   = OUTD / "s54_section_semantic_profiles.tsv"
OUT_SECTION_CONTING    = OUTD / "s54_section_semantic_contingency.tsv"
OUT_HAND_COPY          = OUTD / "s54_hand_semantic_profiles_copy.tsv"
OUT_EXPECTED           = OUTD / "s54_section_expected_frequencies.tsv"
OUT_REPORT             = OUTD / "s54_semantic_batch2_report.txt"

print("[S54] Loading S46…")
s46 = pd.read_csv(S46, sep="\t")

req = ["primary_section","semantic_family","role_group","bot_share","bio_share","proc_share"]
missing = [c for c in req if c not in s46.columns]
if missing:
    raise SystemExit(f"[S54] ERROR: S46 missing columns: {missing}")

s46["primary_section"] = s46["primary_section"].fillna("Unknown")
s46["role_group"] = s46["role_group"].fillna("UNKNOWN")

for col in ["bot_share","bio_share","proc_share"]:
    s46[col] = s46[col].fillna(0.0)

# ---- Section semantic profiles ----
grouped = (
    s46.groupby("primary_section")[["bot_share","bio_share","proc_share"]]
    .mean()
    .reset_index()
    .rename(columns={
        "primary_section":"section",
        "bot_share":"mean_bot_share",
        "bio_share":"mean_bio_share",
        "proc_share":"mean_proc_share"
    })
)
grouped.to_csv(OUT_SECTION_PROFILES, sep="\t", index=False)
print(f"[S54] Wrote section semantic profiles → {OUT_SECTION_PROFILES}")

# ---- Contingency table ----
def coarse(r):
    r=str(r).upper()
    if r.startswith("BOT"): return "BOT"
    if r.startswith("BIO"): return "BIO"
    if r.startswith("PROC"): return "PROC"
    return "OTHER"

s46["coarse_role_group"]=s46["role_group"].apply(coarse)
cont = pd.crosstab(s46["primary_section"], s46["coarse_role_group"])
cont.reset_index().rename(columns={"primary_section":"section"}).to_csv(
    OUT_SECTION_CONTING, sep="\t", index=False
)
print(f"[S54] Wrote contingency table → {OUT_SECTION_CONTING}")

# ---- Expected frequencies / Chi-square / Cramer's V ----
obs = cont.to_numpy().astype(float)
N = obs.sum()
rows, cols = obs.shape

if N == 0 or rows < 2 or cols < 2:
    chi2 = float("nan")
    cramer_v = float("nan")
    expected = np.zeros_like(obs)
else:
    row_sums = obs.sum(axis=1,keepdims=True)
    col_sums = obs.sum(axis=0,keepdims=True)
    expected = row_sums @ col_sums / N

    with np.errstate(divide="ignore", invalid="ignore"):
        chi2_matrix = (obs - expected)**2 / expected
        chi2_matrix[np.isnan(chi2_matrix)] = 0.0
    chi2 = chi2_matrix.sum()
    cramer_v = math.sqrt( chi2 / (N*min(rows-1,cols-1)) )

exp_df = pd.DataFrame(expected, index=cont.index, columns=cont.columns)
exp_df.reset_index().rename(columns={"primary_section":"section"}).to_csv(
    OUT_EXPECTED, sep="\t", index=False
)
print(f"[S54] Wrote expected frequencies → {OUT_EXPECTED}")

print("[S54] Loading S51…")
s51 = pd.read_csv(S51, sep="\t")
s51.to_csv(OUT_HAND_COPY, sep="\t", index=False)
print(f"[S54] Wrote hand semantic profiles → {OUT_HAND_COPY}")

# ---- Write narrative report ----
with open(OUT_REPORT,"w") as f:
    f.write("S54 – Second batch of semantic tests\n")
    f.write("==================================\n\n")
    f.write("Section-level semantic profiles:\n")
    f.write(grouped.to_csv(sep="\t", index=False))
    f.write("\nContingency Table:\n")
    f.write(cont.to_csv(sep="\t"))
    f.write(f"\nChi-square = {chi2:.4f}\n")
    f.write(f"Cramer's V = {cramer_v:.4f}\n")

print(f"[S54] Report written → {OUT_REPORT}")
PY

echo "[S54] Done."
