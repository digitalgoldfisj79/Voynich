#!/usr/bin/env python3
"""
Calculate Currier A/B using Phase M morphological decomposition
"""

import csv
import os
from collections import defaultdict
import numpy as np
import re

print("="*80)
print("CURRIER A/B WITH PHASE M MORPHOLOGY")
print("="*80)

# Files
folio_tokens_file = os.path.expanduser("~/Voynich/ATTIC/PhaseS_dir/out/p6_folio_tokens.tsv")
folio_currier_file = os.path.expanduser("~/Voynich/ATTIC/PhaseS_dir/tmp/s49b_folio_hand_currier_section.tsv")

# Load Currier assignments
print("\n1. Loading Currier assignments...")
folio_to_currier = {}
with open(folio_currier_file, 'r') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            folio = parts[0]
            currier = parts[2]
            if currier in ('A', 'B'):
                folio_to_currier[folio] = currier

print(f"   {len(folio_to_currier)} folio mappings")

# Load Phase M stem-suffix mappings
print("\n2. Loading Phase M morphological data...")
stem_to_suffixes = {}
with open('N4_Frozen_Model/PhaseM/out/m08_stem_suffix_combinations.tsv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        stem = row['stem']
        suffix = row['suffix']
        if suffix == 'NULL':
            suffix = 'NULL'
        
        if stem not in stem_to_suffixes:
            stem_to_suffixes[stem] = []
        stem_to_suffixes[stem].append(suffix)

print(f"   {len(stem_to_suffixes)} stems with morphology")

# Build token→stem→suffix lookup
print("\n3. Analyzing tokens by stem...")
token_to_stem_suffix = {}

for stem, suffixes in stem_to_suffixes.items():
    for suffix in suffixes:
        if suffix == 'NULL':
            token = stem
        else:
            token = stem + suffix
        
        # Store the most common suffix for this token
        if token not in token_to_stem_suffix:
            token_to_stem_suffix[token] = (stem, suffix)

print(f"   {len(token_to_stem_suffix)} token→suffix mappings")

# Process folio tokens with Phase M morphology
print("\n4. Counting suffixes by Currier...")

currier_suffix_counts = {'A': defaultdict(int), 'B': defaultdict(int)}
tokens_processed = {'A': 0, 'B': 0}
tokens_no_morph = 0
tokens_no_currier = 0

with open(folio_tokens_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    
    for row in reader:
        token = row['token']
        folio_full = row['folio']
        
        # Extract folio ID
        match = re.match(r'(f\d+[rv])', folio_full)
        if not match:
            continue
        folio = match.group(1)
        
        # Map to Currier
        currier = folio_to_currier.get(folio)
        if not currier:
            tokens_no_currier += 1
            continue
        
        # Get Phase M morphology
        if token in token_to_stem_suffix:
            stem, suffix = token_to_stem_suffix[token]
        else:
            tokens_no_morph += 1
            continue
        
        currier_suffix_counts[currier][suffix] += 1
        tokens_processed[currier] += 1

print(f"   Currier A: {tokens_processed['A']:,} tokens")
print(f"   Currier B: {tokens_processed['B']:,} tokens")
print(f"   No morphology: {tokens_no_morph:,}")
print(f"   No Currier: {tokens_no_currier:,}")

# Calculate entropy
def calculate_entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0, {}
    props = {k: v/total for k, v in counts.items()}
    probs = np.array([p for p in props.values() if p > 0])
    entropy = -np.sum(probs * np.log2(probs))
    return entropy, props

entropy_A, props_A = calculate_entropy(currier_suffix_counts['A'])
entropy_B, props_B = calculate_entropy(currier_suffix_counts['B'])

print("\n" + "="*80)
print("CURRIER A (PHASE M MORPHOLOGY)")
print("="*80)
print(f"Tokens: {tokens_processed['A']:,}")
print(f"Entropy: {entropy_A:.3f} bits")
print("\nSuffix distribution:")
for suffix in ['y', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am', 'NULL']:
    if suffix in props_A:
        count = currier_suffix_counts['A'][suffix]
        print(f"  {suffix:4s}: {props_A[suffix]*100:5.1f}% ({count:,})")

print("\n" + "="*80)
print("CURRIER B (PHASE M MORPHOLOGY)")
print("="*80)
print(f"Tokens: {tokens_processed['B']:,}")
print(f"Entropy: {entropy_B:.3f} bits")
print("\nSuffix distribution:")
for suffix in ['y', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am', 'NULL']:
    if suffix in props_B:
        count = currier_suffix_counts['B'][suffix]
        print(f"  {suffix:4s}: {props_B[suffix]*100:5.1f}% ({count:,})")

print("\n" + "="*80)
print("COMPARISON")
print("="*80)
print("\nPaper values:")
print("  A: 2.578 bits, y=37.3%")
print("  B: 2.017 bits, y=60.8%")
print("  Δ: 0.561 bits")
print("\nSimple suffix extraction:")
print("  A: 2.685 bits, y=29.5%")
print("  B: 2.468 bits, y=44.9%")
print("  Δ: 0.217 bits")
print("\nPhase M morphology:")
print(f"  A: {entropy_A:.3f} bits, y={props_A.get('y', 0)*100:.1f}%")
print(f"  B: {entropy_B:.3f} bits, y={props_B.get('y', 0)*100:.1f}%")
print(f"  Δ: {entropy_A - entropy_B:.3f} bits")

# Check which is closest to paper
simple_error = abs(2.685 - 2.578) + abs(2.468 - 2.017)
phaseM_error = abs(entropy_A - 2.578) + abs(entropy_B - 2.017)

print(f"\nTotal error from paper values:")
print(f"  Simple extraction: {simple_error:.3f}")
print(f"  Phase M morphology: {phaseM_error:.3f}")

if phaseM_error < simple_error:
    print("\n✓ Phase M morphology is CLOSER to paper values!")
else:
    print("\n✓ Simple extraction is closer to paper values")

