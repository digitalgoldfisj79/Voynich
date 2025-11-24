#!/data/data/com.termux/files/usr/bin/sh
set -eu

echo "[S52] Block boundaries and transitions"

# 1) Force BASE to the Reproducible_Core repo, ignore any old BASE
BASE="$PWD"
if [ ! -d "$BASE/PhaseS/out" ]; then
  BASE="$HOME/Voynich/Voynich_Reproducible_Core"
fi

OUTD="$BASE/PhaseS/out"

REG_MATRIX="$OUTD/s50_folio_register_matrix.tsv"
HAND_MAP="$OUTD/hand_map.tsv"

OUT_SEQ="$OUTD/s52_folio_sequence.tsv"
OUT_BLOCKS="$OUTD/s52_blocks.tsv"
OUT_TRANS="$OUTD/s52_transitions.tsv"

echo "[S52] BASE:        $BASE"
echo "[S52] REG_MATRIX:  $REG_MATRIX"
echo "[S52] HAND_MAP:    $HAND_MAP"
echo "[S52] OUT_SEQ:     $OUT_SEQ"
echo "[S52] OUT_BLOCKS:  $OUT_BLOCKS"
echo "[S52] OUT_TRANS:   $OUT_TRANS"

# Sanity checks
if [ ! -s "$REG_MATRIX" ]; then
  echo "[S52] ERROR: missing or empty $REG_MATRIX" >&2
  exit 1
fi

if [ ! -s "$HAND_MAP" ]; then
  echo "[S52] ERROR: missing or empty $HAND_MAP" >&2
  exit 1
fi

python3 - "$REG_MATRIX" "$HAND_MAP" "$OUT_SEQ" "$OUT_BLOCKS" "$OUT_TRANS" << 'PYEOF'
import sys
from pathlib import Path
import pandas as pd
from collections import Counter

reg_path = Path(sys.argv[1])
hand_path = Path(sys.argv[2])
seq_out_path = Path(sys.argv[3])
blocks_out_path = Path(sys.argv[4])
trans_out_path = Path(sys.argv[5])

print(f"[S52] Python: loading {reg_path} and {hand_path}", file=sys.stderr)

reg = pd.read_csv(reg_path, sep="\t")
if "folio" not in reg.columns:
    raise SystemExit("[S52] ERROR: 'folio' column missing in s50_folio_register_matrix.tsv")

reg["order"] = range(len(reg))

hand = pd.read_csv(hand_path, sep="\t")
if not {"folio", "hand"}.issubset(hand.columns):
    raise SystemExit("[S52] ERROR: 'folio'/'hand' missing in hand_map.tsv")

df = reg.merge(hand, on="folio", how="left")
df = df.sort_values("order").reset_index(drop=True)

for col in ["hand", "section", "currier", "register", "dominant_semantic_register"]:
    if col not in df.columns:
        raise SystemExit(f"[S52] ERROR: required column '{col}' missing in s50_folio_register_matrix.tsv")
    df[col] = df[col].fillna("Unknown")

seq_cols = ["folio", "hand", "section", "currier", "register", "dominant_semantic_register"]
seq_df = df[seq_cols].copy()
seq_df.to_csv(seq_out_path, sep="\t", index=False)
print(f"[S52] Wrote folio sequence to: {seq_out_path}", file=sys.stderr)

blocks = []
block_id = 0
current_key = None
current_block = None

for _, row in df.iterrows():
    folio = row["folio"]
    hand_val = str(row["hand"])
    section_val = str(row["section"])
    currier_val = str(row["currier"])
    register_val = str(row["register"])
    semreg = str(row["dominant_semantic_register"])

    key = (hand_val, currier_val, section_val, register_val)

    if current_key is None or key != current_key:
        if current_block is not None:
            cnt = current_block["semreg_counter"]
            if cnt:
                mc = cnt.most_common()
                if len(mc) == 1:
                    block_semreg = mc[0][0]
                else:
                    block_semreg = "MIXED" if mc[0][1] == mc[1][1] else mc[0][0]
            else:
                block_semreg = "Unknown"
            current_block["dominant_semantic_register"] = block_semreg
            del current_block["semreg_counter"]
            blocks.append(current_block)

        block_id += 1
        current_key = key
        current_block = {
            "block_id": block_id,
            "start_folio": folio,
            "end_folio": folio,
            "n_folios": 1,
            "hand": hand_val,
            "currier": currier_val,
            "section": section_val,
            "register": register_val,
            "semreg_counter": Counter([semreg]),
        }
    else:
        current_block["end_folio"] = folio
        current_block["n_folios"] += 1
        current_block["semreg_counter"][semreg] += 1

if current_block is not None:
    cnt = current_block["semreg_counter"]
    if cnt:
        mc = cnt.most_common()
        if len(mc) == 1:
            block_semreg = mc[0][0]
        else:
            block_semreg = "MIXED" if mc[0][1] == mc[1][1] else mc[0][0]
    else:
        block_semreg = "Unknown"
    current_block["dominant_semantic_register"] = block_semreg
    del current_block["semreg_counter"]
    blocks.append(current_block)

blocks_df = pd.DataFrame(blocks, columns=[
    "block_id",
    "start_folio",
    "end_folio",
    "n_folios",
    "hand",
    "currier",
    "section",
    "register",
    "dominant_semantic_register",
])
blocks_df.to_csv(blocks_out_path, sep="\t", index=False)
print(f"[S52] Wrote blocks to: {blocks_out_path}", file=sys.stderr)

transitions = []
prev = None
for _, row in df.iterrows():
    if prev is not None:
        transitions.append({
            "from_folio": prev["folio"],
            "to_folio": row["folio"],
            "from_hand": str(prev["hand"]),
            "to_hand": str(row["hand"]),
            "from_currier": str(prev["currier"]),
            "to_currier": str(row["currier"]),
            "from_section": str(prev["section"]),
            "to_section": str(row["section"]),
            "from_register": str(prev["register"]),
            "to_register": str(row["register"]),
            "from_semreg": str(prev["dominant_semantic_register"]),
            "to_semreg": str(row["dominant_semantic_register"]),
        })
    prev = row

trans_df = pd.DataFrame(transitions, columns=[
    "from_folio",
    "to_folio",
    "from_hand",
    "to_hand",
    "from_currier",
    "to_currier",
    "from_section",
    "to_section",
    "from_register",
    "to_register",
    "from_semreg",
    "to_semreg",
])
trans_df.to_csv(trans_out_path, sep="\t", index=False)
print(f"[S52] Wrote transitions to: {trans_out_path}", file=sys.stderr)
PYEOF

echo "[S52] Done."
