#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

DANTE_SUFFIX="${DANTE_SUFFIX:-$BASE/PhaseS/out/s6_latin_suffix2_summary.tsv}"
TAC_SUFFIX="${TAC_SUFFIX:-$BASE/PhaseS/out/s6_tac_suffix2_summary.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s6_dante_vs_tac_suffix2.tsv}"

echo "[S6-CT] BASE         = $BASE"
echo "[S6-CT] DANTE_SUFFIX = $DANTE_SUFFIX"
echo "[S6-CT] TAC_SUFFIX   = $TAC_SUFFIX"
echo "[S6-CT] OUT_PATH     = $OUT_PATH"

python3 "$BASE/scripts/s6_compare_dante_tac_suffix2.py" \
  "$DANTE_SUFFIX" \
  "$TAC_SUFFIX" \
  "$OUT_PATH"
