#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$PWD}"
IN_LATIN_MAT="$BASE/corpora/latin_tokens_materia.txt"
OUT="$BASE/PhaseT/out/s83_charonly_fixed.tsv"

echo "[s83] Computing char-only similarity (FIXED - 30 per stem)..."

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

stems = [
    ('qotar', 'PROC_VERB'),
    ('okar', 'PROC_VERB'),
    ('kar', 'BOT_ENTITY'),
    ('ol', 'BIO_STATE'),
]

with open(out_path, 'w') as f:
    f.write("stem\tlabel\tlatin_token\tchar_cosine\n")
    
    for stem, label in stems:
        print(f"[s83] Processing {stem}...", file=sys.stderr)
        
        stem_results = []
        for latin in latin_tokens:
            sim = char_cosine(stem, latin)
            stem_results.append((latin, sim))
        
        stem_results.sort(key=lambda x: -x[1])
        
        # Write top 30 for THIS stem
        for latin, sim in stem_results[:30]:
            f.write(f"{stem}\t{label}\t{latin}\t{sim:.4f}\n")

print("[s83] Done", file=sys.stderr)

PY

echo ""
echo "=== qotar top 10 ==="
grep "^qotar" "$OUT" | head -10

echo ""
echo "=== qotar contains coqui? ==="
grep "^qotar.*coqu" "$OUT" || echo "(none found)"

echo ""
echo "=== kar contains ruta? ==="
grep "^kar.*ruta" "$OUT" || echo "(none found)"

echo ""
echo "=== ol top 10 ==="
grep "^ol" "$OUT" | head -10

