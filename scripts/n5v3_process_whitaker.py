#!/usr/bin/env python3
"""
Process Whitaker lemmas into tokenized format
Extract suffix/prefix patterns from the 31k lemmas
"""

import pandas as pd
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
WHITAKER = BASE / "corpora/latin_vocab/whitaker_lemmas.tsv"
OUTPUT = BASE / "corpora/romance_tokenized"

print("="*80)
print("PROCESSING WHITAKER LATIN LEMMAS")
print("="*80)

# Load Whitaker
df = pd.read_csv(WHITAKER, sep='\t')
df = df.dropna(subset=['lemma'])
df = df[df['lemma'].str.match(r'^[a-z]{2,15}$', na=False)]

lemmas = df['lemma'].tolist()
print(f"\nWhitaker lemmas: {len(lemmas)}")

# Latin suffixes (common endings)
LATIN_ENDINGS = ['us', 'um', 'is', 'os', 'as', 'am', 'em', 'im',
                 'are', 'ere', 'ire', 'or', 'ur', 'at', 'et', 'it',
                 'o', 'a', 'e', 'i', 'ae', 'ei', 'orum', 'arum']

def simple_stem(word, endings):
    """Remove Latin ending to get stem"""
    for ending in sorted(endings, key=len, reverse=True):
        if word.endswith(ending) and len(word) > len(ending) + 2:
            return word[:-len(ending)], ending
    return word, ''

# Extract stems and affixes
stems = []
suffixes = Counter()
prefixes = Counter()

for lemma in lemmas:
    stem, suffix = simple_stem(lemma, LATIN_ENDINGS)
    
    stems.append(stem)
    
    if suffix:
        suffixes[suffix] += 1
    
    # Prefix patterns
    if len(stem) >= 2:
        prefixes[stem[:2]] += 1
    if len(stem) >= 3:
        prefixes[stem[:3]] += 1

unique_stems = list(set(stems))

print(f"Unique stems: {len(unique_stems)}")
print(f"Suffix types: {len(suffixes)}")
print(f"Prefix patterns: {len(prefixes)}")

# Save
OUTPUT.mkdir(exist_ok=True)

# Stems
stem_file = OUTPUT / "latin_stems.txt"
stem_file.write_text('\n'.join(unique_stems))
print(f"\n✓ Saved stems: {stem_file}")

# Suffixes
suffix_file = OUTPUT / "latin_suffixes.tsv"
with open(suffix_file, 'w') as f:
    f.write("suffix\tcount\n")
    for suf, cnt in suffixes.most_common():
        f.write(f"{suf}\t{cnt}\n")
print(f"✓ Saved suffixes: {suffix_file}")

# Prefixes
prefix_file = OUTPUT / "latin_prefixes.tsv"
with open(prefix_file, 'w') as f:
    f.write("prefix\tcount\n")
    for pre, cnt in prefixes.most_common():
        f.write(f"{pre}\t{cnt}\n")
print(f"✓ Saved prefixes: {prefix_file}")

print(f"\nSample stems: {unique_stems[:20]}")
print(f"Top suffixes: {[s for s, _ in suffixes.most_common(10)]}")
print(f"Top prefixes: {[p for p, _ in prefixes.most_common(10)]}")

print("\n✅ Whitaker processing complete")

