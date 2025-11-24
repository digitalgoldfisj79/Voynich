#!/usr/bin/env sh
#
# S41b – suffix-level valency scan (Currier A/B)
#
# Usage:
#   BASE="$HOME/Voynich/Voynich_Reproducible_Core" \
#     ./scripts/s41b_scan_folio_valency_suffix.sh \
#       PhaseS/in/f21r_C.txt \
#       PhaseS/out/s39_valency_ladder.tsv
#
# Output:
#   PhaseS/out/s41b_valency_suffix_hits_<folio>.tsv
#
# Logic:
#   – Loads suffix pairs (agent_suffix, patient_suffix) from s39_valency_ladder.tsv
#   – Scans a folio C-file as sliding triples (tok1, tok2, tok3)
#   – Emits a row whenever tok1 endswith(agent_suffix)
#                     AND tok3 endswith(patient_suffix)
#   – Carries through valency_id and valency_class from s39
#

set -eu

if [ "${BASE-}" = "" ]; then
  BASE="$(pwd)"
fi

if [ "$#" -ne 2 ]; then
  echo "Usage: BASE=/path/to/Voynich_Reproducible_Core \\" >&2
  echo "       $0 PhaseS/in/<folio>_C.txt PhaseS/out/s39_valency_ladder.tsv" >&2
  exit 1
fi

FOLIO_C="$1"
S39_LADDER="$2"

if [ ! -f "$FOLIO_C" ]; then
  echo "[err] folio file not found: $FOLIO_C" >&2
  exit 1
fi

if [ ! -f "$S39_LADDER" ]; then
  echo "[err] s39 ladder file not found: $S39_LADDER" >&2
  exit 1
fi

OUTD="$BASE/PhaseS/out"
mkdir -p "$OUTD"

# Derive folio tag from filename (e.g. f21r_C.txt → f21r)
fname=$(basename "$FOLIO_C")
folio="${fname%_C.txt}"
folio="${folio%.txt}"

OUTFILE="$OUTD/s41b_valency_suffix_hits_${folio}.tsv"
TMP_OUT="${OUTFILE}.tmp"

awk -v ladder="$S39_LADDER" -v folio="$folio" '
BEGIN {
  FS = OFS = "\t"

  # === 1. Load suffix pairs from s39_valency_ladder.tsv ===
  # Uses header names: agent_suffix, patient_suffix, valency_id, valency_class

  while ((getline line < ladder) > 0) {
    if (line ~ /^[[:space:]]*$/) continue  # skip blank
    if (line ~ /^#/) continue             # skip comments

    # Header row
    if (!have_header) {
      have_header = 1
      n = split(line, hdr, "\t")
      for (i = 1; i <= n; i++) {
        if (hdr[i] == "agent_suffix")   col_agent_suffix = i
        if (hdr[i] == "patient_suffix") col_patient_suffix = i
        if (hdr[i] == "valency_id" || hdr[i] == "rule_id") col_rule_id = i
        if (hdr[i] == "valency_class" || hdr[i] == "class" || hdr[i] == "role") col_class = i
      }
      if (!col_agent_suffix || !col_patient_suffix) {
        print "[err] s39 header must contain agent_suffix and patient_suffix" > "/dev/stderr"
        exit 1
      }
      # rule_id / class are optional
      continue
    }

    # Data rows
    split(line, f, "\t")
    a_suf = f[col_agent_suffix]
    p_suf = f[col_patient_suffix]

    gsub(/^[[:space:]]+|[[:space:]]+$/, "", a_suf)
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", p_suf)
    if (a_suf == "" || p_suf == "") continue

    key = a_suf "\034" p_suf
    if (!(key in seen_pair)) {
      seen_pair[key] = 1
      pair_a_suf[pairs] = a_suf
      pair_p_suf[pairs] = p_suf
      pair_rule[pairs]  = (col_rule_id ? f[col_rule_id] : "")
      pair_class[pairs] = (col_class   ? f[col_class]   : "")
      pairs++
    }
  }
  close(ladder)

  if (pairs == 0) {
    print "[warn] no suffix pairs loaded from s39" > "/dev/stderr"
  } else {
    print "[info] loaded", pairs, "suffix pairs from", ladder > "/dev/stderr"
  }

  # Output header
  print "folio",
        "line_idx",
        "triple_idx",
        "tok1",
        "tok2",
        "tok3",
        "agent_suffix",
        "patient_suffix",
        "valency_id",
        "valency_class"
}

# === 2. Scan folio C-file as sliding triples ===
{
  raw = $0

  # Skip comments / blanks in folio
  if (raw ~ /^[[:space:]]*$/) next
  if (raw ~ /^#/) next

  # Strip inline tags like <f21r.1,@P0>
  gsub(/<[^>]+>/, "", raw)

  # EVA words: dot-separated
  gsub(/\./, " ", raw)

  # Normalize spaces
  gsub(/[[:space:]]+/, " ", raw)
  sub(/^[[:space:]]+/, "", raw)
  sub(/[[:space:]]+$/, "", raw)

  if (raw == "") next

  ntok = split(raw, t, " ")
  if (ntok < 3) next

  line_idx++
  triple_idx = 0

  for (i = 1; i <= ntok - 2; i++) {
    a = t[i]
    m = t[i+1]
    p = t[i+2]
    triple_idx++

    for (k = 0; k < pairs; k++) {
      a_suf = pair_a_suf[k]
      p_suf = pair_p_suf[k]

      if (endswith(a, a_suf) && endswith(p, p_suf)) {
        rule = pair_rule[k]
        cls  = pair_class[k]
        print folio,
              line_idx,
              triple_idx,
              a,
              m,
              p,
              a_suf,
              p_suf,
              rule,
              cls
      }
    }
  }
}

function endswith(s, suf,   ls, lsf) {
  ls  = length(s)
  lsf = length(suf)
  if (ls < lsf) return 0
  return (substr(s, ls - lsf + 1, lsf) == suf)
}
' "$FOLIO_C" > "$TMP_OUT"

mv "$TMP_OUT" "$OUTFILE"

echo "[s41b] Wrote suffix-level valency hits to: $OUTFILE"
