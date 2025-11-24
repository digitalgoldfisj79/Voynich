#!/usr/bin/env sh
# S95 – Promote curated domain candidates to metadata/t3_candidates.tsv

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
CURATED="$BASE/metadata/t3_candidates_domains_curated.tsv"
MASTER="$BASE/metadata/t3_candidates.tsv"

echo "[s95] BASE:    $BASE"
echo "[s95] CURATED: $CURATED"
echo "[s95] MASTER:  $MASTER"

if [ ! -f "$CURATED" ]; then
  echo "[s95][ERROR] Missing curated file: $CURATED" >&2
  exit 1
fi

if [ -f "$MASTER" ]; then
  backup="${MASTER}.bak_$(date +%Y%m%d%H%M%S)"
  echo "[s95] Existing master candidate file found; backing up to: $backup"
  cp "$MASTER" "$backup"
fi

cp "$CURATED" "$MASTER"
echo "[s95] Promoted curated domain candidates to master t3_candidates.tsv."
