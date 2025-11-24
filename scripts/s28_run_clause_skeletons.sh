#!/data/data/com.termux/files/usr/bin/bash
set -eu

# Clause skeleton rung (S28)
# Uses recurrent templates from S26 and semantic families from S9b
# to build family-aware clause skeletons.

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN_TEMPLATES="$BASE/PhaseS/out/s26_recurrent_templates.tsv"
STEM_FAMILIES="$BASE/PhaseS/out/s9b_stem_semantic_families.tsv"

OUT_TSV="$BASE/PhaseS/out/s28_clause_skeletons.tsv"
OUT_SUMMARY_TSV="$BASE/PhaseS/out/s28_clause_skeleton_summary.tsv"
OUT_TXT="$BASE/PhaseS/out/s28_clause_skeleton_summary.txt"

echo "[S28] BASE           = $BASE"
echo "[S28] IN_TEMPLATES   = $IN_TEMPLATES"
echo "[S28] STEM_FAMILIES  = $STEM_FAMILIES"
echo "[S28] OUT_TSV        = $OUT_TSV"
echo "[S28] OUT_SUMMARY    = $OUT_SUMMARY_TSV"
echo "[S28] OUT_TXT        = $OUT_TXT"

if [ ! -s "$IN_TEMPLATES" ]; then
  echo "[S28][ERR] Templates file not found or empty: $IN_TEMPLATES" >&2
  exit 1
fi

if [ ! -s "$STEM_FAMILIES" ]; then
  echo "[S28][ERR] Stem families file not found or empty: $STEM_FAMILIES" >&2
  exit 1
fi

python3 "$BASE/scripts/s28_build_clause_skeletons.py" \
  "$IN_TEMPLATES" \
  "$STEM_FAMILIES" \
  "$OUT_TSV" \
  "$OUT_SUMMARY_TSV" \
  "$OUT_TXT"

echo "[S28] Done."
