#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

LATIN_PATH="$BASE/corpora/latin_tokens_tac.txt"
OUT_TOKENS="$BASE/PhaseS/out/s6_tac_token_freq.tsv"
OUT_SUFFIX2="$BASE/PhaseS/out/s6_tac_suffix2_summary.tsv"
OUT_GLOBAL="$BASE/PhaseS/out/s6_tac_global_summary.tsv"

echo "[S6-TAC] BASE        = $BASE"
echo "[S6-TAC] LATIN_PATH  = $LATIN_PATH"
echo "[S6-TAC] OUT_TOKENS  = $OUT_TOKENS"
echo "[S6-TAC] OUT_SUFFIX2 = $OUT_SUFFIX2"
echo "[S6-TAC] OUT_GLOBAL  = $OUT_GLOBAL"

python3 "$BASE/scripts/s6_build_latin_structural_profiles.py" \
  "$LATIN_PATH" \
  "$OUT_TOKENS" \
  "$OUT_SUFFIX2" \
  "$OUT_GLOBAL"
