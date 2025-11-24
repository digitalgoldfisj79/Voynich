#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

STRUCT_PATH="${STRUCT_PATH:-$BASE/PhaseS/out/s4_stem_structural_vectors.tsv}"
DIST_PATH="${DIST_PATH:-$BASE/PhaseS/out/s4_stem_section_distribution.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s5_vm_semantic_profiles.tsv}"

echo "[S5] BASE         = $BASE"
echo "[S5] STRUCT_PATH  = $STRUCT_PATH"
echo "[S5] DIST_PATH    = $DIST_PATH"
echo "[S5] OUT_PATH     = $OUT_PATH"

python3 "$BASE/scripts/s5_build_vm_semantic_profiles.py" \
  "$STRUCT_PATH" \
  "$DIST_PATH" \
  "$OUT_PATH"
