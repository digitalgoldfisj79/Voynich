#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
export BASE

LATIN_SUMMARY="${LATIN_SUMMARY:-$BASE/PhaseS/out/s6_latin_suffix2_summary.tsv}"
VM_TOK_SUMMARY="${VM_TOK_SUMMARY:-$BASE/PhaseS/out/s7_voynich_suffix2_tokens_summary.tsv}"
VM_STEM_SUMMARY="${VM_STEM_SUMMARY:-$BASE/PhaseS/out/s7_voynich_suffix2_stems_summary.tsv}"
OUT_COMPARE="${OUT_COMPARE:-$BASE/PhaseS/out/s7_suffix2_comparison.tsv}"

echo "[S7c] BASE          = $BASE"
echo "[S7c] LATIN_SUMMARY = $LATIN_SUMMARY"
echo "[S7c] VM_TOK_SUMMARY= $VM_TOK_SUMMARY"
echo "[S7c] VM_STEM_SUMMARY= $VM_STEM_SUMMARY"
echo "[S7c] OUT_COMPARE   = $OUT_COMPARE"

python3 "$BASE/scripts/s7_compare_suffix2_profiles.py"
