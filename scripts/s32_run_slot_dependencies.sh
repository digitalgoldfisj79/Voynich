#!/usr/bin/env sh
# S32: cross-position dependencies P(R | L,C) from frame triples

set -eu

BASE="${BASE:-$(pwd)}"

FRAMES_PATH="$BASE/PhaseS/out/s21_family_frames.tsv"
OUT_TSV="$BASE/PhaseS/out/s32_slot_dependencies.tsv"
OUT_TXT="$BASE/PhaseS/out/s32_slot_dependencies.txt"

echo "[S32] BASE        = $BASE"
echo "[S32] FRAMES_PATH = $FRAMES_PATH"
echo "[S32] OUT_TSV     = $OUT_TSV"
echo "[S32] OUT_TXT     = $OUT_TXT"

python3 "$BASE/scripts/s32_build_slot_dependencies.py" \
  --frames "$FRAMES_PATH" \
  --out-tsv "$OUT_TSV" \
  --out-txt "$OUT_TXT"
