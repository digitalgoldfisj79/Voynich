#!/usr/bin/env sh
set -eu

# S26: Recurrent template rung
# Extract all frames with count>=2 from s21_family_frames.tsv,
# assign template IDs, compute per-family coverage, and write
# TSV + human-readable summary.

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN_FRAMES="$BASE/PhaseS/out/s21_family_frames.tsv"
OUT_TSV="$BASE/PhaseS/out/s26_recurrent_templates.tsv"
OUT_TXT="$BASE/PhaseS/out/s26_recurrent_templates.txt"

echo "[S26] BASE      = $BASE"
echo "[S26] IN_FRAMES = $IN_FRAMES"
echo "[S26] OUT_TSV   = $OUT_TSV"
echo "[S26] OUT_TXT   = $OUT_TXT"

if [ ! -s "$IN_FRAMES" ]; then
  echo "[S26][ERR] Input frames file not found or empty: $IN_FRAMES" >&2
  exit 1
fi

mkdir -p "$BASE/PhaseS/out"

python3 "$BASE/scripts/s26_build_recurrent_templates.py" \
  --frames "$IN_FRAMES" \
  --out-tsv "$OUT_TSV" \
  --out-txt "$OUT_TXT"

echo "[S26] Done."
