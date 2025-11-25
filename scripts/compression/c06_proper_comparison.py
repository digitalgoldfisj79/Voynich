#!/usr/bin/env python3
"""
PROPER COMPARISON: Extract LATIN suffixes from Latin, not Voynich suffixes!

The question is: Does compressed Latin have similar SUFFIX DIVERSITY as Voynich?
Not: Does compressed Latin have the SAME suffixes as Voynich?
"""

import re
from collections import Counter
import numpy as np

print("="*80)
print("PROPER SUFFIX DIVERSITY COMPARISON")
print("="*80)

def extract_latin_suffixes(tokens):
    """Extract actual Latin-style suffixes"""
    suffix_counts = Counter()
    
    for token in tokens:
        if len(token) < 2:
            suffix_counts['NULL'] += 1
            continue
        
        # Common Latin endings (1-3 chars)
        if len(token) >= 3:
            # 3-char suffixes
            if token[-3:] in ['bus', 'rum', 'ris', 'tis', 'mus', 'tur']:
                suffix_counts[token[-3:]] += 1
                continue
        
        if len(token) >= 2:
            # 2-char suffixes
            if token[-2:] in ['am', 'um', 'em', 'im', 'om', 'us', 'is', 'es', 'as', 'os', 
                              'ae', 'or', 'ur', 'ar', 'er', 'ir', 'nt', 'et', 'at', 'it']:
                suffix_counts[token[-2:]] += 1
                continue
        
        # 1-char vowel endings
        if token[-1] in 'aeiouy':
            suffix_counts[token[-1]] += 1
        else:
            suffix_counts['NULL'] += 1
    
    return suffix_counts

def calculate_entropy(suffix_counts):
    total = sum(suffix_counts.values())
    props = {k: v/total for k, v in suffix_counts.items()}
    probs = np.array([p for p in props.values() if p > 0])
    return -np.sum(probs * np.log2(probs)), props

# Load corpora
print("\n1. Loading corpora...")

# Voynich
with open('N4_Frozen_Model/PhaseM/out/m01_suffix_inventory.tsv', 'r') as f:
    import csv
    reader = csv.DictReader(f, delimiter='\t')
    voynich_suffixes = Counter()
    for row in reader:
        voynich_suffixes[row['suffix']] = int(row['token_count'])

# Expanded Latin
with open('corpora/latin_abbrev_expanded.txt', 'r') as f:
    expanded_tokens = re.findall(r'\b[a-z]+\b', f.read().lower())

# Smart compressed Latin  
with open('corpora/latin_smart_compressed.txt', 'r') as f:
    compressed_tokens = [line.strip() for line in f if line.strip()]

print(f"   Voynich: {sum(voynich_suffixes.values()):,} tokens")
print(f"   Expanded: {len(expanded_tokens):,} tokens")
print(f"   Compressed: {len(compressed_tokens):,} tokens")

# Extract Latin suffixes properly
print("\n2. Extracting suffix distributions...")

expanded_suf = extract_latin_suffixes(expanded_tokens)
compressed_suf = extract_latin_suffixes(compressed_tokens)

# Calculate entropies
voy_entropy, voy_props = calculate_entropy(voynich_suffixes)
exp_entropy, exp_props = calculate_entropy(expanded_suf)
comp_entropy, comp_props = calculate_entropy(compressed_suf)

print("\n" + "="*80)
print("RESULTS: SUFFIX DIVERSITY")
print("="*80)

print("\nVOYNICH:")
print(f"  Entropy: {voy_entropy:.3f} bits")
print(f"  Suffix types: {len(voynich_suffixes)}")
print(f"  Top suffixes:")
for suffix, count in voynich_suffixes.most_common(8):
    prop = count / sum(voynich_suffixes.values())
    print(f"    {suffix:4s}: {prop*100:5.1f}%")

print("\nEXPANDED LATIN:")
print(f"  Entropy: {exp_entropy:.3f} bits")
print(f"  Suffix types: {len(expanded_suf)}")
print(f"  Top suffixes:")
for suffix, count in expanded_suf.most_common(8):
    prop = count / sum(expanded_suf.values())
    print(f"    {suffix:4s}: {prop*100:5.1f}%")

print("\nSMART COMPRESSED LATIN:")
print(f"  Entropy: {comp_entropy:.3f} bits")
print(f"  Suffix types: {len(compressed_suf)}")
print(f"  Top suffixes:")
for suffix, count in compressed_suf.most_common(8):
    prop = count / sum(compressed_suf.values())
    print(f"    {suffix:4s}: {prop*100:5.1f}%")

print("\n" + "="*80)
print("CRITICAL COMPARISON")
print("="*80)

print(f"\nSuffix entropy:")
print(f"  Voynich:              {voy_entropy:.3f} bits")
print(f"  Expanded Latin:       {exp_entropy:.3f} bits")
print(f"  Compressed Latin:     {comp_entropy:.3f} bits")

print(f"\nDoes compression INCREASE diversity?")
if comp_entropy > exp_entropy:
    increase = ((comp_entropy - exp_entropy) / exp_entropy) * 100
    print(f"  ✓ YES! {increase:+.1f}% increase")
else:
    print(f"  ✗ NO - compression reduced diversity")

print(f"\nDoes compressed Latin approach Voynich?")
voy_exp_diff = abs(voy_entropy - exp_entropy)
voy_comp_diff = abs(voy_entropy - comp_entropy)

print(f"  Voynich ↔ Expanded:   {voy_exp_diff:.3f} bits difference")
print(f"  Voynich ↔ Compressed: {voy_comp_diff:.3f} bits difference")

if voy_comp_diff < voy_exp_diff:
    improvement = ((voy_exp_diff - voy_comp_diff) / voy_exp_diff) * 100
    print(f"  ✓ Compressed is {improvement:.1f}% CLOSER to Voynich")
else:
    print(f"  ✗ Compressed is further from Voynich")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if comp_entropy > exp_entropy and voy_comp_diff < voy_exp_diff:
    print("\n✓✓✓ HYPOTHESIS SUPPORTED!")
    print("Compression INCREASES morphological diversity")
    print("and moves Latin CLOSER to Voynichese patterns.")
elif comp_entropy > exp_entropy:
    print("\n✓ PARTIAL SUPPORT")
    print("Compression increases diversity but still differs from Voynich.")
else:
    print("\n✗ HYPOTHESIS NOT SUPPORTED")
    print("This compression method doesn't produce Voynich-like diversity.")

