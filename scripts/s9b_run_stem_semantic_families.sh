#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

IN_PATH="${IN_PATH:-$BASE/PhaseS/out/s8_stem_semantic_candidates.tsv}"
MV_TABLE="${MV_TABLE:-$BASE/PhaseS/out/s6_materia_dante_voynich_suffix2.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s9b_stem_semantic_families.tsv}"

echo "[S9b] BASE       = $BASE"
echo "[S9b] IN_PATH    = $IN_PATH"
echo "[S9b] MV_TABLE   = $MV_TABLE"
echo "[S9b] OUT_PATH   = $OUT_PATH"

python3 "$BASE/scripts/s9b_build_stem_semantic_families.py" \
  "$IN_PATH" \
  "$MV_TABLE" \
  "$OUT_PATH"
