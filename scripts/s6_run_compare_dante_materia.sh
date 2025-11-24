#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

DANTE_SUFFIX="${DANTE_SUFFIX:-$BASE/PhaseS/out/s6_latin_suffix2_summary.tsv}"
MATERIA_SUFFIX="${MATERIA_SUFFIX:-$BASE/PhaseS/out/s6_materia_suffix2_summary.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s6_dante_vs_materia_suffix2.tsv}"

echo "[S6-DM] BASE           = $BASE"
echo "[S6-DM] DANTE_SUFFIX   = $DANTE_SUFFIX"
echo "[S6-DM] MATERIA_SUFFIX = $MATERIA_SUFFIX"
echo "[S6-DM] OUT_PATH       = $OUT_PATH"

python3 "$BASE/scripts/s6_compare_suffix2_generic.py" \
  "$DANTE_SUFFIX" "$MATERIA_SUFFIX" "$OUT_PATH" "Dante" "Materia"
