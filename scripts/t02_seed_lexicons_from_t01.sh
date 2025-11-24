#!/usr/bin/env bash
#
# t02_seed_lexicons_from_t01.sh
#
# Seed stem_lexicon.tsv and suffix_lexicon.tsv from:
#   PhaseT/out/t01_translations.tsv (new compiler output)
#   PhaseS/out/s46_stem_semantic_envelopes.tsv (semantic families)
#
# This OVERWRITES metadata/stem_lexicon.tsv and metadata/suffix_lexicon.tsv

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "${SCRIPT_DIR}/.." && pwd)"

OUTD="${BASE}/PhaseT/out"
T01="${OUTD}/t01_translations.tsv"
S46="${BASE}/PhaseS/out/s46_stem_semantic_envelopes.tsv"

STEM_LEX="${BASE}/metadata/stem_lexicon.tsv"
SUFFIX_LEX="${BASE}/metadata/suffix_lexicon.tsv"

echo "[t02] BASE:       ${BASE}"
echo "[t02] T01:        ${T01}"
echo "[t02] S46:        ${S46}"
echo "[t02] STEM_LEX:   ${STEM_LEX}"
echo "[t02] SUFFIX_LEX: ${SUFFIX_LEX}"

if [ ! -s "${T01}" ]; then
  echo "[t02][ERROR] Missing or empty ${T01} – run t01_compile_translations.sh first." >&2
  exit 1
fi

if [ ! -s "${S46}" ]; then
  echo "[t02][WARN] Missing or empty ${S46}; stem semantic hints will be limited." >&2
fi

mkdir -p "${BASE}/metadata"

export T01 S46 STEM_LEX SUFFIX_LEX

python3 << 'PY'
import os
from pathlib import Path
import pandas as pd

T01 = Path(os.environ["T01"])
S46 = Path(os.environ["S46"])
STEM_LEX = Path(os.environ["STEM_LEX"])
SUFFIX_LEX = Path(os.environ["SUFFIX_LEX"])

print(f"[t02] (py) Loading t01 translations from {T01}")
df = pd.read_csv(T01, sep="\t", dtype=str)

needed_cols = {"stem", "suffix", "register"}
missing = needed_cols - set(df.columns)
if missing:
  raise ValueError(f"[t02] t01_translations.tsv missing columns: {missing}")

# Clean basics
for col in ["stem", "suffix", "register"]:
  df[col] = df[col].fillna("")

# ---------- Load S46 if available ----------
if S46.is_file() and S46.stat().st_size > 0:
  print(f"[t02] (py) Loading S46 semantic envelopes from {S46}")
  df_s46 = pd.read_csv(S46, sep="\t", dtype=str)
  if "token" in df_s46.columns and "stem" not in df_s46.columns:
    df_s46 = df_s46.rename(columns={"token": "stem"})
  for col in ["stem", "semantic_family", "role_group", "primary_section", "structural_class"]:
    if col not in df_s46.columns:
      df_s46[col] = None
  s46_core = df_s46[["stem", "semantic_family", "role_group", "primary_section", "structural_class"]].drop_duplicates()
else:
  print("[t02] (py) S46 not available; no semantic hints will be merged.")
  s46_core = pd.DataFrame(columns=["stem", "semantic_family", "role_group", "primary_section", "structural_class"])

# ============================================================
# 1) STEM LEXICON
# ============================================================

print("[t02] (py) Building stem lexicon…")
stems = (
  df[["stem", "register"]]
  .dropna()
  .query("stem != '' and register != ''")
  .drop_duplicates()
  .copy()
)

print(f"[t02] (py) Unique (stem, register) pairs: {len(stems)}")

# Merge semantic hints from S46
stems = stems.merge(s46_core, on="stem", how="left")

def make_notes(row):
  parts = []
  if isinstance(row.get("semantic_family"), str) and row["semantic_family"]:
    parts.append(f"family={row['semantic_family']}")
  if isinstance(row.get("role_group"), str) and row["role_group"]:
    parts.append(f"role_group={row['role_group']}")
  if isinstance(row.get("primary_section"), str) and row["primary_section"]:
    parts.append(f"primary_section={row['primary_section']}")
  if isinstance(row.get("structural_class"), str) and row["structural_class"]:
    parts.append(f"struct={row['structural_class']}")
  return ";".join(parts) if parts else ""

stems["gloss"] = ""  # you will fill this
stems["notes"] = stems.apply(make_notes, axis=1)

stem_cols = [
  "stem",
  "register",           # REGISTER_A / REGISTER_B
  "gloss",              # to be filled by you
  "notes",              # auto-hints from S46
  "semantic_family",
  "role_group",
  "primary_section",
  "structural_class",
]

stems_out = stems[stem_cols].sort_values(["stem", "register"], kind="mergesort")
stems_out.to_csv(STEM_LEX, sep="\t", index=False)
print(f"[t02] (py) Wrote {len(stems_out)} stem rows to {STEM_LEX}")

# ============================================================
# 2) SUFFIX LEXICON
# ============================================================

print("[t02] (py) Building suffix lexicon…")
sufs = (
  df[["suffix", "register"]]
  .dropna()
  .query("suffix != '' and register != ''")
  .drop_duplicates()
  .copy()
)

print(f"[t02] (py) Unique (suffix, register) pairs: {len(sufs)}")

sufs["role"] = ""          # e.g. INF_VERB / RESULT / ADJ_QUALIFIER etc.
sufs["pos_tag"] = ""       # e.g. V / N / ADJ
sufs["english_affix"] = "" # e.g. "to <STEM>", "<STEM>-like", "multiple <STEM>"
sufs["notes"] = ""         # you can add hints manually or later via another script

suf_cols = [
  "suffix",
  "register",
  "role",
  "pos_tag",
  "english_affix",
  "notes",
]

sufs_out = sufs[suf_cols].sort_values(["suffix", "register"], kind="mergesort")
sufs_out.to_csv(SUFFIX_LEX, sep="\t", index=False)
print(f"[t02] (py) Wrote {len(sufs_out)} suffix rows to {SUFFIX_LEX}")

print("[t02] (py) Done.")
PY

echo "[t02] Done."
