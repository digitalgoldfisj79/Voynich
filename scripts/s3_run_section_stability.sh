#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN_FOLIOS="$BASE/PhaseS/out/s1_folio_structural_vectors.tsv"
IN_SECTIONS="$BASE/PhaseS/out/s2_section_structural_summary.tsv"

OUT_PATH="$BASE/PhaseS/out/s3_section_stability.tsv"

echo "[S3] BASE        = $BASE"
echo "[S3] IN_FOLIOS   = $IN_FOLIOS"
echo "[S3] IN_SECTIONS = $IN_SECTIONS"
echo "[S3] OUT_PATH    = $OUT_PATH"

python3 "$BASE/scripts/s3_build_section_stability.py" \
    "$IN_FOLIOS" "$IN_SECTIONS" "$OUT_PATH"
