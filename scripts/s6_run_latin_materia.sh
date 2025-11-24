#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
LATIN_PATH="${LATIN_PATH:-$BASE/corpora/latin_tokens_materia.txt}"

OUT_PREFIX="${OUT_PREFIX:-$BASE/PhaseS/out/s6_materia}"
OUT_TOKENS="${OUT_PREFIX}_token_freq.tsv"
OUT_SUFFIX2="${OUT_PREFIX}_suffix2_summary.tsv"
OUT_GLOBAL="${OUT_PREFIX}_global_summary.tsv"

echo "[S6-MAT] BASE        = $BASE"
echo "[S6-MAT] LATIN_PATH  = $LATIN_PATH"
echo "[S6-MAT] OUT_TOKENS  = $OUT_TOKENS"
echo "[S6-MAT] OUT_SUFFIX2 = $OUT_SUFFIX2"
echo "[S6-MAT] OUT_GLOBAL  = $OUT_GLOBAL"

python3 "$BASE/scripts/s6_build_latin_structural_profiles.py" \
  "$LATIN_PATH" "$OUT_TOKENS" "$OUT_SUFFIX2" "$OUT_GLOBAL"
