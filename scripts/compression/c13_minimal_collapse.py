#!/usr/bin/env python3
"""
MINIMAL COLLAPSE: Try to PRESERVE diversity while getting 9 types

Instead of aggressive many→one, try gentle merging that maintains entropy.
"""

import re
from collections import Counter
import numpy as np

print("="*80)
print("MINIMAL COLLAPSE TEST")
print("="*80)

# Load
with open('corpora/latin_abbrev_expanded.txt', 'r') as f:
    latin_tokens = re.findall(r'\b[a-z]+\b', f.read().lower())

with open('p6_voynich_tokens.txt', 'r') as f:
    voynich_tokens = [line.strip() for line in f if line.strip()]

# Voynich reference
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

voy_total = sum(voynich_suffixes.values())
voy_props = {k: v/voy_total for k, v in voynich_suffixes.items()}
voy_probs = np.array([p for p in voy_props.values() if p > 0])
voy_entropy = -np.sum(voy_probs * np.log2(voy_probs))

print(f"\nVoynich: {voy_entropy:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    print(f"  {suf:4s}: {voy_props[suf]*100:5.1f}%")

# Compress
def compress(word):
    if len(word) <= 3:
        return word
    
    suffix_len = 0
    if len(word) >= 2 and word[-2:] in ['us', 'um', 'em', 'is', 'as', 'os', 'or', 'er', 'ar', 'ir']:
        suffix_len = 2
    elif word[-1] in 'aeiou':
        suffix_len = 1
    
    if len(word) <= suffix_len + 2:
        return word
    
    suffix = word[-suffix_len:] if suffix_len > 0 else ''
    middle_end = len(word) - suffix_len
    
    start = word[:min(2, middle_end)]
    middle = word[len(start):middle_end]
    
    comp = ''
    for i, c in enumerate(middle):
        if c not in 'aeiou' and (i % 2 == 0 or len(comp) < 2):
            comp += c
        elif c in 'aeiou' and len(comp) == 0:
            comp += c
    
    return (start + comp + suffix) if len(start + comp + suffix) >= 3 else word

# MINIMAL COLLAPSE: Keep diversity, just merge MINIMALLY
MINIMAL_MAP = {
    # Keep most Latin endings distinct, but map to Voynich labels
    'us': 'ol',    # Nominative
    'um': 'am',    # Accusative neuter
    'em': 'am',    # Accusative
    'is': 'ol',    # Genitive/dative
    'as': 'al',    # Accusative plural
    'os': 'or',    # Accusative plural
    'ae': 'y',     # Genitive/dative fem
    'a': 'y',      # Nominative fem (most common)
    'e': 'ain',    # Various
    'i': 'aiin',   # Genitive/locative
    'o': 'ody',    # Ablative/dative
    'u': 'ody',    # 
    'er': 'or',    # Infinitive
    'ar': 'or',    # Infinitive
    'ir': 'ain',   # Infinitive
    'or': 'or',    # Agent
}

compressed = [compress(t) for t in latin_tokens]

def minimal_merge(token):
    for length in [2, 1]:
        if len(token) >= length:
            suf = token[-length:]
            if suf in MINIMAL_MAP:
                return MINIMAL_MAP[suf]
    return 'NULL'

result_suffixes = Counter(minimal_merge(t) for t in compressed)

res_total = sum(result_suffixes.values())
res_props = {k: v/res_total for k, v in result_suffixes.items()}
res_probs = np.array([p for p in res_props.values() if p > 0])
res_entropy = -np.sum(res_probs * np.log2(res_probs))

print("\n" + "="*80)
print("MINIMAL COLLAPSE RESULT")
print("="*80)
print(f"\nEntropy: {res_entropy:.3f} bits (Voynich: {voy_entropy:.3f})")
print(f"Types: {len(result_suffixes)}")
print(f"Difference: {abs(res_entropy - voy_entropy):.3f} bits")

print("\nDistribution comparison:")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    v = voy_props.get(suf, 0) * 100
    r = res_props.get(suf, 0) * 100
    diff = abs(v - r)
    match = "✓✓" if diff < 5 else "✓" if diff < 10 else "~" if diff < 15 else "✗"
    print(f"  {suf:4s}: Voy={v:5.1f}% Min={r:5.1f}% Δ={diff:4.1f}pp {match}")

if abs(res_entropy - voy_entropy) < 0.4:
    print("\n✓✓✓ EXCELLENT MATCH!")
elif abs(res_entropy - voy_entropy) < 0.7:
    print("\n✓ GOOD MATCH!")
else:
    print("\n~ Partial match")

print("\n" + "="*80)
print("KEY INSIGHT")
print("="*80)
print("\nIf this STILL doesn't work, it means:")
print("1. No simple Latin compression matches Voynichese")
print("2. Either need MUCH more sophisticated model")
print("3. Or Voynichese isn't compressed Romance at all")
print("4. Or it's a constructed abbreviation system")

