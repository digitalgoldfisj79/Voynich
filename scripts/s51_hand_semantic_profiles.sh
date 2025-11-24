#!/bin/sh
# S51 — Hand-level semantic profiles (PROC/BOT/BIO) from s50_folio_register_matrix + hand_map

set -e

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
OUTD="$BASE/PhaseS/out"

REGM="$OUTD/s50_folio_register_matrix.tsv"
HANDMAP="$OUTD/hand_map.tsv"
OUT="$OUTD/s51_hand_semantic_profiles.tsv"

echo "[S51] Hand-level semantic profiles (from s50_folio_register_matrix)"
echo "[S51] BASE:      $BASE"
echo "[S51] OUTD:      $OUTD"
echo "[S51] REGM:      $REGM"
echo "[S51] HAND_MAP:  $HANDMAP"
echo "[S51] OUT_S51:   $OUT"

# QC: ensure inputs exist and are non-empty
for f in "$REGM" "$HANDMAP"; do
    if [ ! -s "$f" ]; then
        echo "[S51] ERROR: missing or empty input: $f"
        exit 1
    fi
done

python3 << 'PYEOF'
import os
import pandas as pd

BASE = os.path.join(os.environ["HOME"], "Voynich", "Voynich_Reproducible_Core")
OUTD = os.path.join(BASE, "PhaseS", "out")

regm_path  = os.path.join(OUTD, "s50_folio_register_matrix.tsv")
hand_path  = os.path.join(OUTD, "hand_map.tsv")
out_path   = os.path.join(OUTD, "s51_hand_semantic_profiles.tsv")

reg = pd.read_csv(regm_path, sep="\t")
hm  = pd.read_csv(hand_path, sep="\t")

# reg: must have folio,total_tokens,known_semantic_tokens,proc_tokens,bot_tokens,bio_tokens,...
# hm:  folio,hand

df = reg.merge(hm, on="folio", how="left")

# Drop folios with no hand assigned (just in case)
df = df.dropna(subset=["hand"])

grouped = df.groupby("hand").agg(
    n_folios=("folio", "nunique"),
    total_tokens=("total_tokens", "sum"),
    known_semantic_tokens=("known_semantic_tokens", "sum"),
    proc_tokens=("proc_tokens", "sum"),
    bot_tokens=("bot_tokens", "sum"),
    bio_tokens=("bio_tokens", "sum"),
)

# Avoid division by zero
known = grouped["known_semantic_tokens"].replace(0, 1)

grouped["proc_frac"] = grouped["proc_tokens"] / known
grouped["bot_frac"]  = grouped["bot_tokens"]  / known
grouped["bio_frac"]  = grouped["bio_tokens"]  / known

def dominant(row):
    if row["proc_frac"] > 0.5:
        return "PROC_DOM"
    if row["bot_frac"] > 0.5:
        return "BOT_DOM"
    if row["bio_frac"] > 0.5:
        return "BIO_DOM"
    return "MIXED"

grouped["dominant_semantic_register"] = grouped.apply(dominant, axis=1)

grouped.reset_index().to_csv(out_path, sep="\t", index=False)
PYEOF

echo "[S51] Wrote: $OUT"
