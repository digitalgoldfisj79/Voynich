#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

MATERIA="${MATERIA:-$BASE/PhaseS/out/s6_materia_suffix2_summary.tsv}"
DANTE="${DANTE:-$BASE/PhaseS/out/s6_latin_suffix2_summary.tsv}"
VM_STEMS="${VM_STEMS:-$BASE/PhaseS/out/s7_voynich_suffix2_stems_summary.tsv}"
OUT="${OUT:-$BASE/PhaseS/out/s6_materia_dante_voynich_suffix2.tsv}"

echo "[S6-MDV] BASE      = $BASE"
echo "[S6-MDV] MATERIA   = $MATERIA"
echo "[S6-MDV] DANTE     = $DANTE"
echo "[S6-MDV] VM_STEMS  = $VM_STEMS"
echo "[S6-MDV] OUT       = $OUT"

python3 "$BASE/scripts/s6_compare_materia_dante_voynich.py" \
  "$MATERIA" \
  "$DANTE" \
  "$VM_STEMS" \
  "$OUT"
