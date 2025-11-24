#!/usr/bin/env sh
# S90 – Domain lemma table sanity check
# Checks: file existence, header, basic counts, per-domain summary.

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
LEMMA_TSV="$BASE/metadata/latin_lemmas_by_domain.tsv"

echo "[s90] BASE:        $BASE"
echo "[s90] LEMMA_TSV:   $LEMMA_TSV"

if [ ! -f "$LEMMA_TSV" ]; then
  echo "[s90][ERROR] File not found: $LEMMA_TSV" >&2
  exit 1
fi

# Show header and first few rows
echo "[s90] Head of latin_lemmas_by_domain.tsv:"
head -n 10 "$LEMMA_TSV"

# Check header columns
HEADER=$(head -n 1 "$LEMMA_TSV")
# Expected: domain\tlemma\tgloss_en\tfrequency\tsource
EXPECTED="domain\tlemma\tgloss_en\tfrequency\tsource"

if [ "x$HEADER" != "x$EXPECTED" ]; then
  echo "[s90][WARN] Header mismatch."
  echo "  Found:    $HEADER"
  echo "  Expected: $EXPECTED"
else
  echo "[s90] Header OK."
fi

# Count lines (including header)
TOTAL_LINES=$(wc -l < "$LEMMA_TSV")
DATA_LINES=$((TOTAL_LINES - 1))
echo "[s90] Total lines: $TOTAL_LINES (data rows: $DATA_LINES)"

# Per-domain frequency summary (sum of frequency column by domain)
echo "[s90] Per-domain frequency totals:"
awk -F'\t' 'NR>1 {freq[$1]+=$4} END{for(d in freq) printf "%s\t%d\n", d, freq[d]}' "$LEMMA_TSV" \
  | sort

# Per-domain row counts
echo "[s90] Per-domain row counts:"
awk -F'\t' 'NR>1 {cnt[$1]++} END{for(d in cnt) printf "%s\t%d\n", d, cnt[d]}' "$LEMMA_TSV" \
  | sort

echo "[s90] Done."
