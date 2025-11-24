#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

CORE_PATH="$BASE/PhaseS/out/s13_semantic_core_report.tsv"
# Default to the *folio-aware* token file
TOKENS_PATH="${TOKENS_PATH:-$BASE/PhaseS/out/p6_folio_tokens.tsv}"
OUT_PATH="$BASE/PhaseS/out/s20_core_context_windows.tsv"

echo "[S20] BASE        = $BASE"
echo "[S20] CORE_PATH   = $CORE_PATH"
echo "[S20] TOKENS_PATH = $TOKENS_PATH"
echo "[S20] OUT_PATH    = $OUT_PATH"

python3 "$BASE/scripts/s20_build_core_context_windows.py" \
  "$CORE_PATH" "$TOKENS_PATH" "$OUT_PATH"
