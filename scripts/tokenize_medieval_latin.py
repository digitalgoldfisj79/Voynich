#!/usr/bin/env python3
"""
Tokenize medieval Latin medical corpus
Extract stems and suffixes like we did for Romance languages
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re

BASE = Path(__file__).parent.parent
MED_TOK = BASE / "corpora/medieval_tokenized"
ROM_TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("TOKENIZING MEDIEVAL LATIN MEDICAL CORPUS")
print("="*80)

# Load medieval Latin
text = (MED_TOK / "medieval_latin_medical.txt").read_text()
tokens = text.split()

print(f"\nTotal tokens: {len(tokens):,}")
print(f"Unique tokens: {len(set(tokens)):,}")

# Latin suffixes (common medical/pharmaceutical)
LATIN_ENDINGS = [
    'us', 'um', 'is', 'os', 'as', 'am', 'em', 'im',
    'are', 'ere', 'ire', 'or', 'ur', 'at', 'et', 'it',
    'orum', 'arum', 'ibus', 'ae', 'ei',
    'o', 'a', 'e', 'i'
]

def stem_word(word, endings):
    """Remove Latin ending to get stem"""
    for ending in sorted(endings, key=len, reverse=True):
        if word.endswith(ending) and len(word) > len(ending) + 2:
            return word[:-len(ending)], ending
    return word, ''

# Process
stems = []
suffixes = Counter()
prefixes = Counter()

for token in tokens:
    if 2 <= len(token) <= 15:  # Filter length
        stem, suffix = stem_word(token, LATIN_ENDINGS)
        
        stems.append(stem)
        
        if suffix:
            suffixes[suffix] += 1
        
        # Prefix patterns
        if len(stem) >= 2:
            prefixes[stem[:2]] += 1
        if len(stem) >= 3:
            prefixes[stem[:3]] += 1

unique_stems = list(set(stems))

print(f"\nStemming results:")
print(f"  Unique stems: {len(unique_stems):,}")
print(f"  Suffix types: {len(suffixes)}")
print(f"  Prefix patterns: {len(prefixes)}")

# Save
ROM_TOK.mkdir(exist_ok=True)

# Stems
(ROM_TOK / "medieval_latin_stems.txt").write_text('\n'.join(unique_stems))

# Suffixes
with open(ROM_TOK / "medieval_latin_suffixes.tsv", 'w') as f:
    f.write("suffix\tcount\n")
    for suf, cnt in suffixes.most_common():
        f.write(f"{suf}\t{cnt}\n")

# Prefixes
with open(ROM_TOK / "medieval_latin_prefixes.tsv", 'w') as f:
    f.write("prefix\tcount\n")
    for pre, cnt in prefixes.most_common():
        f.write(f"{pre}\t{cnt}\n")

print(f"\n✓ Saved to: romance_tokenized/medieval_latin_*")

print(f"\nTop 10 suffixes:")
for suf, cnt in suffixes.most_common(10):
    print(f"  -{suf:8s}: {cnt:6,} times")

print(f"\nTop 10 prefixes:")
for pre, cnt in prefixes.most_common(10):
    print(f"  {pre}-:  {cnt:6,} times")

print(f"\nSample stems: {unique_stems[:20]}")

print("\n" + "="*80)
print("✅ MEDIEVAL LATIN MEDICAL CORPUS READY")
print("="*80)

