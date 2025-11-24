#!/usr/bin/env sh
#
# S40 – Apply valency ladder (S39) to concrete agent–patient clauses (S37).
# Produces an overlay file with one row per clause + valency metadata.
#
# Inputs:
#   PhaseS/out/s37_agent_patient_pairs.tsv
#   PhaseS/out/s39_valency_ladder.tsv
#
# Output:
#   PhaseS/out/s40_clause_valency_overlays.tsv
#
# Key:
#   Join on (family, agent_suffix, patient_suffix).

set -eu

# 1) Resolve BASE
if [ -n "${BASE-}" ]; then
  BASE_DIR="$BASE"
else
  BASE_DIR="$HOME/Voynich/Voynich_Reproducible_Core"
fi

P37="$BASE_DIR/PhaseS/out/s37_agent_patient_pairs.tsv"
P39="$BASE_DIR/PhaseS/out/s39_valency_ladder.tsv"
OUT="$BASE_DIR/PhaseS/out/s40_clause_valency_overlays.tsv"

echo "[S40] BASE  = $BASE_DIR"
echo "[S40] P37   = $P37"
echo "[S40] P39   = $P39"
echo "[S40] OUT   = $OUT"

# 2) Sanity checks
if [ ! -s "$P37" ]; then
  echo "[S40] ERROR: missing or empty $P37" >&2
  exit 1
fi

if [ ! -s "$P39" ]; then
  echo "[S40] ERROR: missing or empty $P39" >&2
  exit 1
fi

# 3) Build overlay via awk join.
#    S39 cols (from your file):
#      1=family, 2=agent_suffix, 3=patient_suffix,
#      4=valency_id, 5=ladder_pattern, 6=valency_class,
#      7=verb_slot_hint, 8=confidence, 9=notes
#
#    S37 cols:
#      1=family, 2=role_group, 3=template_id,
#      4=agent_token, 5=process_token, 6=patient_token,
#      7=agent_suffix, 8=patient_suffix,
#      9=count, 10=family_total_instances,
#      11=coverage_frac, 12=clause_role_pattern
#
#    Output header:
#      family, role_group, template_id,
#      agent_token, process_token, patient_token,
#      agent_suffix, patient_suffix,
#      count, family_total_instances, coverage_frac,
#      clause_role_pattern,
#      valency_id, valency_class, verb_slot_hint,
#      confidence, valency_notes

awk -F'\t' '
  BEGIN {
    OFS = "\t"
  }

  # First pass: read valency ladder (P39).
  FNR==NR {
    if (FNR == 1) {
      # Skip header
      next
    }
    fam  = $1
    asuf = $2
    psuf = $3
    key = fam OFS asuf OFS psuf

    vid[key]    = $4
    vclass[key] = $6
    vslot[key]  = $7
    vconf[key]  = $8
    vnote[key]  = $9
    next
  }

  # Second pass: read agent–patient pairs (P37).
  NR == FNR { next }  # safety, but not strictly needed

  FNR == 1 {
    # Input header from S37, we write our own extended header.
    print "family",
          "role_group",
          "template_id",
          "agent_token",
          "process_token",
          "patient_token",
          "agent_suffix",
          "patient_suffix",
          "count",
          "family_total_instances",
          "coverage_frac",
          "clause_role_pattern",
          "valency_id",
          "valency_class",
          "verb_slot_hint",
          "confidence",
          "valency_notes"
    next
  }

  {
    fam  = $1
    asuf = $7
    psuf = $8
    key  = fam OFS asuf OFS psuf

    # Default if no valency hit
    id    = (key in vid    ? vid[key]    : "VAL_NONE")
    class = (key in vclass ? vclass[key] : "VAL_UNKNOWN")
    slot  = (key in vslot  ? vslot[key]  : "AGENT_ACTS_ON_PATIENT?")
    conf  = (key in vconf  ? vconf[key]  : "0.0")
    note  = (key in vnote  ? vnote[key]  : "no_valency_match")

    print $1,  # family
          $2,  # role_group
          $3,  # template_id
          $4,  # agent_token
          $5,  # process_token
          $6,  # patient_token
          $7,  # agent_suffix
          $8,  # patient_suffix
          $9,  # count
          $10, # family_total_instances
          $11, # coverage_frac
          $12, # clause_role_pattern
          id,
          class,
          slot,
          conf,
          note
  }
' "$P39" "$P37" > "$OUT"

echo "[S40] Done. Wrote: $OUT"
