#!/usr/bin/env python3
"""
TEST OCCITAN COMPRESSION - What we should have done first!

If hypothesis is "Voynichese = compressed Occitan", test OCCITAN, not Latin!
"""

import re
from collections import Counter
import numpy as np

print("="*80)
print("OCCITAN COMPRESSION TEST")
print("="*80)

# Load medieval Occitan
print("\n1. Loading medieval Occitan corpus...")
with open('corpora/medieval_sources/occitan_troubadour_sample.txt', 'r') as f:
    occitan_text = f.read().lower()

occitan_tokens = re.findall(r'\b[a-z]+\b', occitan_text)
print(f"   {len(occitan_tokens):,} tokens")

# Apply same compression as Latin
def smart_compress(word):
    """Same compression as we used for Latin"""
    if len(word) <= 3:
        return word
    
    # Preserve suffix (last 1-2 chars)
    if len(word) >= 2 and word[-2:] in ['er', 'ar', 'ir', 'on', 'an', 'at', 'en', 'et', 'or']:
        suffix_len = 2
    elif word[-1] in 'aeiouy':
        suffix_len = 1
    else:
        suffix_len = 0
    
    if len(word) <= suffix_len + 2:
        return word
    
    suffix = word[-suffix_len:] if suffix_len > 0 else ''
    middle_end = len(word) - suffix_len
    
    # Keep initial consonants
    start = ''
    i = 0
    while i < min(2, middle_end):
        if word[i] not in 'aeiouy':
            start += word[i]
            i += 1
        else:
            break
    
    # Compress middle
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

print("\n2. Compressing Occitan...")
compressed_occitan = [smart_compress(token) for token in occitan_tokens]

# Apply Occitan-specific suffix merging
OCCITAN_MERGER = {
    # Infinitives → map to Voynich suffixes
    'er': 'or',     # Most common infinitive
    'ar': 'or',
    'ir': 'ain',
    
    # Participles/adjectives
    'at': 'am',     # Past participle
    'ada': 'am',
    'ador': 'or',
    
    # Nominals
    'on': 'ol',
    'ment': 'al',
    'atge': 'al',
    
    # Verb endings
    'en': 'ain',
    'an': 'ain',
    'et': 'ody',
    'etz': 'ody',
    
    # Single vowels
    'e': 'y',       # Most common
    'a': 'y',
    'i': 'aiin',
    'o': 'ody',
}

def merge_occitan_suffix(token):
    """Apply Occitan→Voynich suffix mapping"""
    for lat in [4, 3, 2, 1]:  # Try longer suffixes first
        if len(token) >= lat:
            suf = token[-lat:]
            if suf in OCCITAN_MERGER:
                return OCCITAN_MERGER[suf]
    return 'NULL'

merged_occitan_suffixes = Counter()
for token in compressed_occitan:
    suffix = merge_occitan_suffix(token)
    merged_occitan_suffixes[suffix] += 1

# Load Voynich reference
print("\n3. Loading Voynich reference...")
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

# Calculate stats
def calc_stats(counts, name):
    total = sum(counts.values())
    props = {k: v/total for k, v in counts.items()}
    probs = np.array([p for p in props.values() if p > 0])
    entropy = -np.sum(probs * np.log2(probs))
    return {'name': name, 'n_types': len(counts), 'entropy': entropy, 'props': props, 'counts': counts}

voy = calc_stats(voynich_suffixes, "VOYNICH")
occ = calc_stats(merged_occitan_suffixes, "OCCITAN (merged)")

# Also get our Latin result for comparison
from collections import Counter as C
# Re-do Latin for fair comparison
latin_merged = {
    'y': 18.4, 'NULL': 17.1, 'aiin': 8.9, 'ol': 8.3,
    'al': 9.0, 'or': 1.6, 'ain': 11.1, 'ody': 11.6, 'am': 13.9
}
latin_ent = 3.011

print("\n" + "="*80)
print("RESULTS")
print("="*80)

print("\nVOYNICH:")
print(f"  Types: {voy['n_types']}, Entropy: {voy['entropy']:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suf in voy['props']:
        print(f"    {suf:4s}: {voy['props'][suf]*100:5.1f}%")

print("\nOCCITAN (compressed + merged):")
print(f"  Types: {occ['n_types']}, Entropy: {occ['entropy']:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suf in occ['props']:
        print(f"    {suf:4s}: {occ['props'][suf]*100:5.1f}%")

print("\nLATIN (compressed + merged) [from earlier]:")
print(f"  Types: 9, Entropy: {latin_ent:.3f} bits")
for suf in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suf in latin_merged:
        print(f"    {suf:4s}: {latin_merged[suf]:5.1f}%")

print("\n" + "="*80)
print("COMPARISON")
print("="*80)

# Calculate which is closer
voy_lat_diff = abs(voy['entropy'] - latin_ent)
voy_occ_diff = abs(voy['entropy'] - occ['entropy'])

print(f"\nEntropy difference from Voynich:")
print(f"  Latin:   {voy_lat_diff:.3f} bits")
print(f"  Occitan: {voy_occ_diff:.3f} bits")

if voy_occ_diff < voy_lat_diff:
    improvement = ((voy_lat_diff - voy_occ_diff) / voy_lat_diff) * 100
    print(f"\n✓ OCCITAN IS CLOSER! ({improvement:.1f}% better)")
elif voy_occ_diff > voy_lat_diff:
    print(f"\n✗ Latin is closer")
else:
    print(f"\n~ Same distance")

print(f"\nType count:")
print(f"  Voynich: {voy['n_types']}")
print(f"  Occitan: {occ['n_types']}")

