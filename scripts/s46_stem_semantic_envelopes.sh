#!/usr/bin/env sh
set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
SCRIPTD="$BASE/scripts"

python3 "$SCRIPTD/s46_stem_semantic_envelopes.py"
