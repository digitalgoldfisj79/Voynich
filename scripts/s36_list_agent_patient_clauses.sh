#!/usr/bin/env bash
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
CATALOG="$BASE/PhaseS/out/s36_clause_role_catalogue.tsv"

if [ ! -s "$CATALOG" ]; then
  echo "[s36_list] ERROR: missing catalogue: $CATALOG" >&2
  exit 1
fi

awk -F'\t' '
  NR==1 { print; next }
  {
    # Trim whitespace on clause_role_pattern
    if (NF >= 8) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $8)
    }
  }
  # Keep only AGENT→PATIENT clauses with non-zero count
  $5+0 > 0 && $8 ~ /^AGENT_CAND-AMBIGUOUS-PATIENT_CAND$/
' "$CATALOG" | sort -k5,5gr
