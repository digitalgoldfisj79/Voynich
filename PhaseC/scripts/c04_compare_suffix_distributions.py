#!/usr/bin/env python3
"""
The CRITICAL comparison: Do Voynichese and Abbreviated Latin have similar suffixes?
"""

import csv
from collections import Counter
import numpy as np

print("="*80)
print("SUFFIX DISTRIBUTION COMPARISON")
print("="*80)

# 1. Load Voynich suffixes
print("\n1. Loading Voynichese suffix distribution...")
voynich_suffixes = {}
with open('N4_Frozen_Model/PhaseM/out/m01_suffix_inventory.tsv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        suffix = row['suffix']
        count = int(row['token_count'])
        voynich_suffixes[suffix] = count

total_voy = sum(voynich_suffixes.values())
voynich_props = {k: v/total_voy for k, v in voynich_suffixes.items()}

print(f"   {len(voynich_suffixes)} suffix types, {total_voy:,} tokens")

# 2. Load compressed Latin
print("\n2. Processing compressed Latin...")
with open('corpora/latin_abbrev_compressed.txt', 'r') as f:
    compressed_tokens = [line.strip().lower() for line in f if line.strip() and line.strip()[0].isalpha()]

print(f"   {len(compressed_tokens):,} tokens")

# Extract suffixes using Voynich patterns
voynich_suffix_types = ['aiin', 'ain', 'ody', 'ol', 'al', 'or', 'am', 'y']
latin_suffixes = Counter()

for token in compressed_tokens:
    matched = False
    for suf in voynich_suffix_types:
        if token.endswith(suf):
            latin_suffixes[suf] += 1
            matched = True
            break
    
    if not matched:
        latin_suffixes['NULL'] += 1

total_lat = sum(latin_suffixes.values())
latin_props = {k: v/total_lat for k, v in latin_suffixes.items()}

# 3. Calculate entropy
def entropy(props):
    probs = np.array([p for p in props.values() if p > 0])
    return -np.sum(probs * np.log2(probs))

voy_entropy = entropy(voynich_props)
lat_entropy = entropy(latin_props)

print("\n" + "="*80)
print("RESULTS")
print("="*80)

print("\nVoynichese:")
print(f"  Entropy: {voy_entropy:.3f} bits")
for suffix in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suffix in voynich_props:
        print(f"    {suffix:4s}: {voynich_props[suffix]*100:5.1f}%")

print("\nCompressed Latin:")
print(f"  Entropy: {lat_entropy:.3f} bits")
for suffix in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    if suffix in latin_props:
        count = latin_suffixes[suffix]
        print(f"    {suffix:4s}: {latin_props[suffix]*100:5.1f}% ({count:,})")

print("\n" + "="*80)
print("COMPARISON")
print("="*80)
print(f"Entropy difference: {abs(voy_entropy - lat_entropy):.3f} bits")

common = set(voynich_props.keys()) & set(latin_props.keys())
print(f"Common suffixes: {len(common)}")

if abs(voy_entropy - lat_entropy) < 0.5:
    print("\n✓ Entropies MATCH")
else:
    print("\n⚠️ Entropies DIFFER")

print("\nPROBLEM: Token lengths don't match:")
print("  Voynich: 5.09 chars")
print("  Compressed Latin: 2.58 chars")
print("  → Compression is TOO AGGRESSIVE")

