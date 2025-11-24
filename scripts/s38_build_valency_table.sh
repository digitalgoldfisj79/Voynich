#!/usr/bin/env sh
# S38 – build suffix-based valency table from S37 agent–patient pairs
# Inputs:
#   $BASE/PhaseS/out/s37_agent_patient_suffix_pairs.tsv
# Output:
#   $BASE/PhaseS/out/s38_valency_table.tsv
#
# Safe: POSIX sh, no tmp outside project, atomic-ish write.

set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTDIR="$BASE/PhaseS/out"
IN_S37="$OUTDIR/s37_agent_patient_suffix_pairs.tsv"
OUT_S38="$OUTDIR/s38_valency_table.tsv"
TMP_S38="$OUT_S38.tmp.$$"

echo "[S38] BASE      = $BASE"
echo "[S38] IN_S37    = $IN_S37"
echo "[S38] OUT_S38   = $OUT_S38"

if [ ! -s "$IN_S37" ]; then
  echo "[S38] ERROR: missing or empty input: $IN_S37" >&2
  exit 1
fi

# Build S38
# S37 header is:
#   family  agent_suffix    patient_suffix  n_templates
#   total_clause_count      mean_count_per_template
#   family_total_instances  approx_coverage

{
  # Header for valency table
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "family" \
    "agent_suffix" \
    "patient_suffix" \
    "n_templates" \
    "total_clause_count" \
    "approx_coverage" \
    "valency_id" \
    "ladder_pattern" \
    "verb_slot_hint" \
    "confidence" \
    "notes"

  # Data rows
  awk -F'\t' 'NR==1 { next } NF >= 8 {
      fam = $1
      a   = $2
      p   = $3
      nt  = $4
      tc  = $5
      cov = $8

      # trim simple leading/trailing spaces
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", fam)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", a)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", p)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", nt)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", tc)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", cov)

      if (fam=="" || a=="" || p=="") next

      # Stable valency ID: VAL_<family>_<agent>_<patient>
      vid = "VAL_" fam "_" a "_" p

      # Default ladder pattern is AGENT>PROCESS>PATIENT
      # verb_slot_hint / confidence / notes are manual fields
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", \
             fam, a, p, nt, tc, cov, \
             vid, "AGENT>PROCESS>PATIENT", "UNASSIGNED", "0.0", ""
  }' "$IN_S37" \
  | sort -k6,6gr -k1,1 -k2,2 -k3,3
} > "$TMP_S38"

mv "$TMP_S38" "$OUT_S38"
echo "[S38] Wrote: $OUT_S38"
