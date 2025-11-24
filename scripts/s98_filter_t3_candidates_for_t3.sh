#!/usr/bin/env sh
# S98 – Filter T3 domain candidates to remove obvious junk stems
# Current rule: drop single-letter stems (s, r, l, y, etc.).
# You can later extend the AWK section to drop more patterns if needed.

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}

SRC="$BASE/metadata/t3_candidates_domains_curated.tsv"
DST="$BASE/metadata/t3_candidates_domains_filtered.tsv"

echo "[s98] BASE: $BASE"
echo "[s98] SRC:  $SRC"
echo "[s98] DST:  $DST"

if [ ! -f "$SRC" ]; then
  echo "[s98][ERROR] Source file not found: $SRC" >&2
  exit 1
fi

lines_before=$(wc -l < "$SRC" | awk '{print $1}')
echo "[s98] Source rows (incl. header): $lines_before"

tmp="$DST.tmp"
rm -f "$tmp"

awk -F'\t' '
NR==1 { print; next }  # keep header
{
  stem = $1
  len  = length(stem)

  # --- FILTER RULES ---------------------------------------------------
  # 1. Drop all single-letter stems (they are almost certainly function morphemes).
  #    If you *do* want a specific one (e.g. "o"), comment out or tweak this.
  if (len == 1) {
    dropped[stem]++
    next
  }

  # In future you can add more rules here, e.g. to drop specific 2-char stems:
  # if (len == 2 && stem !~ /^(ol|ar|al|am)$/) { dropped[stem]++; next }

  # --------------------------------------------------------------------
  print
}
END {
  n_dropped = 0
  for (s in dropped) {
    n_dropped += dropped[s]
    printf("[s98] Dropped stem=%s (rows=%d)\n", s, dropped[s]) > "/dev/stderr"
  }
  printf("[s98] Total dropped rows: %d\n", n_dropped) > "/dev/stderr"
}
' "$SRC" > "$tmp"

mv "$tmp" "$DST"

lines_after=$(wc -l < "$DST" | awk '{print $1}')
echo "[s98] Filtered rows (incl. header): $lines_after"
echo "[s98] Done. Now use $DST as input for s97."
