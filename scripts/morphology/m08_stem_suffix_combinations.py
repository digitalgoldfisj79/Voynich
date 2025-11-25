#!/usr/bin/env python3
"""
M08: Stem-Suffix Combination Rules

Analyzes which stems combine with which suffixes.
This reveals morphological constraints and formation rules.

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m08_stem_suffix_combinations.tsv

Methodology:
1. For each stem, identify which suffixes it takes
2. For each suffix, identify which stems it attaches to
3. Identify forbidden/required combinations
4. Calculate combination productivity

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT = BASE / "PhaseT/out/t03_enriched_translations.tsv"
OUTPUT = BASE / "PhaseM/out/m08_stem_suffix_combinations.tsv"

print("="*80)
print("M08: STEM-SUFFIX COMBINATION RULES")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')

# Extract stem-suffix pairs
print("\nAnalyzing stem-suffix combinations...")

stem_suffix_counts = defaultdict(lambda: defaultdict(int))
stem_totals = defaultdict(int)
suffix_totals = defaultdict(int)

for _, row in df.iterrows():
    token = str(row['token'])
    stem = str(row['stem'])
    
    if pd.isna(stem) or stem == 'nan':
        continue
    
    # Extract suffix
    if token.startswith(stem):
        suffix = token[len(stem):]
        if suffix == '':
            suffix = 'NULL'
        
        stem_suffix_counts[stem][suffix] += 1
        stem_totals[stem] += 1
        suffix_totals[suffix] += 1

# Get all suffixes
all_suffixes = sorted(suffix_totals.keys())

print(f"\nFound {len(stem_totals)} stems")
print(f"Found {len(all_suffixes)} suffixes")

# Which stems take which suffixes?
print(f"\n{'='*80}")
print("SUFFIX VERSATILITY")
print("="*80)

for suffix in all_suffixes:
    stem_count = sum(1 for stem in stem_suffix_counts if suffix in stem_suffix_counts[stem])
    token_count = suffix_totals[suffix]
    avg_per_stem = token_count / stem_count if stem_count > 0 else 0
    
    print(f"\n{suffix}:")
    print(f"  Attaches to {stem_count} different stems")
    print(f"  Total occurrences: {token_count}")
    print(f"  Average per stem: {avg_per_stem:.2f}")

# Which suffixes do top stems take?
print(f"\n{'='*80}")
print("TOP 20 STEMS: SUFFIX PREFERENCES")
print("="*80)

top_stems = sorted(stem_totals.items(), key=lambda x: x[1], reverse=True)[:20]

for stem, total in top_stems:
    print(f"\n{stem} ({total} tokens):")
    suffix_dist = stem_suffix_counts[stem]
    
    # Sort by frequency
    sorted_suffixes = sorted(suffix_dist.items(), key=lambda x: x[1], reverse=True)
    
    # Show all suffixes this stem takes
    for suffix, count in sorted_suffixes:
        pct = count / total * 100
        print(f"  {suffix:8s}: {count:4d} ({pct:5.1f}%)")

# Create combination matrix
print(f"\n{'='*80}")
print("CREATING STEM-SUFFIX MATRIX")
print("="*80)

# For top 100 stems, create matrix
top_100_stems = [stem for stem, _ in sorted(stem_totals.items(), key=lambda x: x[1], reverse=True)[:100]]

matrix_data = []
for stem in top_100_stems:
    row = {'stem': stem, 'total': stem_totals[stem]}
    for suffix in all_suffixes:
        row[f'suffix_{suffix}'] = stem_suffix_counts[stem].get(suffix, 0)
    matrix_data.append(row)

matrix_df = pd.DataFrame(matrix_data)

# Save matrix
matrix_file = OUTPUT.parent / "m08_stem_suffix_matrix_top100.tsv"
matrix_df.to_csv(matrix_file, sep='\t', index=False)
print(f"✓ Saved matrix: {matrix_file}")

# Identify restricted combinations
print(f"\n{'='*80}")
print("MORPHOLOGICAL RESTRICTIONS")
print("="*80)

print("\nStems that ONLY appear with NULL (no suffixes):")
null_only = [stem for stem in stem_totals if 
             len(stem_suffix_counts[stem]) == 1 and 
             'NULL' in stem_suffix_counts[stem] and
             stem_totals[stem] > 5]

if null_only:
    for stem in null_only[:10]:
        print(f"  {stem:10s}: {stem_totals[stem]} tokens, NULL only")
else:
    print("  None found")

print("\nStems that NEVER appear with NULL (always suffixed):")
never_null = [stem for stem in stem_totals if 
              'NULL' not in stem_suffix_counts[stem] and
              stem_totals[stem] > 5]

if never_null:
    for stem in never_null[:10]:
        print(f"  {stem:10s}: {stem_totals[stem]} tokens, always suffixed")
else:
    print("  None found")

# Save detailed combinations
print(f"\n{'='*80}")
print("SAVING DETAILED COMBINATIONS")
print("="*80)

results = []
for stem in stem_totals:
    for suffix in all_suffixes:
        count = stem_suffix_counts[stem].get(suffix, 0)
        if count > 0:
            results.append({
                'stem': stem,
                'suffix': suffix,
                'count': count,
                'stem_total': stem_totals[stem],
                'proportion': count / stem_totals[stem]
            })

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"✓ Saved: {OUTPUT}")

print(f"\nNext step: Run m09_structural_vs_content.py")
