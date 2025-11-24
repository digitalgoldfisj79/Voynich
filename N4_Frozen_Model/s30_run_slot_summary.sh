#!/usr/bin/env sh
set -eu

# S30 – Summarise slot profiles by family/position

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseS/out"
SCRIPTD="$BASE/scripts"

IN_SLOTS="$OUTD/s29_slot_profiles.tsv"
OUT_TSV="$OUTD/s30_slot_summary.tsv"
OUT_TXT="$OUTD/s30_slot_summary.txt"

echo "[S30] BASE      = $BASE"
echo "[S30] OUTD      = $OUTD"
echo "[S30] IN_SLOTS  = $IN_SLOTS"
echo "[S30] OUT_TSV   = $OUT_TSV"
echo "[S30] OUT_TXT   = $OUT_TXT"

if [ ! -f "$IN_SLOTS" ]; then
  echo "[S30][ERR] Missing input: $IN_SLOTS" >&2
  exit 1
fi

if [ ! -d "$SCRIPTD" ]; then
  echo "[S30][ERR] Scripts directory not found: $SCRIPTD" >&2
  exit 1
fi

python3 "$SCRIPTD/s30_summarise_slot_profiles.py" \
  --slots "$IN_SLOTS" \
  --out-tsv "$OUT_TSV" \
  --out-txt "$OUT_TXT"

echo "[S30] Done."
