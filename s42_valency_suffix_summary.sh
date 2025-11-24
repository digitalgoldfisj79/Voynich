#!/usr/bin/env sh
#
# S42 – summary of suffix-level valency hits
#
# Usage:
#   BASE="$HOME/Voynich/Voynich_Reproducible_Core" \
#     ./scripts/s42_valency_suffix_summary.sh \
#       PhaseS/out/s41b_valency_suffix_hits_f21r.tsv \
#       > PhaseS/out/s42_valency_suffix_summary_f21r.tsv
#
# You can also pass multiple s41b files; it will aggregate across them.
#

set -eu

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 PhaseS/out/s41b_valency_suffix_hits_*.tsv" >&2
  exit 1
fi

awk '
BEGIN {
  FS = OFS = "\t"
}

FNR == 1 {
  # Detect header: assume first line starting with \"folio\" is header
  # Capture column indices by name so we remain robust if order changes.
  if ($1 == "folio") {
    n = NF
    for (i = 1; i <= n; i++) {
      if ($i == "folio")          col_folio = i
      if ($i == "agent_suffix")   col_agent_suffix = i
      if ($i == "patient_suffix") col_patient_suffix = i
      if ($i == "valency_id")     col_valency_id = i
      if ($i == "valency_class")  col_valency_class = i
    }
    next
  }
}

{
  folio  = (col_folio          ? $col_folio          : "")
  a_suf  = (col_agent_suffix   ? $col_agent_suffix   : "")
  p_suf  = (col_patient_suffix ? $col_patient_suffix : "")
  vid    = (col_valency_id     ? $col_valency_id     : "")
  vclass = (col_valency_class  ? $col_valency_class  : "")

  # Skip any malformed rows
  if (folio == "" || a_suf == "" || p_suf == "") next

  key = folio "\034" a_suf "\034" p_suf "\034" vid "\034" vclass
  count[key]++
}

END {
  print "folio",
        "agent_suffix",
        "patient_suffix",
        "valency_id",
        "valency_class",
        "hits"

  for (k in count) {
    split(k, f, "\034")
    print f[1], f[2], f[3], f[4], f[5], count[k]
  }
}
' "$@"
