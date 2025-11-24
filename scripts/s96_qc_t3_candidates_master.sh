#!/usr/bin/env sh
# S96 – QC for metadata/t3_candidates.tsv (master candidates)

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
MASTER="$BASE/metadata/t3_candidates.tsv"

echo "[s96] BASE:   $BASE"
echo "[s96] MASTER: $MASTER"

if [ ! -f "$MASTER" ]; then
  echo "[s96][ERROR] Missing master candidate file: $MASTER" >&2
  exit 1
fi

echo "[s96] Head of t3_candidates.tsv:"
head -n 10 "$MASTER"

header=$(head -n 1 "$MASTER")
req="stem functional_label lemma_latin gloss_en latin_domain corpus_freq latin_source candidate_source"
ok=1
for col in $req; do
  printf '%s\n' "$header" | grep -q "\b$col\b" || {
    echo "[s96][ERROR] Missing required column in header: $col" >&2
    ok=0
  }
done
[ "$ok" -eq 1 ] && echo "[s96] Header looks OK."

echo
wc -l "$MASTER" | awk '{print "[s96] Total lines:", $1, "(data rows:", $1-1 ")"}'

echo
echo "[s96] Candidate rows by functional_label:"
awk -F'\t' 'NR>1 {cnt[$2]++} END{for(k in cnt) printf "%s\t%d\n", k, cnt[k]}' "$MASTER" \
  | sort

echo
echo "[s96] Candidate rows by latin_domain:"
awk -F'\t' 'NR>1 {cnt[$5]++} END{for(k in cnt) printf "%s\t%d\n", k, cnt[k]}' "$MASTER" \
  | sort

