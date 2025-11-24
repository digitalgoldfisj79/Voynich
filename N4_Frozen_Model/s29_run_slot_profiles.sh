#!/usr/bin/env sh
set -eu

# S29 – Slot profiles for core stems across template positions

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseS/out"
SCRIPTD="$BASE/scripts"

IN_TEMPLATES="$OUTD/s26_recurrent_templates.tsv"
OUT_TSV="$OUTD/s29_slot_profiles.tsv"
OUT_TXT="$OUTD/s29_slot_profiles.txt"

echo "[S29] BASE        = $BASE"
echo "[S29] OUTD        = $OUTD"
echo "[S29] IN_TEMPLATES= $IN_TEMPLATES"
echo "[S29] OUT_TSV     = $OUT_TSV"
echo "[S29] OUT_TXT     = $OUT_TXT"

# Basic checks
if [ ! -f "$IN_TEMPLATES" ]; then
  echo "[S29][ERR] Missing input: $IN_TEMPLATES" >&2
  exit 1
fi

# Ensure scripts dir exists
if [ ! -d "$SCRIPTD" ]; then
  echo "[S29][ERR] Scripts directory not found: $SCRIPTD" >&2
  exit 1
fi

python3 "$SCRIPTD/s29_build_slot_profiles.py" \
  --templates "$IN_TEMPLATES" \
  --out-tsv "$OUT_TSV" \
  --out-txt "$OUT_TXT"

echo "[S29] Done."
