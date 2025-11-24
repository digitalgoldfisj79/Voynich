#!/usr/bin/env sh
set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
T4="$BASE/PhaseT/out/t4_tokens_with_t3.tsv"

echo "[t110] BASE: $BASE"
echo "[t110] T4:   $T4"

python3 - << 'PY'
import pandas as pd

T4 = r"""'"'"'""" + r"""{T4_PLACEHOLDER}""" + r"""'"'"'"""  # placeholder
PY
