#!/usr/bin/env sh
#
# S42b – compare suffix-level valency coverage between two S42 (or merged S42c) summaries
#
# Usage:
#   BASE="$HOME/Voynich/Voynich_Reproducible_Core" \
#     ./scripts/s42b_compare_valency_suffix.sh \
#       PhaseS/out/s42_valency_suffix_summary_PROC_B_merged.tsv \
#       PhaseS/out/s42_valency_suffix_summary_HERBAL_A_merged.tsv \
#       > PhaseS/out/s42b_compare_B_vs_A.tsv
#
# Output columns:
#   agent_suffix  patient_suffix  valency_id  valency_class
#   hits_<A>  hits_<B>  total_hits  delta_<B>_minus_<A>
#

set -eu

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 summary_A.tsv summary_B.tsv" >&2
  exit 1
fi

A_FILE="$1"
B_FILE="$2"

if [ ! -f "$A_FILE" ]; then
  echo "[err] not found: $A_FILE" >&2
  exit 1
fi

if [ ! -f "$B_FILE" ]; then
  echo "[err] not found: $B_FILE" >&2
  exit 1
fi

baseA=$(basename "$A_FILE")
baseB=$(basename "$B_FILE")

# Derive short labels from filenames (e.g. PROC_B_merged / HERBAL_A_merged)
labelA="${baseA%.tsv}"
labelB="${baseB%.tsv}"

awk -v fileA="$A_FILE" -v fileB="$B_FILE" -v labelA="$labelA" -v labelB="$labelB" '
BEGIN {
  FS = OFS = "\t"
}

function load_file(path, slot,   line, hdr, i, n, col_a_suf, col_p_suf, col_vid, col_vclass, col_hits, f) {
  while ((getline line < path) > 0) {
    if (line ~ /^[[:space:]]*$/) continue

    if (line ~ /^agent_suffix[ \t]/ || line ~ /^folio[ \t]/) {
      # header row
      n = split(line, hdr, "\t")
      for (i = 1; i <= n; i++) {
        if (hdr[i] == "agent_suffix")   col_a_suf   = i
        if (hdr[i] == "patient_suffix") col_p_suf   = i
        if (hdr[i] == "valency_id")     col_vid     = i
        if (hdr[i] == "valency_class")  col_vclass  = i
        if (hdr[i] == "hits" || hdr[i] == "total_hits") col_hits = i
      }
      continue
    }

    n = split(line, f, "\t")
    if (!col_a_suf || !col_p_suf || !col_vid || !col_vclass || !col_hits) {
      continue
    }

    a_suf  = f[col_a_suf]
    p_suf  = f[col_p_suf]
    vid    = f[col_vid]
    vclass = f[col_vclass]
    hits   = f[col_hits] + 0

    key = a_suf "\034" p_suf "\034" vid "\034" vclass

    if (slot == "A") {
      hitsA[key] += hits
    } else {
      hitsB[key] += hits
    }
    seen[key] = 1
  }
  close(path)
}

END {
  # done in main block
}
' /dev/null > /dev/null 2>&1

# Now run real comparison
awk -v fileA="$A_FILE" -v fileB="$B_FILE" -v labelA="$labelA" -v labelB="$labelB" '
BEGIN {
  FS = OFS = "\t"
  load_file(fileA, "A")
  load_file(fileB, "B")

  print "agent_suffix",
        "patient_suffix",
        "valency_id",
        "valency_class",
        "hits_" labelA,
        "hits_" labelB,
        "total_hits",
        "delta_" labelB "_minus_" labelA
}

function load_file(path, slot,   line, hdr, i, n, col_a_suf, col_p_suf, col_vid, col_vclass, col_hits, f) {
  while ((getline line < path) > 0) {
    if (line ~ /^[[:space:]]*$/) continue

    if (line ~ /^agent_suffix[ \t]/ || line ~ /^folio[ \t]/) {
      n = split(line, hdr, "\t")
      for (i = 1; i <= n; i++) {
        if (hdr[i] == "agent_suffix")   col_a_suf   = i
        if (hdr[i] == "patient_suffix") col_p_suf   = i
        if (hdr[i] == "valency_id")     col_vid     = i
        if (hdr[i] == "valency_class")  col_vclass  = i
        if (hdr[i] == "hits" || hdr[i] == "total_hits") col_hits = i
      }
      continue
    }

    n = split(line, f, "\t")
    if (!col_a_suf || !col_p_suf || !col_vid || !col_vclass || !col_hits) {
      continue
    }

    a_suf  = f[col_a_suf]
    p_suf  = f[col_p_suf]
    vid    = f[col_vid]
    vclass = f[col_vclass]
    hits   = f[col_hits] + 0

    key = a_suf "\034" p_suf "\034" vid "\034" vclass

    if (slot == "A") {
      hitsA[key] += hits
    } else {
      hitsB[key] += hits
    }
    seen[key] = 1
  }
  close(path)
}

END {
  for (key in seen) {
    split(key, f, "\034")
    a_suf  = f[1]
    p_suf  = f[2]
    vid    = f[3]
    vclass = f[4]

    ha = (key in hitsA ? hitsA[key] : 0)
    hb = (key in hitsB ? hitsB[key] : 0)
    total = ha + hb
    delta = hb - ha

    print a_suf, p_suf, vid, vclass, ha, hb, total, delta
  }
}
' /dev/null
