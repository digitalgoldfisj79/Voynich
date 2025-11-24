#!/usr/bin/env sh
# S91 – Generate T3 domain-based candidate lemmas for each T2 stem.
# Inputs:
#   metadata/t2_stem_functional_lexicon.tsv
#   metadata/latin_lemmas_by_domain.tsv
# Output:
#   metadata/t3_candidates_domains.tsv

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}

T2_TSV="$BASE/metadata/t2_stem_functional_lexicon.tsv"
LEMMA_TSV="$BASE/metadata/latin_lemmas_by_domain.tsv"
OUT_TSV="$BASE/metadata/t3_candidates_domains.tsv"

echo "[s91] BASE:      $BASE"
echo "[s91] T2_TSV:    $T2_TSV"
echo "[s91] LEMMA_TSV: $LEMMA_TSV"
echo "[s91] OUT_TSV:   $OUT_TSV"

if [ ! -f "$T2_TSV" ]; then
  echo "[s91][ERROR] Missing T2 lexicon: $T2_TSV" >&2
  exit 1
fi

if [ ! -f "$LEMMA_TSV" ]; then
  echo "[s91][ERROR] Missing domain lemmas: $LEMMA_TSV" >&2
  exit 1
fi

python3 - << 'PY'
import os
import sys
import pandas as pd

base = os.environ.get("BASE", os.path.join(os.path.expanduser("~"), "Voynich", "Voynich_Reproducible_Core"))
t2_path    = os.path.join(base, "metadata", "t2_stem_functional_lexicon.tsv")
lemma_path = os.path.join(base, "metadata", "latin_lemmas_by_domain.tsv")
out_path   = os.path.join(base, "metadata", "t3_candidates_domains.tsv")

print(f"[s91(py)] Loading T2 from: {t2_path}")
t2 = pd.read_csv(t2_path, sep="\t")

expected_t2_cols = {"stem", "functional_label", "confidence", "rule_id", "evidence", "notes"}
missing_t2 = expected_t2_cols - set(t2.columns)
if missing_t2:
    print(f"[s91(py)][ERROR] T2 missing columns: {missing_t2}", file=sys.stderr)
    sys.exit(1)

print(f"[s91(py)] Loading lemma domains from: {lemma_path}")
lemmas = pd.read_csv(lemma_path, sep="\t")

expected_lemma_cols = {"domain", "lemma", "gloss_en", "frequency", "source"}
missing_lemma = expected_lemma_cols - set(lemmas.columns)
if missing_lemma:
    print(f"[s91(py)][ERROR] lemma table missing columns: {missing_lemma}", file=sys.stderr)
    sys.exit(1)

# Map functional_label -> list of latin domains
domain_map = {
    "PROC_VERB":  ["PROC_COOKING", "PROC_MIXING", "PROC_GRINDING", "PROC_ADDING"],
    "BOT_ENTITY": ["BOT_HERB"],
    "BIO_STATE":  ["BIO_FLUID"],
    # You can extend later, e.g.:
    # "ANIM_ENTITY": ["ANIM"],
}

rows = []
n_stems = 0
n_candidates = 0

for _, t2_row in t2.iterrows():
    stem = str(t2_row["stem"])
    func = str(t2_row["functional_label"])
    domains = domain_map.get(func, [])

    if not domains:
        # Skip functional labels we don't yet map
        continue

    # Subset lemma table to those domains
    subset = lemmas[lemmas["domain"].isin(domains)].copy()
    if subset.empty:
        continue

    # For now, we just take ALL lemmas in those domains as potential candidates.
    # You can later filter by frequency, etc.
    for _, lem_row in subset.iterrows():
        rows.append({
            "stem":             stem,
            "functional_label": func,
            "lemma_latin":      str(lem_row["lemma"]),
            "gloss_en":         str(lem_row["gloss_en"]),
            "latin_domain":     str(lem_row["domain"]),
            "corpus_freq":      int(lem_row["frequency"]),
            "latin_source":     str(lem_row["source"]),
            "candidate_source": "DOMAIN_MATCH_S91",
        })
        n_candidates += 1

    n_stems += 1

if not rows:
    print("[s91(py)] WARNING: No candidates generated – check domain_map & inputs.")
    # Still write an empty table with header for reproducibility
    cols = [
        "stem",
        "functional_label",
        "lemma_latin",
        "gloss_en",
        "latin_domain",
        "corpus_freq",
        "latin_source",
        "candidate_source",
    ]
    pd.DataFrame(columns=cols).to_csv(out_path, sep="\t", index=False)
    print(f"[s91(py)] Wrote EMPTY candidate file to {out_path}")
    sys.exit(0)

out_df = pd.DataFrame(rows)
# Sort for stable diffs: by stem, then latin_domain, then lemma_latin
out_df = out_df.sort_values(["stem", "latin_domain", "lemma_latin"]).reset_index(drop=True)

print(f"[s91(py)] Generated candidates for {out_df['stem'].nunique()} stems.")
print(f"[s91(py)] Total candidate rows: {len(out_df)}")

out_df.to_csv(out_path, sep="\t", index=False)
print(f"[s91(py)] Wrote domain-based candidates to: {out_path}")
PY

echo "[s91] Done."
