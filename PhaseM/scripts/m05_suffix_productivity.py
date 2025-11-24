#!/usr/bin/env python3
"""
M05: Suffix Productivity Metrics

Analyzes which suffixes are productive (appear with many stems) vs. frozen (limited stems).

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m05_suffix_productivity.tsv

Methodology:
1. For each suffix, count how many unique stems it appears with
2. Calculate type-token ratio (productivity measure)
3. Identify highly productive vs. frozen suffixes

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
OUTPUT = BASE / "PhaseM/out/m05_suffix_productivity.tsv"

print("="*80)
print("M05: SUFFIX PRODUCTIVITY METRICS")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')

# Analyze suffix-stem combinations
print("\nAnalyzing suffix productivity...")

suffix_stems = defaultdict(set)
suffix_tokens = defaultdict(int)

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
        
        suffix_stems[suffix].add(stem)
        suffix_tokens[suffix] += 1

# Calculate statistics
results = []

for suffix in sorted(suffix_stems.keys()):
    type_count = len(suffix_stems[suffix])
    token_count = suffix_tokens[suffix]
    type_token_ratio = type_count / token_count if token_count > 0 else 0
    
    results.append({
        'suffix': suffix,
        'unique_stems': type_count,
        'token_count': token_count,
        'type_token_ratio': type_token_ratio,
        'avg_tokens_per_stem': token_count / type_count if type_count > 0 else 0
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('type_token_ratio', ascending=False)

# Summary
print(f"\n{'='*80}")
print("PRODUCTIVITY SUMMARY")
print("="*80)

print(f"\n{'Suffix':<10} {'Stems':<10} {'Tokens':<10} {'TTR':<10} {'Tokens/Stem':<12}")
print("-" * 55)

for _, row in results_df.iterrows():
    print(f"{row['suffix']:<10} "
          f"{row['unique_stems']:<10.0f} "
          f"{row['token_count']:<10.0f} "
          f"{row['type_token_ratio']:<10.4f} "
          f"{row['avg_tokens_per_stem']:<12.2f}")

# Categorize
print(f"\n{'='*80}")
print("PRODUCTIVITY CATEGORIES")
print("="*80)

print("\nHighly productive suffixes (TTR > 0.5):")
high_prod = results_df[results_df['type_token_ratio'] > 0.5]
if len(high_prod) > 0:
    for _, row in high_prod.iterrows():
        print(f"  {row['suffix']:10s}: {row['unique_stems']:.0f} stems, TTR={row['type_token_ratio']:.4f}")
else:
    print("  None found")

print("\nModerately productive suffixes (0.2 < TTR < 0.5):")
med_prod = results_df[(results_df['type_token_ratio'] > 0.2) & (results_df['type_token_ratio'] <= 0.5)]
if len(med_prod) > 0:
    for _, row in med_prod.iterrows():
        print(f"  {row['suffix']:10s}: {row['unique_stems']:.0f} stems, TTR={row['type_token_ratio']:.4f}")
else:
    print("  None found")

print("\nLow productivity suffixes (TTR < 0.2):")
low_prod = results_df[results_df['type_token_ratio'] <= 0.2]
if len(low_prod) > 0:
    for _, row in low_prod.iterrows():
        print(f"  {row['suffix']:10s}: {row['unique_stems']:.0f} stems, TTR={row['type_token_ratio']:.4f}")
else:
    print("  None found")

# Most common stems for each suffix
print(f"\n{'='*80}")
print("TOP 5 STEMS PER SUFFIX")
print("="*80)

for suffix in sorted(suffix_stems.keys()):
    print(f"\n{suffix}:")
    
    # Count stem frequencies for this suffix
    stem_counts = defaultdict(int)
    for _, row in df.iterrows():
        token = str(row['token'])
        stem = str(row['stem'])
        
        if pd.isna(stem) or stem == 'nan':
            continue
        
        if token.startswith(stem):
            suff = token[len(stem):]
            if suff == '':
                suff = 'NULL'
            
            if suff == suffix:
                stem_counts[stem] += 1
    
    # Show top 5
    for i, (stem, count) in enumerate(sorted(stem_counts.items(), key=lambda x: x[1], reverse=True)[:5]):
        print(f"  {i+1}. {stem:15s}: {count:4d} tokens")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("PHASE 1 COMPLETE")
print("="*80)
print("\nAll Phase 1 outputs saved to PhaseM/out/")
print("Summary files:")
print("  - m01_suffix_inventory.tsv")
print("  - m02_suffix_by_section.tsv")
print("  - m03_suffix_cooccurrence_matrix.tsv")
print("  - m04_suffix_positions.tsv")
print("  - m05_suffix_productivity.tsv")
