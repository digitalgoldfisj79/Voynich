#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
BASE="$HOME/Voynich/Voynich_Reproducible_Core"

echo "[t3_rebuild] Running s84..."
$BASE/scripts/s84_merge_form_similarity.sh

echo "[t3_rebuild] Running t3_score_candidates..."
python3 $BASE/scripts/t3_score_candidates.py

echo "[t3_rebuild] Done."
