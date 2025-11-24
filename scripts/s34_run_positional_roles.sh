#!/usr/bin/env sh
# S34 wrapper: build positional role profiles from slot bootstrap
# Uses PhaseS/out/s31_slot_bootstrap.tsv
# Writes:
#   PhaseS/out/s34_positional_roles.tsv
#   PhaseS/out/s34_positional_roles.txt

set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN_BOOT="${BASE}/PhaseS/out/s31_slot_bootstrap.tsv"
OUT_TSV="${BASE}/PhaseS/out/s34_positional_roles.tsv"
OUT_TXT="${BASE}/PhaseS/out/s34_positional_roles.txt"
PY_SCRIPT="${BASE}/scripts/s34_build_positional_roles.py"

if [ ! -f "$IN_BOOT" ]; then
  echo "[S34] ERROR: missing input: $IN_BOOT" >&2
  exit 1
fi

mkdir -p "${BASE}/PhaseS/out"
echo "[S34] BASE      = $BASE"
echo "[S34] IN_BOOT   = $IN_BOOT"
echo "[S34] OUT_TSV   = $OUT_TSV"
echo "[S34] OUT_TXT   = $OUT_TXT"
echo "[S34] PY_SCRIPT = $PY_SCRIPT"

python3 "$PY_SCRIPT" \
  --slots-bootstrap "$IN_BOOT" \
  --out-tsv "$OUT_TSV" \
  --out-txt "$OUT_TXT"

echo "[S34] Done. Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_TXT"
