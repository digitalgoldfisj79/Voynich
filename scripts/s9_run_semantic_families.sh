#!/usr/bin/env sh
set -eu

# Base project dir; can be overridden from env
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

IN_PATH="${IN_PATH:-$BASE/PhaseS/out/s8_stem_semantic_candidates.tsv}"
OUT_PATH="${OUT_PATH:-$BASE/PhaseS/out/s9_stem_semantic_families.tsv}"

echo "[S9] BASE      = $BASE"
echo "[S9] IN_PATH   = $IN_PATH"
echo "[S9] OUT_PATH  = $OUT_PATH"

if [ ! -f "$IN_PATH" ]; then
  echo "[S9][ERROR] Input file not found: $IN_PATH" >&2
  exit 1
fi

python3 "$BASE/scripts/s9_build_semantic_families.py" "$IN_PATH" "$OUT_PATH"
echo "[S9] Done."
