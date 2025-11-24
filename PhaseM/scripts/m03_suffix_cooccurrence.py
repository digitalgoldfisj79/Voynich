#!/usr/bin/env python3
"""
M03: Suffix Co-occurrence Patterns

Analyzes which suffixes appear together in the same context (line/folio).

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m03_suffix_cooccurrence_matrix.tsv

Methodology:
1. For each line, identify which suffixes appear
2. Count co-occurrence of suffix pairs
3. Calculate observed vs expected co-occurrence
4. Identify suffix pairs that cluster or avoid each other

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT = BASE / "PhaseT/out/t03_enriched_translations.tsv"
OUTPUT = BASE / "PhaseM/out/m03_suffix_cooccurrence_matrix.tsv"

print("="*80)
print("M03: SUFFIX CO-OCCURRENCE PATTERNS")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')

# Extract suffixes by line
print("\nExtracting suffixes by line...")
line_suffixes = defaultdict(list)

for _, row in df.iterrows():
    token = str(row['token'])
    stem = str(row['stem'])
    line_id = f"{row['folio_norm']}_{row['line']}"
    
    if pd.isna(stem) or stem == 'nan':
        continue
    
    # Extract suffix
    if token.startswith(stem):
        suffix = token[len(stem):]
        if suffix == '':
            suffix = 'NULL'
        line_suffixes[line_id].append(suffix)

# Get all suffixes
all_suffixes = set()
for suffixes in line_suffixes.values():
    all_suffixes.update(suffixes)
all_suffixes = sorted(all_suffixes)

print(f"\nFound {len(all_suffixes)} unique suffixes")
print(f"Analyzing {len(line_suffixes)} lines")

# Count individual suffix frequencies
suffix_counts = Counter()
for suffixes in line_suffixes.values():
    suffix_counts.update(set(suffixes))  # Count each suffix once per line

# Count co-occurrences
cooccur_counts = defaultdict(int)

for suffixes in line_suffixes.values():
    unique_suffixes = list(set(suffixes))
    # Count pairs
    for i, suff1 in enumerate(unique_suffixes):
        for suff2 in unique_suffixes[i+1:]:
            pair = tuple(sorted([suff1, suff2]))
            cooccur_counts[pair] += 1

# Calculate expected co-occurrence (if independent)
total_lines = len(line_suffixes)
results = []

for suff1 in all_suffixes:
    for suff2 in all_suffixes:
        if suff1 >= suff2:  # Only upper triangle
            continue
        
        pair = tuple(sorted([suff1, suff2]))
        observed = cooccur_counts[pair]
        
        # Expected = P(suff1) * P(suff2) * N_lines
        p1 = suffix_counts[suff1] / total_lines
        p2 = suffix_counts[suff2] / total_lines
        expected = p1 * p2 * total_lines
        
        # Ratio
        ratio = observed / expected if expected > 0 else 0
        
        results.append({
            'suffix1': suff1,
            'suffix2': suff2,
            'observed': observed,
            'expected': expected,
            'ratio': ratio,
            'freq1': suffix_counts[suff1],
            'freq2': suffix_counts[suff2]
        })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('ratio', ascending=False)

# Summary
print(f"\n{'='*80}")
print("CO-OCCURRENCE SUMMARY")
print("="*80)

print("\nSuffix pairs that co-occur MORE than expected (ratio > 1.5):")
high_cooccur = results_df[results_df['ratio'] > 1.5]
if len(high_cooccur) > 0:
    print(f"\n{'Suffix 1':<10} {'Suffix 2':<10} {'Observed':<10} {'Expected':<10} {'Ratio':<10}")
    print("-" * 55)
    for _, row in high_cooccur.head(15).iterrows():
        print(f"{row['suffix1']:<10} {row['suffix2']:<10} {row['observed']:<10.0f} {row['expected']:<10.1f} {row['ratio']:<10.2f}")
else:
    print("  None found")

print("\nSuffix pairs that co-occur LESS than expected (ratio < 0.5):")
low_cooccur = results_df[results_df['ratio'] < 0.5]
if len(low_cooccur) > 0:
    print(f"\n{'Suffix 1':<10} {'Suffix 2':<10} {'Observed':<10} {'Expected':<10} {'Ratio':<10}")
    print("-" * 55)
    for _, row in low_cooccur.head(15).iterrows():
        print(f"{row['suffix1']:<10} {row['suffix2']:<10} {row['observed']:<10.0f} {row['expected']:<10.1f} {row['ratio']:<10.2f}")
else:
    print("  None found")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

# Create square matrix for visualization
matrix = pd.DataFrame(0.0, index=all_suffixes, columns=all_suffixes)
for _, row in results_df.iterrows():
    matrix.loc[row['suffix1'], row['suffix2']] = row['ratio']
    matrix.loc[row['suffix2'], row['suffix1']] = row['ratio']  # Symmetric

matrix_file = OUTPUT.parent / "m03_cooccurrence_ratio_matrix.tsv"
matrix.to_csv(matrix_file, sep='\t')
print(f"✓ Saved matrix: {matrix_file}")

print(f"\nNext step: Run m04_suffix_positions.py")
