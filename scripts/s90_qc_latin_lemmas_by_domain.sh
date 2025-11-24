#!/usr/bin/env sh
# S90 – QC for metadata/latin_lemmas_by_domain.tsv

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
LEMMAS="$BASE/metadata/latin_lemmas_by_domain.tsv"

echo "[s90] BASE:   $BASE"
echo "[s90] LEMMAS: $LEMMAS"

if [ ! -f "$LEMMAS" ]; then
  echo "[s90][ERROR] Missing file: $LEMMAS" >&2
  exit 1
fi

echo "[s90] Head:"
head -n 10 "$LEMMAS"

# Check required columns exist
req="domain lemma gloss_en frequency source"
header=$(head -n 1 "$LEMMAS")
ok=1
for col in $req; do
  printf '%s\n' "$header" | grep -q "\b$col\b" || {
    echo "[s90][ERROR] Missing required column in header: $col" >&2
    ok=0
  }
done
[ "$ok" -eq 1 ] && echo "[s90] Header looks OK."

echo
echo "[s90] Unique domains and counts:"
awk -F'\t' 'NR>1 && NF>=1 {cnt[$1]++} END{for(d in cnt) printf "%s\t%d\n", d, cnt[d]}' "$LEMMAS" \
  | sort

echo
echo "[s90] Top 5 lemmas per domain:"
awk -F'\t' 'NR>1 && NF>=4 {
  dom=$1; lem=$2; freq=$4+0;
  key = dom FS lem;
  if (freq > max[key]) max[key]=freq;
}
END{
  for (k in max) {
    print k FS max[k];
  }
}' "$LEMMAS" | sort -k1,1 -k4,4nr | awk -F'\t' '
{
  dom=$1;
  if (dom!=last) {
    count[dom]=0;
    last=dom;
  }
  if (count[dom] < 5) {
    printf "%-15s %-15s freq=%d\n", $1, $2, $4;
    count[dom]++;
  }
}'
