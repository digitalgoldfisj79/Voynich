#!/usr/bin/env sh
#
# S42c – merge multiple S42 valency suffix summaries into one aggregate file
#
# Usage:
#   BASE="$HOME/Voynich/Voynich_Reproducible_Core" \
#     ./scripts/s42c_merge_valency_suffix.sh \
#       PhaseS/out/s42_valency_suffix_summary_f1r.tsv \
#       PhaseS/out/s42_valency_suffix_summary_f5r.tsv \
#       ... \
#       > PhaseS/out/s42_valency_suffix_summary_HERBAL_A_merged.tsv
#

set -eu

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 s42_valency_suffix_summary_*.tsv" >&2
  exit 1
fi

awk '
BEGIN {
  FS = OFS = "\t"
}

FNR == 1 {
  # Header line, detect columns
  if ($1 == "folio") {
    n = NF
    for (i = 1; i <= n; i++) {
      if ($i == "folio")          col_folio = i
      if ($i == "agent_suffix")   col_agent_suffix = i
      if ($i == "patient_suffix") col_patient_suffix = i
      if ($i == "valency_id")     col_valency_id = i
      if ($i == "valency_class")  col_valency_class = i
      if ($i == "hits")           col_hits = i
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
  hits   = (col_hits           ? $col_hits + 0       : 0)

  if (a_suf == "" || p_suf == "" || vid == "" || vclass == "") next

  key = a_suf "\034" p_suf "\034" vid "\034" vclass

  total_hits[key] += hits

  if (folio != "") {
    # Track distinct folios for this key using a composite key
    fk = key "\t" folio
    folio_seen[fk] = 1
  }
}

END {
  print "agent_suffix",
        "patient_suffix",
        "valency_id",
        "valency_class",
        "total_hits",
        "n_folios"

  for (key in total_hits) {
    split(key, f, "\034")
    a_suf  = f[1]
    p_suf  = f[2]
    vid    = f[3]
    vclass = f[4]

    # Count distinct folios for this key
    nfol = 0
    for (fk in folio_seen) {
      split(fk, parts, "\t")
      k2   = parts[1]
      if (k2 == key) nfol++
    }

    print a_suf, p_suf, vid, vclass, total_hits[key], nfol
  }
}
' "$@"
