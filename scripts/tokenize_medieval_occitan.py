#!/usr/bin/env python3
"""
Tokenize medieval Occitan dictionary
Extract stems and suffixes like other Romance languages
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re

BASE = Path(__file__).parent.parent
OCCITAN = BASE / "corpora/medieval_sources/occitan_medieval_dict.txt"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("TOKENIZING MEDIEVAL OCCITAN")
print("="*80)

# Load Occitan words
text = OCCITAN.read_text()
tokens = text.split()

print(f"\nUnique Occitan words: {len(tokens):,}")

# Occitan suffixes (similar to French/Catalan but medieval)
OCCITAN_ENDINGS = [
    'ar', 'er', 'ir', 'or',  # Infinitives
    'at', 'et', 'it',         # Past participles
    'atz', 'etz', 'itz',      # Plural/2nd person
    'a', 'e', 'o', 'i',       # Vowel endings
    'an', 'en', 'on',         # Nasal endings
    'ada', 'eda', 'ida',      # Feminine past
    'ador', 'edor', 'idor',   # Agent nouns
    'atge', 'ment',           # Abstract nouns
]

def stem_word(word, endings):
    """Remove Occitan ending to get stem"""
    for ending in sorted(endings, key=len, reverse=True):
        if word.endswith(ending) and len(word) > len(ending) + 2:
            return word[:-len(ending)], ending
    return word, ''

# Process
stems = []
suffixes = Counter()
prefixes = Counter()

for token in tokens:
    if 2 <= len(token) <= 15:
        stem, suffix = stem_word(token, OCCITAN_ENDINGS)
        
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
TOK.mkdir(exist_ok=True)

# Stems
(TOK / "occitan_medieval_stems.txt").write_text('\n'.join(unique_stems))

# Suffixes
with open(TOK / "occitan_medieval_suffixes.tsv", 'w') as f:
    f.write("suffix\tcount\n")
    for suf, cnt in suffixes.most_common():
        f.write(f"{suf}\t{cnt}\n")

# Prefixes
with open(TOK / "occitan_medieval_prefixes.tsv", 'w') as f:
    f.write("prefix\tcount\n")
    for pre, cnt in prefixes.most_common():
        f.write(f"{pre}\t{cnt}\n")

print(f"\n✓ Saved to: romance_tokenized/occitan_medieval_*")

print(f"\nTop 10 suffixes:")
for suf, cnt in suffixes.most_common(10):
    print(f"  -{suf:8s}: {cnt:6,} times")

print(f"\nTop 10 prefixes:")
for pre, cnt in prefixes.most_common(10):
    print(f"  {pre}-:  {cnt:6,} times")

print(f"\nSample stems: {unique_stems[:20]}")

print("\n" + "="*80)
print("✅ MEDIEVAL OCCITAN READY")
print("="*80)

