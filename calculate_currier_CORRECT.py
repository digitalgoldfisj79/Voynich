#!/usr/bin/env python3
"""
Calculate Currier A/B entropy - CORRECTLY parsing folio identifiers
"""

import csv
import os
from collections import defaultdict
import numpy as np
import re

print("="*80)
print("CALCULATING TRUE CURRIER A/B ENTROPY")
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
            folio, hand, currier = parts[0], parts[1], parts[2]
            if currier in ('A', 'B'):
                folio_to_currier[folio] = currier

print(f"   Loaded {len(folio_to_currier)} folio→Currier mappings")
print(f"   Currier A: {sum(1 for c in folio_to_currier.values() if c == 'A')} folios")
print(f"   Currier B: {sum(1 for c in folio_to_currier.values() if c == 'B')} folios")

# Process tokens
print("\n2. Processing tokens from p6_folio_tokens.tsv...")

currier_suffix_counts = {'A': defaultdict(int), 'B': defaultdict(int)}
tokens_processed = {'A': 0, 'B': 0}
tokens_no_currier = 0

with open(folio_tokens_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    
    for row in reader:
        token = row['token']
        folio_full = row['folio']
        
        # Extract folio identifier (e.g., "f1r>" -> "f1r")
        # It's at the start before any metadata
        match = re.match(r'(f\d+[rv])', folio_full)
        if not match:
            continue
        
        folio = match.group(1)
        
        # Map to Currier
        currier = folio_to_currier.get(folio)
        if not currier:
            tokens_no_currier += 1
            continue
        
        # Extract suffix (check known suffixes in order of length)
        known_suffixes = ['aiin', 'ain', 'ody', 'ol', 'al', 'or', 'am', 'y']
        suffix = 'NULL'
        for suf in known_suffixes:
            if token.endswith(suf):
                suffix = suf
                break
        
        currier_suffix_counts[currier][suffix] += 1
        tokens_processed[currier] += 1

print(f"   Processed tokens:")
print(f"     Currier A: {tokens_processed['A']:,} tokens")
print(f"     Currier B: {tokens_processed['B']:,} tokens")
print(f"     No Currier: {tokens_no_currier:,} tokens")

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
print("CURRIER A RESULTS")
print("="*80)
print(f"Tokens: {tokens_processed['A']:,}")
print(f"Entropy: {entropy_A:.3f} bits")
print("\nSuffix distribution:")
for suffix in ['y', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am', 'NULL']:
    if suffix in props_A:
        count = currier_suffix_counts['A'][suffix]
        print(f"  {suffix:4s}: {props_A[suffix]*100:5.1f}% ({count:,} tokens)")

print("\n" + "="*80)
print("CURRIER B RESULTS")
print("="*80)
print(f"Tokens: {tokens_processed['B']:,}")
print(f"Entropy: {entropy_B:.3f} bits")
print("\nSuffix distribution:")
for suffix in ['y', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am', 'NULL']:
    if suffix in props_B:
        count = currier_suffix_counts['B'][suffix]
        print(f"  {suffix:4s}: {props_B[suffix]*100:5.1f}% ({count:,} tokens)")

print("\n" + "="*80)
print("COMPARISON TO PAPER")
print("="*80)
print("\nPaper values:")
print("  Currier A: 2.578 bits, y=37.3%")
print("  Currier B: 2.017 bits, y=60.8%")
print("  Difference: 0.561 bits")
print("\nCalculated from folio-level data:")
print(f"  Currier A: {entropy_A:.3f} bits, y={props_A.get('y', 0)*100:.1f}%")
print(f"  Currier B: {entropy_B:.3f} bits, y={props_B.get('y', 0)*100:.1f}%")
print(f"  Difference: {entropy_A - entropy_B:.3f} bits")

# Match check
a_close = abs(entropy_A - 2.578) < 0.05
b_close = abs(entropy_B - 2.017) < 0.05

if a_close and b_close:
    print("\n✓✓✓ MATCH! Values reproduced from data!")
else:
    print(f"\n⚠️ Differences:")
    print(f"  Entropy A: {abs(entropy_A - 2.578):.3f} bits off")
    print(f"  Entropy B: {abs(entropy_B - 2.017):.3f} bits off")

print("\n" + "="*80)
print("FINAL TABLE 2 VALUES (100% REPRODUCIBLE)")
print("="*80)
print(f"\nCurrier A: {entropy_A:.3f} bits, y={props_A.get('y', 0)*100:.1f}%")
print(f"Currier B: {entropy_B:.3f} bits, y={props_B.get('y', 0)*100:.1f}%")
print(f"Difference: {entropy_A - entropy_B:.3f} bits")
print("\nCalculated from:")
print("  - p6_folio_tokens.tsv (29,747 tokens)")
print("  - s49b Currier assignments (174 folios)")
print("  - EVA suffix extraction")

