#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

STEM_PATH="${STEM_PATH:-$BASE/PhaseS/out/s5_stem_structural_summary.tsv}"
OUT_STEMS="${OUT_STEMS:-$BASE/PhaseS/out/s7_voynich_stem_suffix2.tsv}"
OUT_SUMMARY="${OUT_SUMMARY:-$BASE/PhaseS/out/s7_voynich_suffix2_stems_summary.tsv}"

echo "[S7b] BASE        = $BASE"
echo "[S7b] STEM_PATH   = $STEM_PATH"
echo "[S7b] OUT_STEMS   = $OUT_STEMS"
echo "[S7b] OUT_SUMMARY = $OUT_SUMMARY"

python3 "$BASE/scripts/s7_build_voynich_suffix2_stems.py"
