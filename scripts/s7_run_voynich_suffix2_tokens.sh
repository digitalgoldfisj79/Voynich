#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

TOK_PATH="${TOK_PATH:-$BASE/corpora/p6_voynich_tokens.txt}"
OUT_TOKENS="${OUT_TOKENS:-$BASE/PhaseS/out/s7_voynich_token_suffix2.tsv}"
OUT_SUMMARY="${OUT_SUMMARY:-$BASE/PhaseS/out/s7_voynich_suffix2_tokens_summary.tsv}"

echo "[S7a] BASE        = $BASE"
echo "[S7a] TOK_PATH    = $TOK_PATH"
echo "[S7a] OUT_TOKENS  = $OUT_TOKENS"
echo "[S7a] OUT_SUMMARY = $OUT_SUMMARY"

python3 "$BASE/scripts/s7_build_voynich_suffix2_tokens.py"
