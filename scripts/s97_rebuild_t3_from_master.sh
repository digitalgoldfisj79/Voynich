#!/usr/bin/env sh
# S97 – Wrapper: rebuild T3 lexicon from current metadata/t3_candidates.tsv

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
REBUILD="$BASE/scripts/t3_rebuild.sh"

echo "[s97] BASE:    $BASE"
echo "[s97] REBUILD: $REBUILD"

if [ ! -x "$REBUILD" ]; then
  echo "[s97][ERROR] t3_rebuild.sh not found or not executable: $REBUILD" >&2
  exit 1
fi

"$REBUILD"
echo "[s97] T3 rebuild completed."
