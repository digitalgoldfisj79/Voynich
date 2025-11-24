#!/usr/bin/env bash
set -euo pipefail

# Simple, Termux-safe runner for the S27 null-model rung
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN_STATS="$BASE/PhaseS/out/s23_frame_stats.tsv"
OUT_TSV="$BASE/PhaseS/out/s27_template_null.tsv"
OUT_TXT="$BASE/PhaseS/out/s27_template_null.txt"
PY_SCRIPT="$BASE/scripts/s27_build_template_null.py"

echo "[S27] BASE      = $BASE"
echo "[S27] IN_STATS  = $IN_STATS"
echo "[S27] OUT_TSV   = $OUT_TSV"
echo "[S27] OUT_TXT   = $OUT_TXT"

if [ ! -f "$IN_STATS" ]; then
  echo "[S27][ERR] Stats file not found: $IN_STATS" >&2
  exit 1
fi

if [ ! -f "$PY_SCRIPT" ]; then
  echo "[S27][ERR] Python script not found: $PY_SCRIPT" >&2
  exit 1
fi

python3 "$PY_SCRIPT" "$IN_STATS" "$OUT_TSV" "$OUT_TXT"

echo "[S27] Done."
