#!/data/data/com.termux/files/usr/bin/sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
OUTD="$BASE/PhaseS/out"
TMP="$BASE/PhaseS/tmp"
SECMAP="$BASE/metadata/folio_sections.tsv"
HANDMAP="$OUTD/s49_folio_hands.tsv"

mkdir -p "$TMP" "$OUTD"

echo "[S49] Running hand/register summary..."

# 1. Extract folio→hand (and currier) if needed
if [ ! -f "$HANDMAP" ]; then
  echo "[S49] s49_folio_hands.tsv not found, running extractor..."
  python3 "$BASE/scripts/s49_extract_folio_hands.py"
fi

# 2. Sanity check inputs
if [ ! -f "$SECMAP" ]; then
  echo "[S49] ERROR: metadata/folio_sections.tsv not found at $SECMAP" >&2
  exit 1
fi

# 3. Sort for join
sort -k1,1 "$HANDMAP" > "$TMP/s49_folio_hands.sorted.tsv"
sort -k1,1 "$SECMAP"  > "$TMP/s49_folio_sections.sorted.tsv"

# 4. Join → folio, hand, currier, section
join -t "$(printf '\t')" -1 1 -2 1 \
  "$TMP/s49_folio_hands.sorted.tsv" \
  "$TMP/s49_folio_sections.sorted.tsv" \
  > "$TMP/s49_folio_hand_section.tsv"
# Columns: folio hand currier section

############################
# 5. Per-hand × section summary
############################
awk -F'\t' '
{
  hand = $2
  sec  = $4
  total[hand]++
  if (sec=="Herbal")          herb[hand]++
  else if (sec=="Biological") bio[hand]++
  else if (sec=="Pharmaceutical") pharm[hand]++
  else if (sec=="Recipes")   rec[hand]++
  else if (sec=="Astronomical") astro[hand]++
  else                        unknown[hand]++
}
END{
  OFS = "\t"
  print "hand","n_folios","n_herbal","n_bio","n_pharm","n_recipes","n_astro","n_unknown","prop_herbal","prop_bio","prop_recipes"
  for (h in total) {
    t = total[h] + 0
    hcount = herb[h] + 0
    bcount = bio[h] + 0
    pcount = pharm[h] + 0
    rcount = rec[h] + 0
    acount = astro[h] + 0
    ucount = unknown[h] + 0
    ph = (t>0 ? hcount/t : 0)
    pb = (t>0 ? bcount/t : 0)
    pr = (t>0 ? rcount/t : 0)
    print h, t, hcount, bcount, pcount, rcount, acount, ucount, ph, pb, pr
  }
}
' "$TMP/s49_folio_hand_section.tsv" > "$OUTD/s49_hand_section_summary.tsv"

############################
# 6. Per-hand × Currier summary
############################
awk -F'\t' '
NR==1 {next}
{
  hand = $2
  cur  = $3
  total[hand]++
  if (cur=="A") A[hand]++
  else if (cur=="B") B[hand]++
  else other[hand]++
}
END{
  OFS = "\t"
  print "hand","n_folios","n_currier_A","n_currier_B","n_currier_other","prop_A","prop_B"
  for (h in total) {
    t = total[h] + 0
    a = A[h] + 0
    b = B[h] + 0
    o = other[h] + 0
    pa = (t>0 ? a/t : 0)
    pb = (t>0 ? b/t : 0)
    print h, t, a, b, o, pa, pb
  }
}
' "$HANDMAP" > "$OUTD/s49_hand_currier_summary.tsv"

echo "[S49] Wrote:"
echo "  - $OUTD/s49_hand_section_summary.tsv"
echo "  - $OUTD/s49_hand_currier_summary.tsv"
