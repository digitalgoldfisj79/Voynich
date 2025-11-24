#!/usr/bin/env bash
# patch_s20_s21_s22_tokens.sh
# Termux-safe patch: switch s6_folio_tokens.tsv → p6_folio_tokens.tsv
# in the s20 / s21 / s22 runner scripts.

set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
SCRIPTD="$BASE/scripts"

echo "[PATCH] BASE = $BASE"
echo "[PATCH] SCRIPTD = $SCRIPTD"

# Scripts we want to patch (only if they exist)
FILES="
s20_run_core_context_windows.sh
s21_run_fsmily_frames.sh
s22_run_frame_summary.sh
"

timestamp="$(date +%Y%m%d_%H%M%S)"

for fname in $FILES; do
  f="$SCRIPTD/$fname"
  if [ -f "$f" ]; then
    echo "[PATCH] Patching $fname"

    # Backup
    backup="${f}.bak.${timestamp}"
    cp "$f" "$backup"
    echo "        Backup -> $backup"

    # Termux/POSIX-safe in-place replace: create temp and move back
    tmp="${f}.tmp.$$"
    # Replace all literal occurrences of s6_folio_tokens.tsv → p6_folio_tokens.tsv
    sed 's/s6_folio_tokens\.tsv/p6_folio_tokens.tsv/g' "$f" > "$tmp"

    mv "$tmp" "$f"
    chmod +x "$f"
  else
    echo "[PATCH] Skipping $fname (not found)"
  fi
done

echo "[PATCH] Done."
