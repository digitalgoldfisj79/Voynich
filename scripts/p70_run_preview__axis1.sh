#!/usr/bin/env sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
export BASE

OUT_DIR="$BASE/Phase70/out"
mkdir -p "$OUT_DIR"

python3 "$BASE/scripts/p70_preview_axis1.py"

echo "[OK] p70 axis1 preview completed."
