#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
cd "$BASE"

echo "[FIX] Patching s21_run_fsmily_frames.sh and s22_run_frame_summary.sh in ./scripts"

# Remove any mv ... .tmp lines from the runners
if [ -f "scripts/s21_run_fsmily_frames.sh" ]; then
  # create a backup once
  cp scripts/s21_run_fsmily_frames.sh scripts/s21_run_fsmily_frames.sh.bak 2>/dev/null || true
  sed -i '/mv .*s21_family_frames.tsv.tmp/d' scripts/s21_run_fsmily_frames.sh
else
  echo "[WARN] scripts/s21_run_fsmily_frames.sh not found"
fi

if [ -f "scripts/s22_run_frame_summary.sh" ]; then
  cp scripts/s22_run_frame_summary.sh scripts/s22_run_frame_summary.sh.bak 2>/dev/null || true
  sed -i '/mv .*s22_frame_summary.tsv.tmp/d' scripts/s22_run_frame_summary.sh
else
  echo "[WARN] scripts/s22_run_frame_summary.sh not found"
fi

echo "[FIX] Done."
