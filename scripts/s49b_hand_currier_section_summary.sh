#!/data/data/com.termux/files/usr/bin/sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
OUTD="$BASE/PhaseS/out"
TMP="$BASE/PhaseS/tmp"
mkdir -p "$OUTD" "$TMP"

HANDMAP="$OUTD/s49_folio_hands.tsv"
CURMAP="$OUTD/currier_map.tsv"
SECMAP="$BASE/metadata/folio_sections.tsv"
SUMMARY="$OUTD/s49b_hand_currier_section_summary.tsv"

echo "[S49b] Building hand × Currier × section summary..."

############################
# 1. Ensure folio→hand map exists
############################
if [ ! -f "$HANDMAP" ]; then
  echo "[S49b] s49_folio_hands.tsv not found, running extractor..."
  python3 "$BASE/scripts/s49_extract_folio_hands.py"
fi

if [ ! -f "$CURMAP" ]; then
  echo "[S49b] ERROR: currier_map.tsv not found at $CURMAP" >&2
  exit 1
fi

if [ ! -f "$SECMAP" ]; then
  echo "[S49b] ERROR: folio_sections.tsv not found at $SECMAP" >&2
  exit 1
fi

############################
# 2. Clean & sort inputs
############################

# HANDS: keep folio,hand only; drop header & weird rows
awk -F'\t' '
  NR==1 {next}                     # skip header
  $1 ~ /^f[0-9]/ && $2 != "" {
    # keep only normal folio IDs and non-empty hands
    print $1 "\t" $2
  }
' "$HANDMAP" | sort -k1,1 > "$TMP/s49b_folio_hands_clean.tsv"

# CURRIER: normalise to folio,currier (A/B/other), ignore comments/blank
awk -F'\t' '
  NF >= 2 && $1 ~ /^f[0-9]/ {
    print $1 "\t" $2
  }
' "$CURMAP" | sort -k1,1 > "$TMP/s49b_currier_clean.tsv"

# SECTIONS: folio,section; drop header and non-folios
awk -F'\t' '
  NR==1 {next}
  NF >= 2 && $1 ~ /^f[0-9]/ {
    print $1 "\t" $2
  }
' "$SECMAP" | sort -k1,1 > "$TMP/s49b_sections_clean.tsv"

############################
# 3. Join: folio → hand + Currier + section
############################

# First: hands + currier
join -t "$(printf '\t')" -1 1 -2 1 \
  "$TMP/s49b_folio_hands_clean.tsv" \
  "$TMP/s49b_currier_clean.tsv" \
  > "$TMP/s49b_folio_hand_currier.tsv"
# folio  hand  currier

# Then: add section
join -t "$(printf '\t')" -1 1 -2 1 \
  "$TMP/s49b_folio_hand_currier.tsv" \
  "$TMP/s49b_sections_clean.tsv" \
  > "$TMP/s49b_folio_hand_currier_section.tsv"
# folio  hand  currier  section

############################
# 4. Aggregate per-hand stats
############################
awk -F'\t' '
{
  fol = $1
  hand = $2
  cur = $3
  sec = $4

  # Filter out any weird hand labels if needed
  if (hand !~ /^[0-9]+$/) next

  total[hand]++

  # Currier counts
  if (cur == "A")      A[hand]++
  else if (cur == "B") B[hand]++
  else                 other[hand]++

  # Section counts
  if      (sec == "Herbal")          herb[hand]++
  else if (sec == "Biological")      bio[hand]++
  else if (sec == "Pharmaceutical")  pharm[hand]++
  else if (sec == "Recipes")         rec[hand]++
  else if (sec == "Astronomical")    astro[hand]++
  else                               unknown[hand]++
}
END{
  OFS = "\t"
  print "hand",
        "n_folios",
        "n_currier_A","n_currier_B","n_currier_other","prop_A","prop_B",
        "n_herbal","n_bio","n_pharm","n_recipes","n_astro","n_unknown",
        "prop_herbal","prop_bio","prop_recipes"

  for (h in total) {
    t = total[h] + 0

    a = A[h] + 0
    b = B[h] + 0
    o = other[h] + 0

    hcount = herb[h] + 0
    bcount = bio[h] + 0
    pcount = pharm[h] + 0
    rcount = rec[h] + 0
    acount = astro[h] + 0
    ucount = unknown[h] + 0

    pa = (t > 0 ? a / t : 0)
    pb = (t > 0 ? b / t : 0)
    ph = (t > 0 ? hcount / t : 0)
    pbio = (t > 0 ? bcount / t : 0)
    prec = (t > 0 ? rcount / t : 0)

    print h,
          t,
          a,b,o,pa,pb,
          hcount,bcount,pcount,rcount,acount,ucount,
          ph,pbio,prec
  }
}
' "$TMP/s49b_folio_hand_currier_section.tsv" > "$SUMMARY"

echo "[S49b] Wrote summary to: $SUMMARY"
