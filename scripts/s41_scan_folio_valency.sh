#!/usr/bin/env sh
# s41_scan_folio_valency.sh
# Scan a folio C-pack for triples that match S40 valency clauses
# and report where the strong/medium valency rules fire.

set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

if [ "$#" -ne 1 ]; then
  echo "usage: BASE=... $0 PATH/TO/folio_C.txt" >&2
  exit 1
fi

IN_PACK="$1"
S40="${S40:-$BASE/PhaseS/out/s40_clause_valency_overlays.tsv}"

if [ ! -s "$S40" ]; then
  echo "[s41] ERROR: missing or empty S40 file: $S40" >&2
  exit 1
fi

if [ ! -s "$IN_PACK" ]; then
  echo "[s41] ERROR: missing or empty folio file: $IN_PACK" >&2
  exit 1
fi

OUT_DIR="$BASE/PhaseS/out"
mkdir -p "$OUT_DIR"

BASENAME="$(basename "$IN_PACK")"
OUT_TSV="$OUT_DIR/s41_valency_hits_${BASENAME%.txt}.tsv"

awk -v OFS='\t' -v pack="$IN_PACK" '
  BEGIN {
    # nothing
  }

  # --------
  # First file: S40 overlays -> build valency triple map
  # --------
  FNR==1 && NR==1 {
    # S40 header; skip
    next
  }

  FNR==NR {
    # Columns in S40 (tab-separated):
    # 1 family
    # 2 role_group
    # 3 template_id
    # 4 agent_token
    # 5 process_token
    # 6 patient_token
    # 7 agent_suffix
    # 8 patient_suffix
    # 9 count
    # 10 family_total_instances
    # 11 coverage_frac
    # 12 clause_role_pattern
    # 13 valency_id
    # 14 valency_class
    # 15 verb_slot_hint
    # 16 confidence
    # 17 valency_notes

    # Only keep rules that actually have a valency class
    if (NF < 14) next

    key = $4 "|" $5 "|" $6
    family         = $1
    template_id    = $3
    agent_suffix   = $7
    patient_suffix = $8
    valency_id     = $13
    valency_class  = $14
    verb_slot      = $15
    conf           = $16
    notes          = (NF >= 17 ? $17 : "")

    # We keep both STRONG and MEDIUM; you can filter later by class
    meta[key] = family "\t" template_id "\t" agent_suffix "\t" patient_suffix \
               "\t" valency_id "\t" valency_class "\t" verb_slot "\t" conf "\t" notes
    next
  }

  # --------
  # Second file: folio C-lines
  # --------
  {
    line = $0
    # Skip empty / comment lines
    if (line ~ /^[[:space:]]*$/) next
    if (line ~ /^#/) next

    # Extract an ID like f21r.P.1;C from "<f21r.P.1;C> tokens..."
    id = ""
    text = line

    if (match(line, /^<([^>]+)>\s*(.*)$/, m)) {
      id = m[1]
      text = m[2]
    }

    # Normalise delimiters:
    # - dots, commas, exclamation marks and hyphens -> spaces
    gsub(/[.,!\-=]/, " ", text)

    # Strip simple {plant}-like markers to avoid spurious matches
    gsub(/\{[^}]*\}/, " ", text)

    # Split into tokens on whitespace
    n = split(text, t, /[[:space:]]+/)
    if (n < 3) next

    # Slide a 3-token window and look up in valency rules
    for (i = 1; i + 2 <= n; i++) {
      if (t[i] == "" || t[i+1] == "" || t[i+2] == "") continue
      triple = t[i] "|" t[i+1] "|" t[i+2]
      if (triple in meta) {
        # We have a valency hit
        split(meta[triple], m2, "\t")

        family         = m2[1]
        template_id    = m2[2]
        agent_suffix   = m2[3]
        patient_suffix = m2[4]
        valency_id     = m2[5]
        valency_class  = m2[6]
        verb_slot      = m2[7]
        conf           = m2[8]
        notes          = m2[9]

        # Output:
        # folio_id, token_index, agent_token, process_token, patient_token,
        # family, template_id, agent_suffix, patient_suffix,
        # valency_id, valency_class, verb_slot_hint, confidence, notes
        print id, i, t[i], t[i+1], t[i+2],
              family, template_id, agent_suffix, patient_suffix,
              valency_id, valency_class, verb_slot, conf, notes
      }
    }
  }
' "$S40" "$IN_PACK" > "$OUT_TSV"

echo "[s41] Wrote valency hits to: $OUT_TSV" >&2
