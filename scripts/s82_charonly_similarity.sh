#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$PWD}"
IN_LATIN_MAT="$BASE/corpora/latin_tokens_materia.txt"
OUT="$BASE/PhaseT/out/s82_charonly_similarity.tsv"

echo "[s82] Computing similarity using character cosine ONLY..."

python3 - "$IN_LATIN_MAT" "$OUT" << 'PY'
import sys, math
from collections import Counter

in_latin, out_path = sys.argv[1], sys.argv[2]

def char_cosine(w1, w2):
    c1, c2 = Counter(w1.lower()), Counter(w2.lower())
    all_chars = set(c1.keys()) | set(c2.keys())
    vec1 = [c1.get(c, 0) for c in all_chars]
    vec2 = [c2.get(c, 0) for c in all_chars]
    dot = sum(v1*v2 for v1, v2 in zip(vec1, vec2))
    mag1 = math.sqrt(sum(v**2 for v in vec1))
    mag2 = math.sqrt(sum(v**2 for v in vec2))
    return dot / (mag1 * mag2) if mag1 and mag2 else 0

with open(in_latin, 'r') as f:
    latin_tokens = [line.strip() for line in f if line.strip() and len(line.strip()) >= 3]

print(f"[s82] Loaded {len(latin_tokens)} Latin tokens", file=sys.stderr)

stems = [
    ('qotar', 'PROC_VERB'),
    ('okar', 'PROC_VERB'),
    ('kar', 'BOT_ENTITY'),
    ('ol', 'BIO_STATE'),
]

results = []
for stem, label in stems:
    for latin in latin_tokens:
        sim = char_cosine(stem, latin)
        results.append({
            'stem': stem,
            'label': label,
            'latin': latin,
            'char_cosine': round(sim, 4)
        })

results.sort(key=lambda x: (x['stem'], -x['char_cosine']))

with open(out_path, 'w') as f:
    f.write("stem\tlabel\tlatin_token\tchar_cosine\n")
    for r in results[:120]:  # Top 30 per stem
        f.write(f"{r['stem']}\t{r['label']}\t{r['latin']}\t{r['char_cosine']}\n")

print(f"[s82] Wrote results to {out_path}", file=sys.stderr)

PY

echo ""
echo "=== Top 15 matches for qotar (char_cosine only) ==="
grep "^qotar" "$OUT" | head -15

echo ""
echo "=== Looking for coquo-family in qotar matches ==="
grep "^qotar.*coqu" "$OUT" | head -10 || echo "(none found)"

echo ""
echo "=== Looking for ruta in kar matches ==="
grep "^kar.*rut" "$OUT" | head -10 || echo "(none found)"

