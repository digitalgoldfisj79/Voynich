#!/usr/bin/env sh
# Corrected: uses the proper absolute base path.

set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
export BASE

IN_DIR="$BASE/Phase70/in"
OUT_DIR="$BASE/Phase70/out"

mkdir -p "$IN_DIR" "$OUT_DIR"

if [ ! -s "$IN_DIR/p70_prefixes.txt" ] || [ ! -s "$IN_DIR/p70_suffixes.txt" ]; then
  echo "[WARN] Missing prefix or suffix file in:"
  echo "       $IN_DIR/p70_prefixes.txt"
  echo "       $IN_DIR/p70_suffixes.txt"
fi

python3 "$BASE/scripts/p71_segment_schemeC.py"

echo "[OK] Scheme C segmentation completed."
