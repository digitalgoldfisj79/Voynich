#!/usr/bin/env sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
export BASE

OUT_DIR="$BASE/Phase72/out"
mkdir -p "$OUT_DIR"

python3 "$BASE/scripts/p72_vm_semantic_fields.py"

echo "[OK] p72 VM semantic fields (clusters) completed."
