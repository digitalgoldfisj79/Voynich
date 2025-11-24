#!/usr/bin/env sh
# S94 – Export domain candidates to a curated file for manual editing.

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
SRC="$BASE/metadata/t3_candidates_domains.tsv"
DST="$BASE/metadata/t3_candidates_domains_curated.tsv"

echo "[s94] BASE: $BASE"
echo "[s94] SRC:  $SRC"
echo "[s94] DST:  $DST"

if [ ! -f "$SRC" ]; then
  echo "[s94][ERROR] Missing source candidate file: $SRC" >&2
  exit 1
fi

if [ -f "$DST" ]; then
  backup="${DST}.bak_$(date +%Y%m%d%H%M%S)"
  echo "[s94] Existing curated file found; backing up to: $backup"
  cp "$DST" "$backup"
fi

cp "$SRC" "$DST"
echo "[s94] Copied domain candidates to curated file."
echo "[s94] Now manually edit:"
echo "  $DST"
echo "to prune/adjust lemmas before promotion to T3."
