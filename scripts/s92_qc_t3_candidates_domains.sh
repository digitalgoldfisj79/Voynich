#!/usr/bin/env sh
# S92 – QC for metadata/t3_candidates_domains.tsv

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
CAND_TSV="$BASE/metadata/t3_candidates_domains.tsv"

echo "[s92] BASE:     $BASE"
echo "[s92] CAND_TSV: $CAND_TSV"

if [ ! -f "$CAND_TSV" ]; then
  echo "[s92][ERROR] Missing candidate file: $CAND_TSV" >&2
  exit 1
fi

echo "[s92] Head of t3_candidates_domains.tsv:"
head -n 10 "$CAND_TSV"

header=$(head -n 1 "$CAND_TSV")

req="stem functional_label lemma_latin gloss_en latin_domain corpus_freq latin_source candidate_source"
ok=1
for col in $req; do
  printf '%s\n' "$header" | grep -q "\b$col\b" || {
    echo "[s92][ERROR] Missing required column in header: $col" >&2
    ok=0
  }
done
[ "$ok" -eq 1 ] && echo "[s92] Header looks OK."

echo
wc -l "$CAND_TSV" | awk '{print "[s92] Total lines:", $1, "(data rows:", $1-1 ")"}'

echo
echo "[s92] Unique stems and counts:"
awk -F'\t' 'NR>1 {cnt[$1]++} END{for(s in cnt) printf "%d\t%s\n", cnt[s], s}' "$CAND_TSV" \
  | sort -k2,2

echo
echo "[s92] Candidate rows by functional_label:"
awk -F'\t' 'NR>1 {cnt[$2]++} END{for(k in cnt) printf "%s\t%d\n", k, cnt[k]}' "$CAND_TSV" \
  | sort

echo
echo "[s92] Candidate rows by latin_domain:"
awk -F'\t' 'NR>1 {cnt[$5]++} END{for(k in cnt) printf "%s\t%d\n", k, cnt[k]}' "$CAND_TSV" \
  | sort

# Quick spotlight on a few stems
for STEM in qotar okar kar ol; do
  echo
  echo "[s92] --- Candidates for stem=$STEM ---"
  awk -F'\t' -v s="$STEM" 'NR==1 || $1==s' "$CAND_TSV" \
    | column -t -s "$(printf '\t')"
done

