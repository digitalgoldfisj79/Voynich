#!/usr/bin/env sh
# S98 – Pretty-print the current T3 lexical lexicon

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
LEX="$BASE/metadata/t3_lexical_lexicon.tsv"

echo "[s98] BASE: $BASE"
echo "[s98] LEX:  $LEX"

if [ ! -f "$LEX" ]; then
  echo "[s98][ERROR] Missing T3 lexicon file: $LEX" >&2
  exit 1
fi

column -t -s "$(printf '\t')" "$LEX" | head -n 40
