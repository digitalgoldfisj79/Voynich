#!/usr/bin/env python3
"""
PROPER OCCITAN COMPRESSION TEST with full corpus (7,003 tokens)
"""

import re
from collections import Counter
import numpy as np

print("="*80)
print("OCCITAN COMPRESSION - PROPER TEST")
print("="*80)

# Load the FULL medieval Occitan corpus
print("\n1. Loading medieval Occitan stems...")
with open('corpora/romance_tokenized/occitan_medieval_stems.txt', 'r') as f:
    occitan_tokens = [line.strip().lower() for line in f if line.strip()]

print(f"   {len(occitan_tokens):,} tokens")

# Compression (same as Latin)
def smart_compress(word):
    if len(word) <= 3:
        return word
    
    # Identify Occitan suffix
    suffix_len = 0
    if len(word) >= 3 and word[-3:] in ['ador', 'atge', 'ment']:
        suffix_len = 3
    elif len(word) >= 2 and word[-2:] in ['er', 'ar', 'ir', 'on', 'an', 'at', 'en', 'et', 'or', 'ada']:
        suffix_len = 2
    elif word[-1] in 'aeiouy':
        suffix_len = 1
    
    if len(word) <= suffix_len + 2:
        return word
    
    suffix = word[-suffix_len:] if suffix_len > 0 else ''
    middle_end = len(word) - suffix_len
    
    start = ''
    i = 0
    while i < min(2, middle_end):
        if word[i] not in 'aeiouy':
            start += word[i]
            i += 1
        else:
            break
    
    middle = word[len(start):middle_end]
    compressed_middle = ''
    for i, c in enumerate(middle):
        if c not in 'aeiouy':
            if i % 2 == 0 or len(compressed_middle) < 2:
                compressed_middle += c
        elif len(compressed_middle) == 0:
            compressed_middle += c
    
    result = start + compressed_middle + suffix
    return result if len(result) >= 3 else word

print("\n2. Compressing Occitan tokens...")
compressed = [smart_compress(token) for token in occitan_tokens]

mean_orig = sum(len(t) for t in occitan_tokens) / len(occitan_tokens)
mean_comp = sum(len(t) for t in compressed) / len(compressed)
print(f"   {mean_orig:.2f} → {mean_comp:.2f} chars")

# Morphological merging
OCCITAN_TO_VOYNICH = {
    # Infinitives (very common in Occitan)
    'er': 'or', 'ar': 'or', 'ir': 'ain',
    
    # Participles
    'at': 'am', 'ada': 'am', 'ador': 'or',
    
    # Nominals
    'on': 'ol', 'ment': 'al', 'atge': 'al',
    
    # Verbs
    'en': 'ain', 'an': 'ain', 'et': 'ody', 'etz': 'ody',
    
    # Vowels
    'e': 'y', 'a': 'y', 'i': 'aiin', 'o': 'ody', 'u': 'ody',
}

def merge_suffix(token):
    for lat in [4, 3, 2, 1]:
        if len(token) >= lat:
            suf = token[-lat:]
            if suf in OCCITAN_TO_VOYNICH:
                return OCCITAN_TO_VOYNICH[suf]
    return 'NULL'

print("\n3. Applying morphological merging...")
merged_suffixes = Counter()
for token in compressed:
    merged_suffixes[merge_suffix(token)] += 1

# Load Voynich
with open('p6_voynich_tokens.txt', 'r') as f:
    voynich_tokens = [line.strip() for line in f if line.strip()]

voynich_suffixes = Counter()
for token in voynich_tokens:
    matched = False
    for suf in ['aiin', 'ain', 'ody', 'ol', 'al', 'or', 'am', 'y']:
        if token.endswith(suf):
            voynich_suffixes[suf] += 1
            matched = True
            break
    if not matched:
        voynich_suffixes['NULL'] += 1

# Stats
def calc_stats(counts):
    total = sum(counts.values())
    props = {k: v/total for k, v in counts.items()}
    probs = np.array([p for p in props.values() if p > 0])
    entropy = -np.sum(probs * np.log2(probs))
    return len(counts), entropy, props

voy_n, voy_ent, voy_props = calc_stats(voynich_suffixes)
occ_n, occ_ent, occ_props = calc_stats(merged_suffixes)

# Latin comparison (from earlier)
latin_ent = 3.011
latin_props = {
    'y': 18.4, 'NULL': 17.1, 'aiin': 8.9, 'ol': 8.3,
    'al': 9.0, 'or': 1.6, 'ain': 11.1, 'ody': 11.6, 'am': 13.9
}

print("\n" + "="*80)
print("RESULTS")
print("="*80)

print("\nVOYNICH:")
print(f"  Corpus: 29,688 tokens")
print(f"  Types: {voy_n}, Entropy: {voy_ent:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suf in voy_props:
        print(f"    {suf:4s}: {voy_props[suf]*100:5.1f}%")

print("\nOCCITAN (compressed + merged):")
print(f"  Corpus: {len(occitan_tokens):,} tokens")
print(f"  Types: {occ_n}, Entropy: {occ_ent:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suf in occ_props:
        print(f"    {suf:4s}: {occ_props[suf]*100:5.1f}%")

print("\nLATIN (compressed + merged):")
print(f"  Corpus: 13,200 tokens")
print(f"  Types: 9, Entropy: {latin_ent:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suf in latin_props:
        print(f"    {suf:4s}: {latin_props[suf]:5.1f}%")

print("\n" + "="*80)
print("HEAD-TO-HEAD COMPARISON")
print("="*80)

print(f"\nEntropy vs Voynich ({voy_ent:.3f} bits):")
print(f"  Latin:   {abs(latin_ent - voy_ent):.3f} bits off")
print(f"  Occitan: {abs(occ_ent - voy_ent):.3f} bits off")

if abs(occ_ent - voy_ent) < abs(latin_ent - voy_ent):
    print("  → OCCITAN WINS!")
else:
    print("  → Latin closer")

print(f"\nSuffix types:")
print(f"  Target (Voynich): {voy_n}")
print(f"  Latin:   {9} (exact match ✓)")
print(f"  Occitan: {occ_n}")

# Detailed distribution comparison
print("\n" + "="*80)
print("DISTRIBUTION DETAILS")
print("="*80)

print(f"\n{'Suffix':6s} {'Voynich':>8s} {'Occitan':>8s} {'Latin':>8s}")
print("-" * 34)
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    v = voy_props.get(suf, 0) * 100
    o = occ_props.get(suf, 0) * 100
    l = latin_props.get(suf, 0)
    print(f"{suf:6s} {v:7.1f}% {o:7.1f}% {l:7.1f}%")

