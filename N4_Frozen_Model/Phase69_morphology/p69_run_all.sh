#!/usr/bin/env bash
set -euo pipefail
OUT="$HOME/Voynich/Phase69/out"
LOG="$OUT/p69_run.log"
: > "$LOG"

RULES="$HOME/Voynich/Phase67p/out/p67p_rules_compact.tsv"
SEGS="$HOME/Voynich/Phase58/out/p58_segments.tsv"

echo "== Phase 69 pipeline start ==" | tee -a "$LOG"
echo "rules: $RULES" | tee -a "$LOG"
echo "segs:  $SEGS"  | tee -a "$LOG"

# Preflight
test -s "$RULES" || { echo "[ERR] missing $RULES" | tee -a "$LOG"; exit 1; }
test -s "$SEGS"  || { echo "[ERR] missing $SEGS"  | tee -a "$LOG"; exit 1; }

echo "== Python check ==" | tee -a "$LOG"
python3 - <<'PY' | tee -a "$LOG"
import sys
print("python:", sys.version.split()[0])
try:
    import numpy as np
    print("numpy:", np.__version__, "ok:", np.array([1,2,3]).sum()==6)
except Exception as e:
    print("[WARN] numpy issue:", e)
PY

# Validate & freeze
"$HOME/Voynich/Phase69/scripts/p69_validate.py" 2>&1 | tee -a "$LOG"

# Heads
echo "== Head: summary ==" | tee -a "$LOG"
sed -n '1,160p' "$OUT/p69_summary.json" | tee -a "$LOG"
echo "== Head: doc ==" | tee -a "$LOG"
sed -n '1,80p' "$OUT/p69_doc.md" | tee -a "$LOG"
echo "[ok] Phase 69 complete. See $LOG" | tee -a "$LOG"
