#!/usr/bin/env sh
set -eu

# Base repo
BASE="$HOME/Voynich/Voynich_Reproducible_Core"
OUTD="$BASE/PhaseS/out"
IN="$OUTD/s50_folio_register_matrix.tsv"
OUT="$OUTD/s50_hand_currier_summary.tsv"

echo "[S50b] Hand–Currier summary from s50_folio_register_matrix.tsv"
echo "[S50b] IN:  $IN"
echo "[S50b] OUT: $OUT"

if [ ! -s "$IN" ]; then
  echo "[S50b] ERROR: input file not found or empty: $IN" >&2
  exit 1
fi

awk -F'\t' '
  NR == 1 {
    for (i = 1; i <= NF; i++) {
      if ($i == "hand")    hcol = i;
      if ($i == "currier") ccol = i;
    }
    if (!hcol || !ccol) {
      printf "[S50b] ERROR: missing required columns hand/currier in header\n" > "/dev/stderr";
      exit 1;
    }
    next;
  }
  {
    hand = $hcol;
    cur  = $ccol;

    # skip empty or weird rows
    if (hand == "" || hand == "hand") next;
    if (cur == ""  || cur == "currier" || cur == "nan") cur = "Unknown";

    key = hand "\t" cur;
    cnt[key]++;
  }
  END {
    print "hand\tcurrier\tn_folios";
    for (k in cnt) {
      split(k, a, "\t");
      printf "%s\t%s\t%d\n", a[1], a[2], cnt[k];
    }
  }
' "$IN" \
  | sort -k1,1 -k2,2 \
  > "${OUT}.tmp"

mv "${OUT}.tmp" "$OUT"
echo "[S50b] Wrote hand–Currier summary to $OUT"
