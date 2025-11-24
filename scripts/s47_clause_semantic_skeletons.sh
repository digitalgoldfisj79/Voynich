#!/usr/bin/env sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
SCRIPTD="$BASE/scripts"

python3 "$SCRIPTD/s47_clause_semantic_skeletons.py"
