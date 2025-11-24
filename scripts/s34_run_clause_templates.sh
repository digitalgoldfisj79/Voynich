#!/bin/sh
set -eu

echo "[S34] BASE=$BASE"

IN_FRAMES="$BASE/PhaseS/out/s26_recurrent_templates.tsv"
OUT_TSV="$BASE/PhaseS/out/s34_clause_templates.tsv"
OUT_TXT="$BASE/PhaseS/out/s34_clause_templates.txt"
PY_SCRIPT="$BASE/scripts/s34_build_clause_templates.py"

if [ ! -f "$IN_FRAMES" ]; then
    echo "[S34] ERROR: missing $IN_FRAMES"
    exit 1
fi

mkdir -p "$BASE/PhaseS/out"

python3 "$PY_SCRIPT" \
    --frames "$IN_FRAMES" \
    --out-tsv "$OUT_TSV" \
    --out-txt "$OUT_TXT"

echo "[S34] Done. Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_TXT"
