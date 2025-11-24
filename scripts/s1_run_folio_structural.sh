#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

TOK_PATH="${TOK_PATH:-$BASE/p6_folio_tokens.tsv}"
TYPES_PATH="${TYPES_PATH:-$BASE/Phase71/out/p71_vm_structural_vectors.tsv}"
SECTION_PATH="${SECTION_PATH:-$BASE/metadata/folios_sections.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s1_folio_structural_vectors.tsv}"

mkdir -p "$BASE/PhaseS/out"

echo "[S1] BASE          = $BASE"
echo "[S1] TOK_PATH      = $TOK_PATH"
echo "[S1] TYPES_PATH    = $TYPES_PATH"
echo "[S1] SECTION_PATH  = $SECTION_PATH"
echo "[S1] OUT_PATH      = $OUT_PATH"

python3 "$BASE/scripts/s1_build_folio_structural_vectors.py"
