#!/usr/bin/env sh
#
# s42_master_currier_AB.sh
#
# End-to-end Currier A/B valency pipeline:
#  - Build C-files from master transliteration for all Currier A and B folios
#  - Run S41b suffix-level valency scan for each folio
#  - Run S42 summary for each folio
#  - Merge ALL A and ALL B with S42c
#  - Compare merged A vs B with S42b
#
# Usage:
#   BASE="$HOME/Voynich/Voynich_Reproducible_Core" \
#     ./scripts/s42_master_currier_AB.sh
#

set -eu

# ---- 0. Base paths ----

if [ "${BASE-}" = "" ]; then
  echo "[err] BASE is not set. Example:" >&2
  echo "  BASE=\$HOME/Voynich/Voynich_Reproducible_Core \\" >&2
  echo "    ./scripts/s42_master_currier_AB.sh" >&2
  exit 1
fi

MASTER="$BASE/corpora/voynich_transliteration.txt"
LADDER="$BASE/PhaseS/out/s39_valency_ladder.tsv"
ACFG="$BASE/PhaseS/config/currierA_folios.list"
BCFG="$BASE/PhaseS/config/currierB_folios.list"

if [ ! -f "$MASTER" ]; then
  echo "[err] master transliteration not found: $MASTER" >&2
  exit 1
fi
if [ ! -f "$LADDER" ]; then
  echo "[err] s39 valency ladder not found: $LADDER" >&2
  exit 1
fi
if [ ! -f "$ACFG" ]; then
  echo "[err] Currier A list not found: $ACFG" >&2
  exit 1
fi
if [ ! -f "$BCFG" ]; then
  echo "[err] Currier B list not found: $BCFG" >&2
  exit 1
fi

OUTD="$BASE/PhaseS/out"
IND="$BASE/PhaseS/in"
mkdir -p "$OUTD" "$IND"

# ---- 1. Build C-files for all A & B folios ----

echo "[s42-master] Building C-files for Currier A folios..."
A_FOLIOS=$(awk 'NF>0 {printf "%s ", $1}' "$ACFG")

"$BASE/scripts/s00_build_folio_C_from_master.sh" \
  "$MASTER" \
  $A_FOLIOS

echo "[s42-master] Building C-files for Currier B folios..."
B_FOLIOS=$(awk 'NF>0 {printf "%s ", $1}' "$BCFG")

"$BASE/scripts/s00_build_folio_C_from_master.sh" \
  "$MASTER" \
  $B_FOLIOS

# ---- 2. Run S41b on all A & B ----

echo "[s42-master] Running S41b on Currier A folios..."
while read F; do
  [ -z "$F" ] && continue
  CFILE="$IND/${F}_C.txt"
  if [ ! -f "$CFILE" ]; then
    echo "[warn] missing C-file for $F: $CFILE" >&2
    continue
  fi
  echo "  [S41b-A] $F"
  BASE="$BASE" \
    "$BASE/scripts/s41b_scan_folio_valency_suffix.sh" \
      "$CFILE" \
      "$LADDER"
done < "$ACFG"

echo "[s42-master] Running S41b on Currier B folios..."
while read F; do
  [ -z "$F" ] && continue
  CFILE="$IND/${F}_C.txt"
  if [ ! -f "$CFILE" ]; then
    echo "[warn] missing C-file for $F: $CFILE" >&2
    continue
  fi
  echo "  [S41b-B] $F"
  BASE="$BASE" \
    "$BASE/scripts/s41b_scan_folio_valency_suffix.sh" \
      "$CFILE" \
      "$LADDER"
done < "$BCFG"

# ---- 3. Run S42 summaries for all A & B ----

echo "[s42-master] Running S42 summaries for Currier A folios..."
while read F; do
  [ -z "$F" ] && continue
  HITS="$OUTD/s41b_valency_suffix_hits_${F}.tsv"
  if [ ! -f "$HITS" ]; then
    echo "[warn] missing S41b hits for $F: $HITS" >&2
    continue
  fi
  echo "  [S42-A] $F"
  BASE="$BASE" \
    "$BASE/scripts/s42_valency_suffix_summary.sh" \
      "$HITS" \
      > "$OUTD/s42_valency_suffix_summary_${F}.tsv"
done < "$ACFG"

echo "[s42-master] Running S42 summaries for Currier B folios..."
while read F; do
  [ -z "$F" ] && continue
  HITS="$OUTD/s41b_valency_suffix_hits_${F}.tsv"
  if [ ! -f "$HITS" ]; then
    echo "[warn] missing S41b hits for $F: $HITS" >&2
    continue
  fi
  echo "  [S42-B] $F"
  BASE="$BASE" \
    "$BASE/scripts/s42_valency_suffix_summary.sh" \
      "$HITS" \
      > "$OUTD/s42_valency_suffix_summary_${F}.tsv"
done < "$BCFG"

# ---- 4. Merge ALL A and ALL B with S42c ----

echo "[s42-master] Merging ALL Currier A folios with S42c..."
A_TSVS=$(awk -v outd="$OUTD" 'NF>0 {printf "%s/s42_valency_suffix_summary_%s.tsv ", outd, $1}' "$ACFG")

BASE="$BASE" \
  "$BASE/scripts/s42c_merge_valency_suffix.sh" \
    $A_TSVS \
    > "$OUTD/s42_valency_suffix_summary_ALL_A_merged.tsv"

echo "[s42-master] Merging ALL Currier B folios with S42c..."
B_TSVS=$(awk -v outd="$OUTD" 'NF>0 {printf "%s/s42_valency_suffix_summary_%s.tsv ", outd, $1}' "$BCFG")

BASE="$BASE" \
  "$BASE/scripts/s42c_merge_valency_suffix.sh" \
    $B_TSVS \
    > "$OUTD/s42_valency_suffix_summary_ALL_B_merged.tsv"

# ---- 5. Compare ALL B vs ALL A with S42b ----

echo "[s42-master] Comparing ALL_B vs ALL_A with S42b..."
"$BASE/scripts/s42b_compare_valency_suffix.sh" \
  "$OUTD/s42_valency_suffix_summary_ALL_B_merged.tsv" \
  "$OUTD/s42_valency_suffix_summary_ALL_A_merged.tsv" \
  > "$OUTD/s42b_compare_ALL_B_vs_ALL_A.tsv"

echo "[s42-master] Done."
echo "  Merged A: $OUTD/s42_valency_suffix_summary_ALL_A_merged.tsv"
echo "  Merged B: $OUTD/s42_valency_suffix_summary_ALL_B_merged.tsv"
echo "  Compare : $OUTD/s42b_compare_ALL_B_vs_ALL_A.tsv"
