#!/usr/bin/env sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
export BASE

OUT_DIR="$BASE/Phase71/out"
mkdir -p "$OUT_DIR"

python3 "$BASE/scripts/p71_vm_structural_vectors.py"

echo "[OK] p71 VM structural vectors completed."
