#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

TYPES_PATH="$BASE/Phase71/out/p71_vm_structural_vectors.tsv"
TOK_PATH="$BASE/PhaseS/out/p6_folio_tokens.tsv"
FOLIO_SECT_PATH="$BASE/metadata/folio_sections.tsv"
SECT_SUMMARY="$BASE/PhaseS/out/s2_section_structural_summary.tsv"
OUT_PREFIX="$BASE/PhaseS/out/s4"

echo "[S4] BASE           = $BASE"
echo "[S4] TYPES_PATH     = $TYPES_PATH"
echo "[S4] TOK_PATH       = $TOK_PATH"
echo "[S4] FOLIO_SECTIONS = $FOLIO_SECT_PATH"
echo "[S4] SECT_SUMMARY   = $SECT_SUMMARY"
echo "[S4] OUT_PREFIX     = $OUT_PREFIX"

python3 "$BASE/scripts/s4_build_stem_structural_vectors.py" \
  "$TYPES_PATH" "$TOK_PATH" "$FOLIO_SECT_PATH" "$SECT_SUMMARY" "$OUT_PREFIX"
