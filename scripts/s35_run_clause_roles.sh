#!/usr/bin/env bash
set -euo pipefail

# Base repo path (can be overridden by env)
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

SKELETONS="$BASE/PhaseS/out/s34_clause_templates.tsv"
ROLES="$BASE/PhaseS/out/s34_positional_roles.tsv"
OUT_TSV="$BASE/PhaseS/out/s35_clause_role_patterns.tsv"
OUT_TXT="$BASE/PhaseS/out/s35_clause_role_patterns.txt"
PY="$BASE/scripts/s35_build_clause_roles.py"

# Sanity checks
for f in "$SKELETONS" "$ROLES" "$PY"; do
  if [ ! -f "$f" ]; then
    echo "[S35] ERROR: missing input: $f" >&2
    exit 1
  fi
done

echo "[S35] BASE         = $BASE"
echo "[S35] SKELETONS    = $SKELETONS"
echo "[S35] ROLES        = $ROLES"
echo "[S35] OUT_TSV      = $OUT_TSV"
echo "[S35] OUT_TXT      = $OUT_TXT"

python3 "$PY" \
  --skeletons "$SKELETONS" \
  --roles "$ROLES" \
  --out-tsv "$OUT_TSV" \
  --out-txt "$OUT_TXT"

echo "[S35] Done. Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_TXT"
