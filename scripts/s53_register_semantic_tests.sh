#!/bin/sh
set -eu

# S53: Register–semantic cross-validation
# Uses:
#   PhaseS/out/s50_folio_register_matrix.tsv
#
# Outputs:
#   PhaseS/out/s53_register_semantic_summary.tsv
#   PhaseS/out/s53_register_semantic_tests.txt

# Resolve repo root as "directory above scripts/"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTD="$REPO/PhaseS/out"

REG_MATRIX="$OUTD/s50_folio_register_matrix.tsv"
OUT_SUMMARY="$OUTD/s53_register_semantic_summary.tsv"
OUT_REPORT="$OUTD/s53_register_semantic_tests.txt"

echo "[S53] Register–semantic cross-validation"
echo "[S53] REPO:       $REPO"
echo "[S53] REG_MATRIX: $REG_MATRIX"
echo "[S53] OUT_SUMMARY: $OUT_SUMMARY"
echo "[S53] OUT_REPORT:  $OUT_REPORT"

if [ ! -s "$REG_MATRIX" ]; then
  echo "[S53] ERROR: missing or empty $REG_MATRIX" >&2
  exit 1
fi

REG_MATRIX="$REG_MATRIX" OUT_SUMMARY="$OUT_SUMMARY" OUT_REPORT="$OUT_REPORT" python3 - << 'PY'
import pandas as pd
import math
import numpy as np
import os
from pathlib import Path

reg_matrix = Path(os.environ["REG_MATRIX"])
out_summary = Path(os.environ["OUT_SUMMARY"])
out_report = Path(os.environ["OUT_REPORT"])

df = pd.read_csv(reg_matrix, sep="\t")

required = [
    "folio",
    "known_semantic_tokens",
    "proc_frac",
    "bot_frac",
    "bio_frac",
    "dominant_semantic_register",
    "section",
    "currier",
    "register",
]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"[S53] Missing columns in s50_folio_register_matrix.tsv: {missing}")

# Only REGISTER_A / REGISTER_B with some semantics
mask = df["register"].isin(["REGISTER_A", "REGISTER_B"]) & (df["known_semantic_tokens"] > 0)
sub = df.loc[mask].copy()

if sub.empty:
    raise ValueError("[S53] No folios with REGISTER_A/REGISTER_B and known_semantic_tokens > 0")

# ---- 1. Per-register mean fractions ----
grouped = (
    sub
    .groupby("register", dropna=False)
    .agg(
        n_folios=("folio", "nunique"),
        mean_proc_frac=("proc_frac", "mean"),
        mean_bot_frac=("bot_frac", "mean"),
        mean_bio_frac=("bio_frac", "mean"),
    )
    .reset_index()
)

# ---- 2. Contingency: register x dominant_semantic_register ----
cont = pd.crosstab(sub["register"], sub["dominant_semantic_register"])
obs = cont.values.astype(float)
total = obs.sum()

if total == 0:
    chi2 = float("nan")
    df_chi = 0
    cramer_v = float("nan")
else:
    row_sums = obs.sum(axis=1, keepdims=True)
    col_sums = obs.sum(axis=0, keepdims=True)
    expected = row_sums * col_sums / total
    with np.errstate(divide="ignore", invalid="ignore"):
        chi2 = np.nansum((obs - expected) ** 2 / expected)
    df_chi = (obs.shape[0] - 1) * (obs.shape[1] - 1)
    k = min(obs.shape)
    if k > 1:
        cramer_v = math.sqrt(chi2 / (total * (k - 1)))
    else:
        cramer_v = float("nan")

def frac(condition):
    sel = sub.loc[condition]
    return len(sel), (len(sel) / len(sub)) if len(sub) > 0 else 0.0

n_a_bot, frac_a_bot = frac(
    (sub["register"] == "REGISTER_A") & (sub["dominant_semantic_register"] == "BOT_DOM")
)
n_b_proc, frac_b_proc = frac(
    (sub["register"] == "REGISTER_B") & (sub["dominant_semantic_register"] == "PROC_DOM")
)
n_a_proc, frac_a_proc = frac(
    (sub["register"] == "REGISTER_A") & (sub["dominant_semantic_register"] == "PROC_DOM")
)
n_b_bot, frac_b_bot = frac(
    (sub["register"] == "REGISTER_B") & (sub["dominant_semantic_register"] == "BOT_DOM")
)

# ---- Write summary TSV ----
out_summary.parent.mkdir(parents=True, exist_ok=True)
grouped.to_csv(out_summary, sep="\t", index=False)

# ---- Write human-readable report ----
with open(out_report, "w", encoding="utf-8") as f:
    f.write("[S53] Register–semantic cross-validation\n")
    f.write(f"[S53] Input:  {reg_matrix}\n")
    f.write(f"[S53] Output: {out_summary}\n\n")

    f.write("Per-register mean semantic fractions (folios with REGISTER_A/REGISTER_B only):\n")
    f.write("register\tn_folios\tmean_proc_frac\tmean_bot_frac\tmean_bio_frac\n")
    for _, row in grouped.iterrows():
        f.write(
            f"{row['register']}\t{int(row['n_folios'])}\t"
            f"{row['mean_proc_frac']:.4f}\t"
            f"{row['mean_bot_frac']:.4f}\t"
            f"{row['mean_bio_frac']:.4f}\n"
        )
    f.write("\n")

    f.write("Contingency table: register x dominant_semantic_register\n")
    f.write(cont.to_string())
    f.write("\n\n")

    f.write("Chi-square test of independence (register vs dominant_semantic_register):\n")
    f.write(f"  chi^2 = {chi2:.4f}\n")
    f.write(f"  df    = {df_chi}\n")
    f.write(f"  N     = {int(total)}\n")
    f.write(f"  Cramer's V = {cramer_v:.4f}\n")
    f.write("\n")

    f.write("Alignment metrics:\n")
    f.write(
        f"  REGISTER_A & BOT_DOM:  n={n_a_bot}, "
        f"fraction of all register-evaluable folios={frac_a_bot:.3f}\n"
    )
    f.write(
        f"  REGISTER_B & PROC_DOM: n={n_b_proc}, "
        f"fraction of all register-evaluable folios={frac_b_proc:.3f}\n"
    )
    f.write(
        f"  REGISTER_A & PROC_DOM: n={n_a_proc}, "
        f"fraction of all register-evaluable folios={frac_a_proc:.3f}\n"
    )
    f.write(
        f"  REGISTER_B & BOT_DOM:  n={n_b_bot}, "
        f"fraction of all register-evaluable folios={frac_b_bot:.3f}\n"
    )
    f.write("\n")

    f.write("Notes:\n")
    f.write("  * Uses folio-level semantic fractions from S50.\n")
    f.write("  * Only folios with REGISTER_A/REGISTER_B and known_semantic_tokens>0 are included.\n")
    f.write("  * 'dominant_semantic_register' is taken from S49c/S50 (BOT_DOM, PROC_DOM, etc.).\n")

print("[S53] Wrote:", out_summary)
print("[S53] Wrote:", out_report)
PY

echo "[S53] Done."
