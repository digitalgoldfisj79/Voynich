#!/usr/bin/env sh
# S91 – Build metadata/t3_candidates_domains.tsv
# from metadata/t2_stem_functional_lexicon.tsv
# and metadata/latin_lemmas_by_domain.tsv

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
  echo "[s91][ERROR] Missing T2 file: $T2_TSV" >&2
  exit 1
fi

if [ ! -f "$LEMMA_TSV" ]; then
  echo "[s91][ERROR] Missing lemma file: $LEMMA_TSV" >&2
  exit 1
fi

python - << 'PY'
import csv
import os

base = os.environ.get("BASE", "")
t2_path    = os.path.join(base, "metadata", "t2_stem_functional_lexicon.tsv")
lemma_path = os.path.join(base, "metadata", "latin_lemmas_by_domain.tsv")
out_path   = os.path.join(base, "metadata", "t3_candidates_domains.tsv.tmp")

# Map T2 -> lemma domains
domain_map = {
    "PROC_VERB":   ["PROC_COOKING", "PROC_MIXING", "PROC_GRINDING", "PROC_ADDING"],
    "BOT_ENTITY":  ["BOT_HERB"],
    "BIO_STATE":   ["BIO_FLUID"],
}

# Load lemmas
lemmas_by_domain = {}
with open(lemma_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        dom = row.get("domain", "").strip()
        if not dom:
            continue
        lemmas_by_domain.setdefault(dom, []).append(row)

# Load T2
t2_rows = []
with open(t2_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        stem = row.get("stem", "").strip()
        flab = row.get("functional_label", "").strip()
        if not stem or not flab:
            continue
        t2_rows.append((stem, flab))

# Build candidates
out_rows = []
seen = set()

for stem, flab in t2_rows:
    domains = domain_map.get(flab, [])
    if not domains:
        continue
    for dom in domains:
        for lem in lemmas_by_domain.get(dom, []):
            lemma = lem.get("lemma", "").strip()
            gloss = lem.get("gloss_en", "").strip()
            freq  = lem.get("frequency", "").strip()
            src   = lem.get("source", "").strip()

            key = (stem, flab, lemma, dom)
            if key in seen:
                continue
            seen.add(key)

            out_rows.append({
                "stem":             stem,
                "functional_label": flab,
                "lemma_latin":      lemma,
                "gloss_en":         gloss,
                "latin_domain":     dom,
                "corpus_freq":      freq,
                "latin_source":     src,
                "candidate_source": "DOMAIN_MATCH_S91",
            })

fieldnames = [
    "stem",
    "functional_label",
    "lemma_latin",
    "gloss_en",
    "latin_domain",
    "corpus_freq",
    "latin_source",
    "candidate_source",
]

with open(out_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
    writer.writeheader()
    for row in out_rows:
        writer.writerow(row)

print(f"[s91(py)] Wrote {len(out_rows)} rows to {out_path}")
PY

# Atomic move
mv "$OUT_TSV.tmp" "$OUT_TSV"
echo "[s91] Done."
