#!/usr/bin/env sh
# S99 – Promote freq-priority T3 selection to canonical t3_lexical_lexicon.tsv
set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
SEL_T3="$BASE/PhaseT/out/t3_lexicon_selected_freq.tsv"
OUT_T3="$BASE/metadata/t3_lexical_lexicon.tsv"

echo "[s99] BASE:   $BASE"
echo "[s99] INPUT:  $SEL_T3"
echo "[s99] OUTPUT: $OUT_T3"

if [ ! -f "$SEL_T3" ]; then
  echo "[s99][ERROR] Missing selected T3 file: $SEL_T3" >&2
  exit 1
fi

# Backup existing lexicon if present
if [ -f "$OUT_T3" ]; then
  TS=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "backup")
  BAK="$OUT_T3.bak.$TS"
  cp "$OUT_T3" "$BAK"
  echo "[s99] Backed up existing lexicon to: $BAK"
fi

python3 - << 'PY'
import os
import pandas as pd

base = os.environ.get("BASE", os.path.join(os.path.expanduser("~"), "Voynich", "Voynich_Reproducible_Core"))
sel_path = os.path.join(base, "PhaseT", "out", "t3_lexicon_selected_freq.tsv")
out_path = os.path.join(base, "metadata", "t3_lexical_lexicon.tsv")

print(f"[s99(py)] Reading selected T3 from: {sel_path}", flush=True)
df = pd.read_csv(sel_path, sep="\t")

# Expected columns in selected file:
# stem, functional_label, lemma_latin, gloss_en, latin_domain,
# confidence, total_score, freq_score, form_score, domain_score,
# spec_score, corpus_freq, note

# Map functional_label → pos
def label_to_pos(label: str) -> str:
    if label.startswith("PROC_"):
        return "V"
    elif label in ("BOT_ENTITY", "BIO_STATE", "ANIM_ENTITY"):
        return "N"
    else:
        return "X"

pos = [label_to_pos(x) for x in df["functional_label"]]

# Build canonical T3 schema
cols = [
    "stem",
    "lemma_latin",
    "gloss_en",
    "pos",
    "confidence",
    "lexical_score",
    "rule_id",
    "evidence",
    "notes",
    "alt1_lemma",
    "alt1_score",
    "alt2_lemma",
    "alt2_score",
    "gap_to_alt1",
    "form_char_cosine",
    "form_edit_similarity",
    "form_combined",
    "form_rank",
    "form_in_corpus",
    "form_semantic_match",
    "form_stem_length",
    "form_corpus_frequency",
    "form_note",
    "form_confidence_effect",
]

out = pd.DataFrame(columns=cols)

out["stem"]              = df["stem"]
out["lemma_latin"]       = df["lemma_latin"]
out["gloss_en"]          = df["gloss_en"]
out["pos"]               = pos
out["confidence"]        = df["confidence"]
out["lexical_score"]     = df["total_score"]
out["rule_id"]           = "R_T3_DOMAIN_FREQ"
out["evidence"]          = "T2,DomainFreq,S80-S83"
out["notes"]             = df["note"].fillna("").replace("nan", "")

# No explicit alternatives at this stage
out["alt1_lemma"]        = ""
out["alt1_score"]        = ""
out["alt2_lemma"]        = ""
out["alt2_score"]        = ""
out["gap_to_alt1"]       = ""

# Form similarity: we only have a single scalar form_score per lemma
out["form_char_cosine"]      = df["form_score"]
out["form_edit_similarity"]  = ""
out["form_combined"]         = df["form_score"]
out["form_rank"]             = ""
out["form_in_corpus"]        = ""
out["form_semantic_match"]   = ""
out["form_stem_length"]      = ""
out["form_corpus_frequency"] = df["corpus_freq"]
out["form_note"]             = "s83_charonly_fixed"
out["form_confidence_effect"]= df["note"].fillna("").replace("nan", "")

print(f"[s99(py)] Writing canonical lexicon to: {out_path}", flush=True)
out.to_csv(out_path, sep="\t", index=False)
print("[s99(py)] Done. Rows:", len(out), flush=True)
PY

echo "[s99] Finished promoting T3 selection to metadata/t3_lexical_lexicon.tsv"
