#!/usr/bin/env sh
set -eu

HAND_MAP="PhaseS/out/hand_map.tsv"
REG_MATRIX="PhaseS/out/s50_folio_register_matrix.tsv"
OUT="PhaseS/out/s50_hand_currier_summary.tsv"

echo "[S50c] Hand–Currier summary"
echo "[S50c] HAND_MAP:    $HAND_MAP"
echo "[S50c] REG_MATRIX:  $REG_MATRIX"

if [ ! -s "$HAND_MAP" ]; then
  echo "[S50c] ERROR: hand map not found or empty: $HAND_MAP" >&2
  exit 1
fi

if [ ! -s "$REG_MATRIX" ]; then
  echo "[S50c] ERROR: register matrix not found or empty: $REG_MATRIX" >&2
  exit 1
fi

awk -F'\t' '
  # First file: hand_map.tsv → build folio→hand map
  NR == FNR {
    if (FNR == 1) next  # skip header
    folio = $1
    hand  = $2
    gsub(/^[ \t\r]+|[ \t\r]+$/, "", folio)
    gsub(/^[ \t\r]+|[ \t\r]+$/, "", hand)
    if (folio != "" && hand != "")
      folio2hand[folio] = hand
    next
  }

  # Second file: s50_folio_register_matrix.tsv
  FNR == 1 {
    # detect currier column
    currier_col = 0
    for (i = 1; i <= NF; i++) {
      col = $i
      gsub(/^[ \t\r]+|[ \t\r]+$/, "", col)
      lc = tolower(col)
      if (lc == "currier") currier_col = i
    }
    if (!currier_col) {
      print "[S50c] ERROR: could not locate currier column in header" > "/dev/stderr"
      for (i = 1; i <= NF; i++) {
        printf "  [%d] \"%s\"\n", i, $i > "/dev/stderr"
      }
      exit 1
    }
    next
  }

  {
    folio = $1
    cur   = $currier_col

    gsub(/^[ \t\r]+|[ \t\r]+$/, "", folio)
    gsub(/^[ \t\r]+|[ \t\r]+$/, "", cur)

    if (folio == "") next

    if (cur == "" || cur == "nan") cur = "Unknown"

    hand = "Unknown"
    if (folio in folio2hand) {
      hand = folio2hand[folio]
    }

    key = hand "\t" cur
    cnt[key]++
  }

  END {
    print "hand\tcurrier\tn_folios"
    for (k in cnt) {
      split(k, a, "\t")
      printf "%s\t%s\t%d\n", a[1], a[2], cnt[k]
    }
  }
' "$HAND_MAP" "$REG_MATRIX" \
  | sort -k1,1 -k2,2 \
  > "$OUT"

echo "[S50c] Wrote $OUT"
