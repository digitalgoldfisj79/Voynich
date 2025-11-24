#!/usr/bin/env bash
set -eu

# S15 – Semantic system summary (core families + gates)

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"

IN_S13="$BASE/PhaseS/out/s13_semantic_core_report.tsv"
IN_S14="$BASE/PhaseS/out/s14_semantic_system_gate.tsv"

OUT_TSV="$BASE/PhaseS/out/s15_semantic_system_summary.tsv"
OUT_TXT="$BASE/PhaseS/out/s15_semantic_system_summary.txt"

echo "[S15] BASE     = $BASE"
echo "[S15] IN_S13   = $IN_S13"
echo "[S15] IN_S14   = $IN_S14"
echo "[S15] OUT_TSV  = $OUT_TSV"
echo "[S15] OUT_TXT  = $OUT_TXT"

if [ ! -f "$IN_S13" ]; then
  echo "[S15] ERROR: missing S13 core report TSV at: $IN_S13" >&2
  exit 1
fi

if [ ! -f "$IN_S14" ]; then
  echo "[S15] ERROR: missing S14 gate TSV at: $IN_S14" >&2
  exit 1
fi

python3 "$BASE/scripts/s15_build_semantic_system_summary.py" \
  "$IN_S13" \
  "$IN_S14" \
  "$OUT_TSV" \
  "$OUT_TXT"

echo "[S15] Done."
