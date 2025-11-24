#!/bin/sh

set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
IN="$BASE/corpora/voynich_transliteration.txt"
CORE="$BASE/corpora/p6_voynich_tokens.txt"
OUTD="$BASE/PhaseS/out"
OUT="$OUTD/p6_folio_tokens.tsv"

mkdir -p "$OUTD"

# Temp
TMP="$(mktemp "$OUTD/tmp_s0.XXXXXX")"

# 1. Build unfiltered token stream
awk -v OFS='\t' '
  BEGIN {
    folio="NA"; line=0;
  }
  /^<f[0-9rv]+>/ {
    # e.g. <f20v>
    folio = gensub(/^<|>$/,"","g",$0);
    line=0;
    next;
  }
  /^[[:space:]]*$/ { next; }

  {
    line++;
    # split field into tokens separated by periods
    n = split($0, a, /\./);
    for (i=1;i<=n;i++) {
      tok = a[i];
      # ignore empty or metadata tokens such as </>
      if (tok ~ /^[[:alnum:]]+$/) {
        pos++;
        print tok, folio, line, pos;
      }
    }
  }
' "$IN" > "$TMP"

# 2. Filter using core token universe
sort "$CORE" > "$OUTD/core.set"

awk -F'\t' '
  NR==FNR { core[$1]=1; next }
  $1 in core
' "$OUTD/core.set" "$TMP" > "$OUT"

rm -f "$TMP"

echo "[s0] Built clean canonical folio-token file:"
echo "     $OUT"
