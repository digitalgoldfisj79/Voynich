#!/usr/bin/env python3
"""
SYSTEMATIC COMPRESSION TESTING SUITE

Test ALL plausible compression models to find what works.
"""

import re
from collections import Counter
import numpy as np

print("="*80)
print("SYSTEMATIC COMPRESSION TEST SUITE")
print("="*80)

# Load corpora
print("\n1. Loading corpora...")
with open('corpora/latin_abbrev_expanded.txt', 'r') as f:
    latin_tokens = re.findall(r'\b[a-z]+\b', f.read().lower())

with open('corpora/romance_tokenized/occitan_medieval_stems.txt', 'r') as f:
    occitan_tokens = [line.strip().lower() for line in f if line.strip()]

with open('p6_voynich_tokens.txt', 'r') as f:
    voynich_tokens = [line.strip() for line in f if line.strip()]

print(f"   Latin: {len(latin_tokens):,}")
print(f"   Occitan: {len(occitan_tokens):,}")
print(f"   Voynich: {len(voynich_tokens):,}")

# Extract Voynich reference
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

print(f"\nVoynich reference: {len(voynich_suffixes)} types, {voy_entropy:.3f} bits")

# Compression functions
def compress_token(word):
    """Standard compression"""
    if len(word) <= 3:
        return word
    
    suffix_len = 0
    for suf_len in [3, 2, 1]:
        if len(word) >= suf_len:
            suf = word[-suf_len:]
            if suf_len == 2 and suf in ['er', 'ar', 'ir', 'on', 'an', 'at', 'en', 'et', 'or', 'am', 'um', 'em', 'us', 'is']:
                suffix_len = 2
                break
            elif suf_len == 1 and suf in 'aeiouy':
                suffix_len = 1
                break
    
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
    compressed = ''
    for i, c in enumerate(middle):
        if c not in 'aeiouy':
            if i % 2 == 0 or len(compressed) < 2:
                compressed += c
        elif len(compressed) == 0:
            compressed += c
    
    result = start + compressed + suffix
    return result if len(result) >= 3 else word

# TEST 1: AGGRESSIVE MANY-TO-ONE COLLAPSE
print("\n" + "="*80)
print("TEST 1: AGGRESSIVE MANY-TO-ONE SUFFIX COLLAPSE")
print("="*80)

AGGRESSIVE_COLLAPSE = {
    # ALL nominal endings → y (most common in Voynich)
    'a': 'y', 'ae': 'y', 'am': 'y', 'as': 'y', 'arum': 'y',
    'us': 'y', 'um': 'y', 'o': 'y', 'os': 'y', 'orum': 'y',
    'e': 'y', 'i': 'y',
    
    # ALL infinitives + some verbals → or
    'are': 'or', 'ere': 'or', 'ire': 'or', 
    'or': 'or', 'ur': 'or', 'er': 'or', 'ar': 'or', 'ir': 'or',
    
    # Participles + some endings → am
    'at': 'am', 'et': 'am', 'it': 'am',
    'atum': 'am', 'atus': 'am',
    
    # Plural/dative → ol
    'is': 'ol', 'bus': 'ol', 'on': 'ol',
    
    # Adverbial/abstract → al  
    'ment': 'al', 'atge': 'al',
    
    # Verbal continuous → ain
    'nt': 'ain', 'an': 'ain', 'en': 'ain',
    
    # Gerunds/participles → aiin
    'ntur': 'aiin', 'ndo': 'aiin', 'endo': 'aiin',
    
    # Short endings → ody
    'etz': 'ody', 'u': 'ody',
}

def aggressive_merge(token):
    for length in [5, 4, 3, 2, 1]:
        if len(token) >= length:
            suf = token[-length:]
            if suf in AGGRESSIVE_COLLAPSE:
                return AGGRESSIVE_COLLAPSE[suf]
    return 'NULL'

compressed_latin = [compress_token(t) for t in latin_tokens]
test1_suffixes = Counter(aggressive_merge(t) for t in compressed_latin)

test1_total = sum(test1_suffixes.values())
test1_props = {k: v/test1_total for k, v in test1_suffixes.items()}
test1_probs = np.array([p for p in test1_props.values() if p > 0])
test1_entropy = -np.sum(test1_probs * np.log2(test1_probs))

print(f"\nResult: {len(test1_suffixes)} types, {test1_entropy:.3f} bits")
print("Distribution:")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    v = voy_props.get(suf, 0) * 100
    t = test1_props.get(suf, 0) * 100
    diff = abs(v - t)
    print(f"  {suf:4s}: Voy={v:5.1f}% Test1={t:5.1f}% (Δ={diff:4.1f}pp)")

test1_score = abs(voy_entropy - test1_entropy)
print(f"\nEntropy difference: {test1_score:.3f} bits")

# TEST 2: HYBRID (70% Latin + 30% Occitan)
print("\n" + "="*80)
print("TEST 2: HYBRID LATIN + OCCITAN")
print("="*80)

n_latin = int(len(latin_tokens) * 0.7)
n_occitan = int(len(occitan_tokens) * 0.3)
hybrid_tokens = latin_tokens[:n_latin] + occitan_tokens[:n_occitan]

compressed_hybrid = [compress_token(t) for t in hybrid_tokens]
test2_suffixes = Counter(aggressive_merge(t) for t in compressed_hybrid)

test2_total = sum(test2_suffixes.values())
test2_props = {k: v/test2_total for k, v in test2_suffixes.items()}
test2_probs = np.array([p for p in test2_props.values() if p > 0])
test2_entropy = -np.sum(test2_probs * np.log2(test2_probs))

print(f"\nResult: {len(test2_suffixes)} types, {test2_entropy:.3f} bits")
print("Top differences:")
for suf in ['y', 'NULL', 'or', 'am']:
    v = voy_props.get(suf, 0) * 100
    t = test2_props.get(suf, 0) * 100
    print(f"  {suf:4s}: Voy={v:5.1f}% Hybrid={t:5.1f}%")

test2_score = abs(voy_entropy - test2_entropy)
print(f"\nEntropy difference: {test2_score:.3f} bits")

# TEST 3: CONTEXT-DEPENDENT (different rules for Currier A vs B)
print("\n" + "="*80)
print("TEST 3: CONTEXT-DEPENDENT COMPRESSION")
print("="*80)

# Simulate: Currier A (formal) = less aggressive, Currier B (informal) = more aggressive
CURRIER_A_COLLAPSE = {
    'a': 'y', 'us': 'y', 'um': 'y',
    'are': 'or', 'ere': 'or',
    'is': 'ol', 'bus': 'ol',
    'nt': 'ain',
}

CURRIER_B_COLLAPSE = {
    'a': 'y', 'ae': 'y', 'e': 'y', 'i': 'y', 'o': 'y', 'u': 'y',  # Aggressive vowel collapse
    'us': 'y', 'um': 'y', 'os': 'y',
    'are': 'or', 'ere': 'or', 'ire': 'or', 'or': 'or',
    'at': 'am', 'et': 'am',
    'is': 'ol', 'bus': 'ol',
    'nt': 'ain', 'an': 'ain',
}

def context_merge_a(token):
    for length in [3, 2, 1]:
        if len(token) >= length:
            suf = token[-length:]
            if suf in CURRIER_A_COLLAPSE:
                return CURRIER_A_COLLAPSE[suf]
    return 'NULL'

def context_merge_b(token):
    for length in [3, 2, 1]:
        if len(token) >= length:
            suf = token[-length:]
            if suf in CURRIER_B_COLLAPSE:
                return CURRIER_B_COLLAPSE[suf]
    return 'NULL'

# Mix: 40% Currier A, 60% Currier B (approximate manuscript proportions)
n_a = int(len(compressed_latin) * 0.4)
test3_suffixes = Counter()
for i, token in enumerate(compressed_latin):
    if i < n_a:
        test3_suffixes[context_merge_a(token)] += 1
    else:
        test3_suffixes[context_merge_b(token)] += 1

test3_total = sum(test3_suffixes.values())
test3_props = {k: v/test3_total for k, v in test3_suffixes.items()}
test3_probs = np.array([p for p in test3_props.values() if p > 0])
test3_entropy = -np.sum(test3_probs * np.log2(test3_probs))

print(f"\nResult: {len(test3_suffixes)} types, {test3_entropy:.3f} bits")
print("Key suffixes:")
for suf in ['y', 'NULL', 'or']:
    v = voy_props.get(suf, 0) * 100
    t = test3_props.get(suf, 0) * 100
    print(f"  {suf:4s}: Voy={v:5.1f}% Context={t:5.1f}%")

test3_score = abs(voy_entropy - test3_entropy)
print(f"\nEntropy difference: {test3_score:.3f} bits")

# TEST 4: ULTRA-AGGRESSIVE (maximize y-suffix dominance)
print("\n" + "="*80)
print("TEST 4: ULTRA-AGGRESSIVE COLLAPSE (maximize y)")
print("="*80)

ULTRA_COLLAPSE = {
    # Map EVERYTHING nominal to y
    'a': 'y', 'ae': 'y', 'am': 'y', 'as': 'y', 'arum': 'y',
    'us': 'y', 'um': 'y', 'o': 'y', 'os': 'y', 'orum': 'y',
    'e': 'y', 'i': 'y', 'em': 'y', 'es': 'y', 'is': 'y',
    
    # Only keep distinct suffixes for specific functions
    'are': 'or', 'ere': 'or', 'ire': 'or',
    'nt': 'ain', 'ntur': 'aiin',
    'bus': 'ol',
    'ment': 'al',
    'at': 'am',
}

def ultra_merge(token):
    for length in [4, 3, 2, 1]:
        if len(token) >= length:
            suf = token[-length:]
            if suf in ULTRA_COLLAPSE:
                return ULTRA_COLLAPSE[suf]
    return 'NULL'

test4_suffixes = Counter(ultra_merge(t) for t in compressed_latin)

test4_total = sum(test4_suffixes.values())
test4_props = {k: v/test4_total for k, v in test4_suffixes.items()}
test4_probs = np.array([p for p in test4_props.values() if p > 0])
test4_entropy = -np.sum(test4_probs * np.log2(test4_probs))

print(f"\nResult: {len(test4_suffixes)} types, {test4_entropy:.3f} bits")
print("Distribution:")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    v = voy_props.get(suf, 0) * 100
    t = test4_props.get(suf, 0) * 100
    diff = abs(v - t)
    print(f"  {suf:4s}: Voy={v:5.1f}% Test4={t:5.1f}% (Δ={diff:4.1f}pp)")

test4_score = abs(voy_entropy - test4_entropy)
print(f"\nEntropy difference: {test4_score:.3f} bits")

# FINAL COMPARISON
print("\n" + "="*80)
print("FINAL COMPARISON - WHICH MODEL WINS?")
print("="*80)

results = [
    ("Aggressive collapse", test1_score, test1_entropy, len(test1_suffixes)),
    ("Hybrid Latin+Occitan", test2_score, test2_entropy, len(test2_suffixes)),
    ("Context-dependent", test3_score, test3_entropy, len(test3_suffixes)),
    ("Ultra-aggressive", test4_score, test4_entropy, len(test4_suffixes)),
]

results.sort(key=lambda x: x[1])

print(f"\nVoynich target: {voy_entropy:.3f} bits, 9 types")
print(f"\nRanked by entropy match:")
for i, (name, score, entropy, n_types) in enumerate(results, 1):
    match = "✓✓✓" if score < 0.2 else "✓✓" if score < 0.4 else "✓" if score < 0.6 else "~"
    print(f"{i}. {name:25s}: {entropy:.3f} bits ({n_types} types) Δ={score:.3f} {match}")

best_name, best_score, best_ent, best_types = results[0]
print(f"\n{'='*80}")
print(f"WINNER: {best_name}")
print(f"{'='*80}")
print(f"Entropy: {best_ent:.3f} vs Voynich {voy_entropy:.3f}")
print(f"Difference: {best_score:.3f} bits")

if best_score < 0.3:
    print("\n✓✓✓ EXCELLENT MATCH! Hypothesis strongly supported!")
elif best_score < 0.5:
    print("\n✓ GOOD MATCH! Hypothesis supported with minor differences.")
else:
    print("\n~ PARTIAL MATCH. Some support but gaps remain.")

