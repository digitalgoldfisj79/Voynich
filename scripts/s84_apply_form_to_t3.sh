#!/usr/bin/env bash
# s84_apply_form_to_t3.sh
# Post-process T3 lexicon to:
#  - add form-similarity metadata (from s80–s83 manual stats)
#  - apply confidence constraints based on form support
#  - enforce "one lemma per (lemma,pos) cluster" rule
#
# Uses ONLY hard-coded scores for the handful of key stems
# (qotar, okar, kar, ol, ar) derived from s80–s83. No SciPy, no extra deps.

set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
IN_T3="$BASE/metadata/t3_lexical_lexicon.tsv"
OUT_TMP="$BASE/metadata/t3_lexical_lexicon.tsv.s84.tmp"

if [ ! -f "$IN_T3" ]; then
  echo "[s84] ERROR: input T3 lexicon not found: $IN_T3" >&2
  exit 1
fi

echo "[s84] BASE:   $BASE"
echo "[s84] IN_T3:  $IN_T3"
echo "[s84] OUT:    $OUT_TMP"

python3 - "$IN_T3" "$OUT_TMP" << 'PYEOF'
import sys, csv, math

in_path, out_path = sys.argv[1], sys.argv[2]

# ---------------------------------------------------------------------
# 1. Hard-coded form similarity info derived from s80–s83
#    (You measured these already; we’re just encoding the results.)
#
# combined_score is approx (char_cosine + edit_similarity)/2
# rank is approximate rank among Latin tokens for that stem.
# ---------------------------------------------------------------------

FORM_INFO = [
    # qotar – cooking verb, coquo family
    {
        "stem": "qotar",
        "lemma_latin": "coquo",
        "char_cosine": 0.5071,
        "edit_similarity": 0.2000,
        "combined_score": 0.3536,
        "rank": 158,
        "in_corpus": "0",   # base lemma not in tokens
        "semantic_match": "1",
        "stem_length": 5,
        "corpus_frequency": 0,
        "note": "dictionary_form_absent"
    },
    {
        "stem": "qotar",
        "lemma_latin": "coquitur",
        "char_cosine": 0.5657,
        "edit_similarity": 0.2500,
        "combined_score": 0.4078,
        "rank": 92,
        "in_corpus": "1",
        "semantic_match": "1",
        "stem_length": 5,
        "corpus_frequency": 17,
        "note": "inflected_form_penalty"
    },

    # okar – competing cooking verb, weaker form support
    {
        "stem": "okar",
        "lemma_latin": "coquo",
        "char_cosine": 0.3780,
        "edit_similarity": 0.2000,
        "combined_score": 0.2890,
        "rank": 240,
        "in_corpus": "0",
        "semantic_match": "1",
        "stem_length": 4,
        "corpus_frequency": 0,
        "note": "secondary_candidate_in_coquo_family"
    },

    # kar – botanical entity, ruta family
    {
        "stem": "kar",
        "lemma_latin": "ruta",
        "char_cosine": 0.5774,
        "edit_similarity": 0.2500,
        "combined_score": 0.4137,
        "rank": 78,
        "in_corpus": "1",
        "semantic_match": "1",
        "stem_length": 3,
        "corpus_frequency": 52,
        "note": "short_stem_moderate_match"
    },

    # ol – fluid/ole- family (this one actually benefits from form)
    {
        "stem": "ol",
        "lemma_latin": "ole",
        "char_cosine": 0.8165,
        "edit_similarity": 0.6667,
        "combined_score": 0.7416,
        "rank": 12,
        "in_corpus": "1",
        "semantic_match": "1",
        "stem_length": 2,
        "corpus_frequency": 38,
        "note": "short_stem_strong_match"
    },

    # ar – burning verb, uro family
    {
        "stem": "ar",
        "lemma_latin": "uro",
        "char_cosine": 0.4500,
        "edit_similarity": 0.2000,
        "combined_score": 0.3250,
        "rank": 140,
        "in_corpus": "1",
        "semantic_match": "1",
        "stem_length": 2,
        "corpus_frequency": 20,
        "note": "form_support_weak"
    },
]

form_index = {}
for rec in FORM_INFO:
    key = (rec["stem"], rec["lemma_latin"])
    form_index[key] = rec

# ---------------------------------------------------------------------
# 2. Confidence levels and utility
# ---------------------------------------------------------------------
CONFIDENCE_LEVELS = ["HIGH", "MEDIUM-HIGH", "MEDIUM", "LOW-MEDIUM", "LOW", "DEMOTED"]

def cap_confidence(current, max_level):
    """Cap confidence string at max_level based on CONFIDENCE_LEVELS order."""
    if current not in CONFIDENCE_LEVELS or max_level not in CONFIDENCE_LEVELS:
        return current
    if CONFIDENCE_LEVELS.index(current) < CONFIDENCE_LEVELS.index(max_level):
        return max_level
    return current

# ---------------------------------------------------------------------
# 3. Load T3 lexicon
# ---------------------------------------------------------------------
with open(in_path, "r", encoding="utf-8") as f_in:
    reader = csv.DictReader(f_in, delimiter="\t")
    rows = list(reader)
    fieldnames = list(reader.fieldnames) if reader.fieldnames else []

# New metadata columns if not already present
new_cols = [
    "form_char_cosine",
    "form_edit_similarity",
    "form_combined",
    "form_rank",
    "form_in_corpus",
    "form_semantic_match",
    "form_stem_length",
    "form_corpus_frequency",
    "form_note",
    "form_confidence_effect"
]

for col in new_cols:
    if col not in fieldnames:
        fieldnames.append(col)

# ---------------------------------------------------------------------
# 4. Attach form info + apply confidence constraints
# ---------------------------------------------------------------------
for row in rows:
    stem = row.get("stem", "")
    lemma = row.get("lemma_latin", "")
    key = (stem, lemma)

    rec = form_index.get(key)
    effects = []

    if rec is None:
        # No specific form data: neutral defaults
        row["form_char_cosine"]      = ""
        row["form_edit_similarity"]  = ""
        row["form_combined"]         = ""
        row["form_rank"]             = ""
        row["form_in_corpus"]        = ""
        row["form_semantic_match"]   = ""
        row["form_stem_length"]      = str(len(stem)) if stem else ""
        row["form_corpus_frequency"] = ""
        row["form_note"]             = "no_specific_form_data"
        # No confidence change
        row["form_confidence_effect"] = "NONE"
        continue

    # Fill in the numeric / metadata fields
    row["form_char_cosine"]      = f"{rec['char_cosine']:.4f}"
    row["form_edit_similarity"]  = f"{rec['edit_similarity']:.4f}"
    row["form_combined"]         = f"{rec['combined_score']:.4f}"
    row["form_rank"]             = str(rec["rank"])
    row["form_in_corpus"]        = rec["in_corpus"]
    row["form_semantic_match"]   = rec["semantic_match"]
    row["form_stem_length"]      = str(rec["stem_length"])
    row["form_corpus_frequency"] = str(rec["corpus_frequency"])
    row["form_note"]             = rec["note"]

    form_combined = rec["combined_score"]
    stem_len = rec["stem_length"]
    conf = row.get("confidence", "").strip() or "MEDIUM"

    # --- Confidence rules ---
    # 1. Boost for very short stems with strong form support
    if stem_len <= 2 and form_combined >= 0.75:
        # Only boost up to MEDIUM-HIGH
        if conf in ["MEDIUM", "LOW-MEDIUM", "LOW"]:
            conf = "MEDIUM-HIGH"
            effects.append("BOOST:short_stem_strong_form")
    # 2. Downgrade when form support is weak
    elif form_combined < 0.60:
        # Cap at MEDIUM
        new_conf = cap_confidence(conf, "MEDIUM")
        if new_conf != conf:
            effects.append("DOWNGRADE:form_combined<0.60")
        conf = new_conf

        # If very weak (<0.50), cap at LOW-MEDIUM
        if form_combined < 0.50:
            new_conf2 = cap_confidence(conf, "LOW-MEDIUM")
            if new_conf2 != conf:
                effects.append("DOWNGRADE:form_combined<0.50")
            conf = new_conf2

    row["confidence"] = conf
    row["form_confidence_effect"] = ";".join(effects) if effects else "NONE"

# ---------------------------------------------------------------------
# 5. "One lemma per cluster" rule:
#    group by (lemma_latin, pos) and keep only highest lexical_score as non-DEMOTED
# ---------------------------------------------------------------------
# Build cluster index
clusters = {}
for idx, row in enumerate(rows):
    lemma = row.get("lemma_latin", "")
    pos   = row.get("pos", "")
    key   = (lemma, pos)
    clusters.setdefault(key, []).append(idx)

for key, idxs in clusters.items():
    # Consider only clusters with >1 entry
    if len(idxs) <= 1:
        continue

    # Filter to those not already DEMOTED
    active = [i for i in idxs if rows[i].get("confidence", "") != "DEMOTED"]
    if len(active) <= 1:
        continue

    # Choose winner by lexical_score
    def get_lex_score(i):
        try:
            return float(rows[i].get("lexical_score", "") or 0.0)
        except ValueError:
            return 0.0

    best_idx = max(active, key=get_lex_score)
    best_stem = rows[best_idx].get("stem", "")

    for i in active:
        if i == best_idx:
            continue
        # Demote competitor
        rows[i]["confidence"] = "DEMOTED"
        note_old = rows[i].get("notes", "").strip()
        extra = f"demoted: competing stem for lemma={key[0]}, pos={key[1]}; primary_stem={best_stem}"
        rows[i]["notes"] = (note_old + "; " + extra).strip("; ")

# ---------------------------------------------------------------------
# 6. Write out updated TSV
# ---------------------------------------------------------------------
with open(out_path, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

PYEOF

# Atomic move with backup
if [ -f "$OUT_TMP" ]; then
  cp "$IN_T3" "$IN_T3.bak.s84" 2>/dev/null || true
  mv "$OUT_TMP" "$IN_T3"
  echo "[s84] Updated T3 lexicon written to: $IN_T3"
else
  echo "[s84] ERROR: expected tmp output not found: $OUT_TMP" >&2
  exit 1
fi
