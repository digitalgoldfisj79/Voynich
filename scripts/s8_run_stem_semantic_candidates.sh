#!/usr/bin/env sh
set -eu

# Base repo path
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

IN_STRUCT="${IN_STRUCT:-$BASE/PhaseS/out/s4_stem_structural_vectors.tsv}"
IN_SECT_DIST="${IN_SECT_DIST:-$BASE/PhaseS/out/s4_stem_section_distribution.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s8_stem_semantic_candidates.tsv}"

echo "[S8] BASE         = $BASE"
echo "[S8] IN_STRUCT    = $IN_STRUCT"
echo "[S8] IN_SECT_DIST = $IN_SECT_DIST"
echo "[S8] OUT_PATH     = $OUT_PATH"

python3 "$BASE/scripts/s8_build_stem_semantic_candidates.py" \
  "$IN_STRUCT" "$IN_SECT_DIST" "$OUT_PATH"
