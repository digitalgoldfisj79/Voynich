#!/bin/sh
set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
PY="$BASE/scripts/s26_build_recurrent_templates.py"

if [ ! -f "$PY" ]; then
  echo "[FIX S26] ERROR: cannot find $PY" >&2
  exit 1
fi

tmp="$PY.tmp.$$"

echo "[FIX S26] Patching newline=\\\"§\\\" in:"
echo "         $PY"

# Remove the ', newline="§"' chunk from the open() call
sed 's/, *newline="§"//' "$PY" > "$tmp"

mv "$tmp" "$PY"

echo "[FIX S26] Done. Updated file:"
ls -l "$PY"
