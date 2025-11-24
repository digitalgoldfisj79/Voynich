#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

SLOTS_PATH="$BASE/PhaseS/out/s29_slot_profiles_with_suffix.tsv"
CORE_PATH="$BASE/PhaseS/out/s13_semantic_core_report.tsv"  # kept for CLI, ignored in code
OUT_TSV="$BASE/PhaseS/out/s33_slot_morphology.tsv"
OUT_SUMMARY="$BASE/PhaseS/out/s33_slot_morph_summary.tsv"
OUT_TXT="$BASE/PhaseS/out/s33_slot_morphology.txt"
PY_SCRIPT="$BASE/scripts/s33_build_slot_morphology.py"

echo "[S33] BASE        = $BASE"
echo "[S33] SLOTS_PATH  = $SLOTS_PATH"
echo "[S33] CORE_PATH   = $CORE_PATH (ignored)"
echo "[S33] OUT_TSV     = $OUT_TSV"
echo "[S33] OUT_SUMMARY = $OUT_SUMMARY"
echo "[S33] OUT_TXT     = $OUT_TXT"

if [ ! -f "$SLOTS_PATH" ]; then
  echo "[S33] ERROR: slots file not found: $SLOTS_PATH" >&2
  exit 1
fi

python3 "$PY_SCRIPT" \
  --slots "$SLOTS_PATH" \
  --core "$CORE_PATH" \
  --out-tsv "$OUT_TSV" \
  --out-summary-tsv "$OUT_SUMMARY" \
  --out-txt "$OUT_TXT"

echo "[S33] Done. Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_SUMMARY"
echo "  - $OUT_TXT"
