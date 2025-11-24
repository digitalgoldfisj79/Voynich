#!/usr/bin/env bash
set -euo pipefail

: "${BASE:="$HOME/Voynich/Voynich_Reproducible_Core"}"

SLOTS="$BASE/PhaseS/out/s29_slot_profiles_with_suffix.tsv"
CATALOG="$BASE/PhaseS/out/s36_clause_role_catalogue.tsv"

OUT_PAIRS="$BASE/PhaseS/out/s37_agent_patient_pairs.tsv"
OUT_SUFFIX="$BASE/PhaseS/out/s37_agent_patient_suffix_pairs.tsv"
OUT_TXT="$BASE/PhaseS/out/s37_agent_patient_summary.txt"

PY="$BASE/scripts/s37_build_agent_patient_pairs.py"

echo "[S37] BASE        = $BASE"
echo "[S37] SLOTS       = $SLOTS"
echo "[S37] CATALOG     = $CATALOG"
echo "[S37] PY_SCRIPT   = $PY"
echo "[S37] OUT_PAIRS   = $OUT_PAIRS"
echo "[S37] OUT_SUFFIX  = $OUT_SUFFIX"
echo "[S37] OUT_TXT     = $OUT_TXT"

# Basic checks
if [ ! -s "$SLOTS" ]; then
  echo "[S37] ERROR: missing or empty slots file: $SLOTS" >&2
  exit 1
fi

if [ ! -s "$CATALOG" ]; then
  echo "[S37] ERROR: missing or empty catalogue file: $CATALOG" >&2
  exit 1
fi

if [ ! -x "$PY" ]; then
  echo "[S37] ERROR: Python script not executable: $PY" >&2
  exit 1
fi

mkdir -p "$BASE/PhaseS/out"

python3 "$PY" \
  --slots "$SLOTS" \
  --catalogue "$CATALOG" \
  --out-pairs "$OUT_PAIRS" \
  --out-suffix "$OUT_SUFFIX" \
  --out-txt "$OUT_TXT"

echo "[S37] Done."
echo "  - $OUT_PAIRS"
echo "  - $OUT_SUFFIX"
echo "  - $OUT_TXT"
