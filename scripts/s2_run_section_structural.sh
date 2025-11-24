#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

IN_PATH="${IN_PATH:-$BASE/PhaseS/out/s1_folio_structural_vectors.tsv}"
OUT_SUMMARY="${OUT_SUMMARY:-$BASE/PhaseS/out/s2_section_structural_summary.tsv}"
OUT_DISTS="${OUT_DISTS:-$BASE/PhaseS/out/s2_section_centroid_distances.tsv}"

echo "[S2] BASE        = $BASE"
echo "[S2] IN_PATH     = $IN_PATH"
echo "[S2] OUT_SUMMARY = $OUT_SUMMARY"
echo "[S2] OUT_DISTS   = $OUT_DISTS"

python3 "$BASE/scripts/s2_section_structural_summary.py"
