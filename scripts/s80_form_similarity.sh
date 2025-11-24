#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$PWD}"

IN_T2="$BASE/metadata/t2_stem_functional_lexicon.tsv"
IN_LATIN_TAC="$BASE/corpora/latin_tokens.txt"
IN_LATIN_MAT="$BASE/corpora/latin_tokens_materia.txt"
OUT="$BASE/PhaseT/out/s80_form_similarity.tsv"

echo "[s80] Computing form similarity for T3 candidates..."
echo "[s80] IN_T2: $IN_T2"
echo "[s80] IN_LATIN: $IN_LATIN_TAC, $IN_LATIN_MAT"
echo "[s80] OUT: $OUT"

if [ ! -f "$IN_T2" ]; then
  echo "[s80] ERROR: T2 file not found: $IN_T2" >&2
  exit 1
fi

if [ ! -f "$IN_LATIN_TAC" ]; then
  echo "[s80] ERROR: Latin file not found: $IN_LATIN_TAC" >&2
  exit 1
fi

if [ ! -f "$IN_LATIN_MAT" ]; then
  echo "[s80] ERROR: Latin file not found: $IN_LATIN_MAT" >&2
  exit 1
fi

mkdir -p "$BASE/PhaseT/out"

python3 - "$IN_T2" "$IN_LATIN_TAC" "$IN_LATIN_MAT" "$OUT" << 'PY'
import sys
import math
from collections import Counter
import pandas as pd

# Get arguments
in_t2 = sys.argv[1]
in_latin_tac = sys.argv[2]
in_latin_mat = sys.argv[3]
out_path = sys.argv[4]

def char_cosine_similarity(word1, word2):
    """Compute cosine similarity of character frequency vectors."""
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
    """Compute edit distance."""
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
    """Normalized similarity."""
    distance = levenshtein_distance(word1, word2)
    max_len = max(len(word1), len(word2))
    return 1 - (distance / max_len) if max_len > 0 else 0

# Load T2 stems
print("[s80(py)] Loading T2 stems...", file=sys.stderr)
t2 = pd.read_csv(in_t2, sep="\t")
stems_to_match = t2[['stem', 'functional_label']].values

# Load Latin tokens (simple text files, one token per line)
print("[s80(py)] Loading Latin tokens...", file=sys.stderr)
with open(in_latin_tac, 'r', encoding='utf-8') as f:
    latin_tac = [line.strip() for line in f if line.strip()]

with open(in_latin_mat, 'r', encoding='utf-8') as f:
    latin_mat = [line.strip() for line in f if line.strip()]

# Combine and deduplicate
latin_all = list(set(latin_tac + latin_mat))
print(f"[s80(py)] Loaded {len(latin_all)} unique Latin tokens", file=sys.stderr)

# For each T2 stem, find top Latin matches
results = []

for stem, func_label in stems_to_match:
    print(f"[s80(py)] Processing stem: {stem} ({func_label})", file=sys.stderr)
    
    # Skip very short stems (problematic matches)
    if len(stem) < 2:
        print(f"[s80(py)]   Skipping (too short)", file=sys.stderr)
        continue
    
    # Compute similarities
    stem_results = []
    for latin_word in latin_all:
        # Skip very short Latin words
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
    
    # Sort by avg_similarity and keep top 10
    stem_results.sort(key=lambda x: x['avg_similarity'], reverse=True)
    results.extend(stem_results[:10])

# Convert to DataFrame
df_results = pd.DataFrame(results)

# Sort by stem and similarity
df_results = df_results.sort_values(
    ['voynich_stem', 'avg_similarity'], 
    ascending=[True, False]
)

# Write output
df_results.to_csv(out_path, sep="\t", index=False)
print(f"[s80(py)] Wrote {len(df_results)} similarity scores to {out_path}", file=sys.stderr)

PY

echo "[s80] Done."
