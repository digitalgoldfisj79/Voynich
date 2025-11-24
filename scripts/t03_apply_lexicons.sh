#!/usr/bin/env sh
# t03_apply_lexicons.sh
# Enrich t01 translations with stem/suffix lexicon info, POS tags, and simple valency hints.

set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseT/out"
T01="$OUTD/t01_translations.tsv"
STEM_LEX="$BASE/metadata/stem_lexicon.tsv"
SUFFIX_LEX="$BASE/metadata/suffix_lexicon.tsv"
OUT_ENRICHED="$OUTD/t03_enriched_translations.tsv"

echo "[t03] BASE:        $BASE"
echo "[t03] T01:         $T01"
echo "[t03] STEM_LEX:    $STEM_LEX"
echo "[t03] SUFFIX_LEX:  $SUFFIX_LEX"
echo "[t03] OUT_ENRICHED:$OUT_ENRICHED"

if [ ! -s "$T01" ]; then
  echo "[t03][ERROR] Missing or empty $T01 – run t01_compile_translations.sh first." >&2
  exit 1
fi

if [ ! -s "$STEM_LEX" ] || [ ! -s "$SUFFIX_LEX" ]; then
  echo "[t03][ERROR] Missing stem/suffix lexicons – run t02_seed_lexicons_from_t01.sh and/or t10_update_lexicons_from_S57_S58_S59.sh first." >&2
  exit 1
fi

mkdir -p "$OUTD"

python3 - << 'PYCODE'
import pandas as pd
import os

BASE = os.environ.get("BASE")
OUTD = os.path.join(BASE, "PhaseT", "out")
T01 = os.path.join(OUTD, "t01_translations.tsv")
STEM_LEX = os.path.join(BASE, "metadata", "stem_lexicon.tsv")
SUFFIX_LEX = os.path.join(BASE, "metadata", "suffix_lexicon.tsv")
OUT_ENRICHED = os.path.join(OUTD, "t03_enriched_translations.tsv")

print("[t03] (py) BASE =", BASE)
print("[t03] (py) Loading t01 translations from", T01)
df = pd.read_csv(T01, sep="\t")

print("[t03] (py) Rows in t01:", len(df))

# Defensive: ensure required columns exist
required_cols = ["folio_norm", "folio", "line", "pos", "section", "currier",
                 "register", "dominant_semantic_register",
                 "token", "stem", "suffix",
                 "semantic_family", "role_group",
                 "structural_class", "positional_role_label",
                 "best_position", "gloss", "role",
                 "english_affix", "english_phrase"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError("[t03] Missing columns in t01_translations.tsv: " + ",".join(missing))

# Load lexicons
print("[t03] (py) Loading stem lexicon from", STEM_LEX)
stem_lex = pd.read_csv(STEM_LEX, sep="\t")

print("[t03] (py) Loading suffix lexicon from", SUFFIX_LEX)
suf_lex = pd.read_csv(SUFFIX_LEX, sep="\t")

# Normalise keys
for col in ["stem", "register"]:
    if col in stem_lex.columns:
        stem_lex[col] = stem_lex[col].astype(str)
for col in ["suffix", "register"]:
    if col in suf_lex.columns:
        suf_lex[col] = suf_lex[col].astype(str)

df["stem"] = df["stem"].astype(str)
df["suffix"] = df["suffix"].astype(str)
df["register"] = df["register"].astype(str)

# Merge stem lexicon (on stem + register)
stem_key_cols = [c for c in ["stem", "register"] if c in stem_lex.columns]
merge_cols_stem = [c for c in stem_lex.columns if c not in stem_key_cols]

if stem_key_cols:
    print("[t03] (py) Merging stem lexicon on", stem_key_cols)
    df = df.merge(stem_lex, on=stem_key_cols, how="left", suffixes=("", "_stemlex"))
else:
    print("[t03] (py) WARNING: stem_lexicon has no usable stem/register keys – skipping merge.")

# Merge suffix lexicon (on suffix + register)
suf_key_cols = [c for c in ["suffix", "register"] if c in suf_lex.columns]
if suf_key_cols:
    print("[t03] (py) Merging suffix lexicon on", suf_key_cols)
    df = df.merge(suf_lex, on=suf_key_cols, how="left", suffixes=("", "_suflex"))
else:
    print("[t03] (py) WARNING: suffix_lexicon has no usable suffix/register keys – skipping merge.")

# POS tagging heuristic
def infer_pos(row):
    # If lexicon already has pos_tag, prefer that
    for col in ["pos_tag", "pos_tag_stemlex"]:
        if col in row and isinstance(row[col], str) and row[col].strip():
            return row[col]
    role_group = str(row.get("role_group", "")).upper()
    if "PROC" in role_group:
        return "VERB"
    if "BOT" in role_group or "BIO" in role_group:
        return "NOUN"
    if "PARTICLE" in role_group:
        return "PART"
    return "X"

df["pos_tag"] = df.apply(infer_pos, axis=1)

# Valency hint heuristic – we map from stem_lex if present, else UNKNOWN
if "valency_hint" not in df.columns:
    df["valency_hint"] = ""

# Register bias – if lexicon has it, propagate; otherwise just copy from stem_lex
if "register_bias" not in df.columns and "register_bias" in stem_lex.columns:
    # After merge above, register_bias lives as a column already
    pass

# Build english_token from stem_gloss + suffix_english_affix if available
stem_gloss_cols = [c for c in ["stem_gloss", "stem_gloss_stemlex"] if c in df.columns]
suffix_aff_cols = [c for c in ["suffix_english_affix", "suffix_english_affix_suflex", "english_affix"] if c in df.columns]

def build_english_token(row):
    stem_gloss = ""
    for c in stem_gloss_cols:
        val = row.get(c, "")
        if isinstance(val, str) and val.strip():
            stem_gloss = val.strip()
            break
    suff = ""
    for c in suffix_aff_cols:
        val = row.get(c, "")
        if isinstance(val, str) and val.strip():
            suff = val.strip()
            break
    # Fall back to existing english_phrase if nothing else
    if stem_gloss and suff:
        return stem_gloss + suff
    if stem_gloss:
        return stem_gloss
    if isinstance(row.get("english_phrase"), str):
        return row["english_phrase"]
    return ""

df["english_token"] = df.apply(build_english_token, axis=1)

print("[t03] (py) Final columns:", list(df.columns))
print("[t03] (py) Writing enriched translations to", OUT_ENRICHED)
df.to_csv(OUT_ENRICHED, sep="\t", index=False)
print("[t03] (py) Done.")
PYCODE

echo "[t03] Done."
