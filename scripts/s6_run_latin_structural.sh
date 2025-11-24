#!/usr/bin/env sh
set -eu

# Base directory for the Voynich Reproducible Core
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

LATIN_PATH="${LATIN_PATH:-$BASE/corpora/latin_tokens.txt}"
OUTDIR="${OUTDIR:-$BASE/PhaseS/out}"

mkdir -p "$OUTDIR"

OUT_TOKENS="$OUTDIR/s6_latin_token_freq.tsv"
OUT_SUFFIX2="$OUTDIR/s6_latin_suffix2_summary.tsv"
OUT_GLOBAL="$OUTDIR/s6_latin_global_summary.tsv"

echo "[S6] BASE        = $BASE"
echo "[S6] LATIN_PATH  = $LATIN_PATH"
echo "[S6] OUT_TOKENS  = $OUT_TOKENS"
echo "[S6] OUT_SUFFIX2 = $OUT_SUFFIX2"
echo "[S6] OUT_GLOBAL  = $OUT_GLOBAL"

python3 "$BASE/scripts/s6_build_latin_structural_profiles.py" \
    "$LATIN_PATH" \
    "$OUT_TOKENS" \
    "$OUT_SUFFIX2" \
    "$OUT_GLOBAL"
