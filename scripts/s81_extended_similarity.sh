#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$PWD}"
IN_T2="$BASE/metadata/t2_stem_functional_lexicon.tsv"
IN_LATIN_TAC="$BASE/corpora/latin_tokens.txt"
IN_LATIN_MAT="$BASE/corpora/latin_tokens_materia.txt"
OUT="$BASE/PhaseT/out/s81_extended_form_similarity.tsv"

echo "[s81] Computing EXTENDED form similarity (top 30)..."

mkdir -p "$BASE/PhaseT/out"

python3 - "$IN_T2" "$IN_LATIN_TAC" "$IN_LATIN_MAT" "$OUT" << 'PY'
import sys, math
from collections import Counter
import pandas as pd

in_t2, in_latin_tac, in_latin_mat, out_path = sys.argv[1:5]

def char_cosine_similarity(word1, word2):
    chars1 = Counter(word1.lower())
    chars2 = Counter(word2.lower())
    all_chars = set(chars1.keys()) | set(chars2.keys())
    vec1 = [chars1.get(c, 0) for c in all_chars]
    vec2 = [chars2.get(c, 0) for c in all_chars]
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    mag1 = math.sqrt(sum(v**2 for v in vec1))
    mag2 = math.sqrt(sum(v**2 for v in vec2))
    return dot_product / (mag1 * mag2) if mag1 and mag2 else 0

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def normalized_edit_similarity(word1, word2):
    distance = levenshtein_distance(word1, word2)
    max_len = max(len(word1), len(word2))
    return 1 - (distance / max_len) if max_len > 0 else 0

print("[s81(py)] Loading data...", file=sys.stderr)
t2 = pd.read_csv(in_t2, sep="\t")
stems_to_match = t2[['stem', 'functional_label']].values

with open(in_latin_tac, 'r') as f:
    latin_tac = [line.strip() for line in f if line.strip()]
with open(in_latin_mat, 'r') as f:
    latin_mat = [line.strip() for line in f if line.strip()]

latin_all = list(set(latin_tac + latin_mat))
print(f"[s81(py)] Loaded {len(latin_all)} unique Latin tokens", file=sys.stderr)

results = []

# Only process key stems
key_stems = ['qotar', 'okar', 'kar', 'ol']

for stem, func_label in stems_to_match:
    if stem not in key_stems:
        continue
        
    print(f"[s81(py)] Processing: {stem}", file=sys.stderr)
    
    stem_results = []
    for latin_word in latin_all:
        if len(latin_word) < 2:
            continue
            
        char_sim = char_cosine_similarity(stem, latin_word)
        edit_sim = normalized_edit_similarity(stem, latin_word)
        avg_sim = (char_sim + edit_sim) / 2
        
        stem_results.append({
            'voynich_stem': stem,
            'functional_label': func_label,
            'latin_token': latin_word,
            'char_cosine': round(char_sim, 4),
            'edit_similarity': round(edit_sim, 4),
            'avg_similarity': round(avg_sim, 4)
        })
    
    stem_results.sort(key=lambda x: x['avg_similarity'], reverse=True)
    results.extend(stem_results[:30])  # Top 30 instead of 10

df_results = pd.DataFrame(results)
df_results = df_results.sort_values(['voynich_stem', 'avg_similarity'], ascending=[True, False])

df_results.to_csv(out_path, sep="\t", index=False)
print(f"[s81(py)] Wrote {len(df_results)} similarity scores", file=sys.stderr)

PY

echo "[s81] Done. Now searching for coquo-family words..."

# Search for coquo-family in results
echo ""
echo "=== qotar matches containing 'coqu' ==="
grep "qotar.*coqu" "$OUT" || echo "(none found)"

echo ""
echo "=== okar matches containing 'coqu' ==="
grep "okar.*coqu" "$OUT" || echo "(none found)"

echo ""
echo "=== kar matches containing 'rut' ==="
grep "kar.*rut" "$OUT" || echo "(none found)"

echo ""
echo "=== ol matches containing 'ole' or 'hum' ==="
grep -E "^ol.*(ole|hum)" "$OUT" || echo "(none found)"

