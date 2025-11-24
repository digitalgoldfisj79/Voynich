#!/usr/bin/env sh
set -eu

# Allow BASE override but default sensibly
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

SLOTS_PATH="$BASE/PhaseS/out/s29_slot_profiles.tsv"
OUT_PATH="$BASE/PhaseS/out/s29_slot_profiles_with_suffix.tsv"
PY_SCRIPT="$BASE/scripts/s29_add_slot_suffixes.py"

echo "[S29_SUFFIX] BASE       = $BASE"
echo "[S29_SUFFIX] SLOTS_PATH = $SLOTS_PATH"
echo "[S29_SUFFIX] OUT_PATH   = $OUT_PATH"
echo "[S29_SUFFIX] PY_SCRIPT  = $PY_SCRIPT"

if [ ! -f "$SLOTS_PATH" ]; then
  echo "[s29_suffix] ERROR: slots file not found: $SLOTS_PATH" >&2
  exit 1
fi

python3 "$PY_SCRIPT" "$SLOTS_PATH" "$OUT_PATH"
echo "[S29_SUFFIX] Done. Wrote: $OUT_PATH"
