#!/usr/bin/env sh
# S99 – Summarise T3 lexicon into metadata/t3_summary.txt

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}
LEX="$BASE/metadata/t3_lexical_lexicon.tsv"
OUT="$BASE/metadata/t3_summary.txt"

echo "[s99] BASE: $BASE"
echo "[s99] LEX:  $LEX"
echo "[s99] OUT:  $OUT"

if [ ! -f "$LEX" ]; then
  echo "[s99][ERROR] Missing T3 lexicon file: $LEX" >&2
  exit 1
fi

python - << 'PY'
import csv
import os
from collections import Counter, defaultdict

base = os.environ.get("BASE", "")
lex_path = os.path.join(base, "metadata", "t3_lexical_lexicon.tsv")
out_path = os.path.join(base, "metadata", "t3_summary.txt")

conf_counts = Counter()
lemma_by_stem = defaultdict(list)

with open(lex_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        stem = row.get("stem", "").strip()
        lemma = row.get("lemma_latin", "").strip()
        conf = row.get("confidence", "").strip()

        if conf:
            conf_counts[conf] += 1
        if stem and lemma:
            lemma_by_stem[stem].append(lemma)

with open(out_path, "w", encoding="utf-8") as out:
    out.write("T3 Lexicon Summary\n")
    out.write("==================\n\n")
    out.write("Confidence counts:\n")
    for conf, n in sorted(conf_counts.items()):
        out.write(f"  {conf}: {n}\n")
    out.write("\nLemmas per stem:\n")
    for stem in sorted(lemma_by_stem.keys()):
        uniq = sorted(set(lemma_by_stem[stem]))
        out.write(f"  {stem}: {', '.join(uniq)}\n")

print(f"[s99(py)] Wrote summary to {out_path}")
PY

echo "[s99] Done."
