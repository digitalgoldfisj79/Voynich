#!/usr/bin/env sh
# S96 – Build Voynich stem frequencies from t03_enriched_translations.tsv
# Output: metadata/t03_stem_frequencies.tsv  (stem\tstem_freq)

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
T03="$BASE/PhaseT/out/t03_enriched_translations.tsv"
OUT="$BASE/metadata/t03_stem_frequencies.tsv"

echo "[s96] BASE: $BASE"
echo "[s96] T03:  $T03"
echo "[s96] OUT:  $OUT"

if [ ! -f "$T03" ]; then
  echo "[s96][ERROR] Missing t03 file: $T03" >&2
  exit 1
fi

mkdir -p "$BASE/metadata"

awk -F'\t' '
  NR==1 {
    stem_col = -1
    for (i = 1; i <= NF; i++) {
      if ($i == "stem") {
        stem_col = i
        break
      }
    }
    if (stem_col < 0) {
      printf "[s96][ERROR] Could not find stem column in header\n" > "/dev/stderr"
      exit 1
    }
    next
  }
  {
    s = $stem_col
    if (s != "") {
      counts[s]++
    }
  }
  END {
    print "stem\tstem_freq"
    for (s in counts) {
      print s "\t" counts[s]
    }
  }
' "$T03" > "$OUT.tmp"

mv "$OUT.tmp" "$OUT"
echo "[s96] Wrote stem frequencies to $OUT"

# quick sanity
echo "[s96] Top 10 stems by frequency:"
sort -k2,2nr "$OUT" | head -10
