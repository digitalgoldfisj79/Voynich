#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

echo "[S50] Hand–register cross-matrix (simple join version)"

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseS/out"
TMP="$BASE/PhaseS/tmp"

mkdir -p "$OUTD" "$TMP"

HAND_MAP="$OUTD/hand_map.tsv"
FOLIO_REG_MATRIX="$OUTD/s50_folio_register_matrix.tsv"
HAND_REG_MATRIX="$OUTD/s50_hand_register_matrix.tsv"
HAND_REG_SUMMARY="$OUTD/s50_hand_register_summary.tsv"
HAND_CURR_SUMMARY="$OUTD/s50_hand_currier_summary.tsv"

# --- Sanity checks ---
if [ ! -f "$HAND_MAP" ]; then
  echo "[S50] ERROR: $HAND_MAP not found. Create it with columns: folio<TAB>hand" >&2
  exit 1
fi

if [ ! -f "$FOLIO_REG_MATRIX" ]; then
  echo "[S50] ERROR: $FOLIO_REG_MATRIX not found. Run s50_register_heatmap.sh first." >&2
  exit 1
fi

echo "[S50] Using:"
echo "      hand_map:                $HAND_MAP"
echo "      folio_register_matrix:   $FOLIO_REG_MATRIX"

# --- Prepare sorted copies for join (skip headers) ---
awk 'NR>1 {print $0}' "$HAND_MAP" \
  | sort -k1,1 > "$TMP/s50_hand_map.sorted.tsv"

awk 'NR>1 {print $0}' "$FOLIO_REG_MATRIX" \
  | sort -k1,1 > "$TMP/s50_folio_register_matrix.sorted.tsv"

# --- Join on folio ---
# hand_map: folio hand
# s50_folio_register_matrix: folio total_tokens ... register
# join output: folio hand total_tokens ...
join -t $'\t' -1 1 -2 1 \
  "$TMP/s50_hand_map.sorted.tsv" \
  "$TMP/s50_folio_register_matrix.sorted.tsv" \
  > "$TMP/s50_hand_register_matrix.body.tsv"

# --- Write header for the joined matrix ---
# Ensure this matches the columns in s50_folio_register_matrix.tsv
# s50_folio_register_matrix.tsv header is:
# folio  total_tokens  known_semantic_tokens  proc_tokens  bot_tokens  bio_tokens  other_semantic_tokens  proc_frac  bot_frac  bio_frac  other_frac  dominant_semantic_register  section  currier  register
{
  printf "folio\thand\t"
  # take header from s50_folio_register_matrix.tsv, drop the first "folio"
  awk 'NR==1 {
    for (i=2; i<=NF; i++) {
      printf "%s", $i
      if (i < NF) printf "\t"
    }
    printf "\n"
  }' "$FOLIO_REG_MATRIX"
} > "$HAND_REG_MATRIX"

# Append body
cat "$TMP/s50_hand_register_matrix.body.tsv" >> "$HAND_REG_MATRIX"

echo "[S50] Wrote hand+register matrix to: $HAND_REG_MATRIX"

# --- Build hand × register summary ---
# register is the last column in HAND_REG_MATRIX
awk -F'\t' '
  NR==1 {next}
  {
    hand = $2
    reg  = $NF
    if (reg == "" || reg == "nan") reg = "UNKNOWN"
    key = hand "\t" reg
    count[key]++
  }
  END {
    print "hand\tregister\tn_folios"
    for (k in count) {
      print k "\t" count[k]
    }
  }
' "$HAND_REG_MATRIX" \
  | sort -k1,1 -k2,2 \
  > "$HAND_REG_SUMMARY"

echo "[S50] Wrote hand×register summary to: $HAND_REG_SUMMARY"

# --- Build hand × Currier summary ---
# Currier column in HAND_REG_MATRIX: use header to locate it robustly
currier_col=$(
  awk -F'\t' '
    NR==1 {
      for (i=1; i<=NF; i++) {
        if ($i=="currier") {print i; exit}
      }
    }
  ' "$HAND_REG_MATRIX"
)

if [ -z "${currier_col:-}" ]; then
  echo "[S50] WARNING: no currier column found in $HAND_REG_MATRIX; skipping hand×currier summary" >&2
else
  awk -F'\t' -v ccol="$currier_col" '
    NR==1 {next}
    {
      hand = $2
      cur  = $ccol
      if (cur == "" || cur == "nan") cur = "Unknown"
      key = hand "\t" cur
      count[key]++
    }
    END {
      print "hand\tcurrier\tn_folios"
      for (k in count) {
        print k "\t" count[k]
      }
    }
  ' "$HAND_REG_MATRIX" \
    | sort -k1,1 -k2,2 \
    > "$HAND_CURR_SUMMARY"

  echo "[S50] Wrote hand×currier summary to: $HAND_CURR_SUMMARY"
fi

echo "[S50] Done."
