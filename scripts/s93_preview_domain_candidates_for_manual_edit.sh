#!/usr/bin/env sh
# S93 – Pretty-print domain-based candidates grouped by stem,
# for manual review / curation.

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
CAND_TSV="$BASE/metadata/t3_candidates_domains.tsv"

echo "[s93] BASE:     $BASE"
echo "[s93] CAND_TSV: $CAND_TSV"

if [ ! -f "$CAND_TSV" ]; then
  echo "[s93][ERROR] Missing candidate file: $CAND_TSV" >&2
  exit 1
fi

STEM_FILTER="${1:-}"

if [ -n "$STEM_FILTER" ]; then
  echo "[s93] Filtering for single stem: $STEM_FILTER"
  awk -F'\t' -v s="$STEM_FILTER" 'NR==1 || $1==s' "$CAND_TSV" \
    | column -t -s "$(printf '\t')" \
    | less
  exit 0
fi

echo "[s93] No stem filter provided; showing a few key stems."

for STEM in qotar okar kar ol ain am l aiin; do
  echo
  echo "### Stem: $STEM"
  awk -F'\t' -v s="$STEM" 'NR==1 || $1==s' "$CAND_TSV" \
    | column -t -s "$(printf '\t')" \
    | head -n 15
done

echo
echo "[s93] Hint: you can run:"
echo "  ./scripts/s93_preview_domain_candidates_for_manual_edit.sh qotar"
echo "to inspect a single stem."
