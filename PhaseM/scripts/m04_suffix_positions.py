#!/usr/bin/env python3
"""
M04: Suffix Positional Patterns

Analyzes where suffixes appear in word sequences (folio-initial, medial, final).

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m04_suffix_positions.tsv

Methodology:
1. For each folio, identify position of each suffix (first/middle/last word)
2. Calculate positional preferences for each suffix
3. Test if certain suffixes prefer certain positions

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
OUTPUT = BASE / "PhaseM/out/m04_suffix_positions.tsv"

print("="*80)
print("M04: SUFFIX POSITIONAL PATTERNS")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')

# Group by folio and analyze positions
print("\nAnalyzing suffix positions by folio...")

suffix_positions = defaultdict(lambda: {'initial': 0, 'medial': 0, 'final': 0, 'only': 0})

# Group by folio
for folio in df['folio_norm'].unique():
    folio_data = df[df['folio_norm'] == folio].copy()
    folio_data = folio_data.sort_values('pos')
    
    # Extract suffixes for this folio
    folio_suffixes = []
    for _, row in folio_data.iterrows():
        token = str(row['token'])
        stem = str(row['stem'])
        
        if pd.isna(stem) or stem == 'nan':
            continue
        
        if token.startswith(stem):
            suffix = token[len(stem):]
            if suffix == '':
                suffix = 'NULL'
            folio_suffixes.append(suffix)
    
    if len(folio_suffixes) == 0:
        continue
    
    # Classify positions
    if len(folio_suffixes) == 1:
        suffix_positions[folio_suffixes[0]]['only'] += 1
    else:
        # Initial
        suffix_positions[folio_suffixes[0]]['initial'] += 1
        # Final
        suffix_positions[folio_suffixes[-1]]['final'] += 1
        # Medial
        for suffix in folio_suffixes[1:-1]:
            suffix_positions[suffix]['medial'] += 1

# Calculate statistics
results = []

for suffix in sorted(suffix_positions.keys()):
    counts = suffix_positions[suffix]
    total = sum(counts.values())
    
    if total == 0:
        continue
    
    results.append({
        'suffix': suffix,
        'initial_count': counts['initial'],
        'medial_count': counts['medial'],
        'final_count': counts['final'],
        'only_count': counts['only'],
        'total': total,
        'initial_pct': counts['initial'] / total * 100,
        'medial_pct': counts['medial'] / total * 100,
        'final_pct': counts['final'] / total * 100,
        'only_pct': counts['only'] / total * 100
    })

results_df = pd.DataFrame(results)

# Summary
print(f"\n{'='*80}")
print("POSITIONAL SUMMARY")
print("="*80)

print(f"\n{'Suffix':<10} {'Initial':<10} {'Medial':<10} {'Final':<10} {'Only':<10} {'Total':<10}")
print("-" * 65)

for _, row in results_df.iterrows():
    print(f"{row['suffix']:<10} "
          f"{row['initial_count']:>4.0f} ({row['initial_pct']:>4.1f}%)  "
          f"{row['medial_count']:>4.0f} ({row['medial_pct']:>4.1f}%)  "
          f"{row['final_count']:>4.0f} ({row['final_pct']:>4.1f}%)  "
          f"{row['only_count']:>4.0f} ({row['only_pct']:>4.1f}%)  "
          f"{row['total']:>5.0f}")

# Identify positional preferences
print(f"\n{'='*80}")
print("POSITIONAL PREFERENCES")
print("="*80)

print("\nSuffixes with strong initial preference (>40%):")
initial_pref = results_df[results_df['initial_pct'] > 40].sort_values('initial_pct', ascending=False)
if len(initial_pref) > 0:
    for _, row in initial_pref.iterrows():
        print(f"  {row['suffix']:10s}: {row['initial_pct']:5.1f}%")
else:
    print("  None found")

print("\nSuffixes with strong final preference (>40%):")
final_pref = results_df[results_df['final_pct'] > 40].sort_values('final_pct', ascending=False)
if len(final_pref) > 0:
    for _, row in final_pref.iterrows():
        print(f"  {row['suffix']:10s}: {row['final_pct']:5.1f}%")
else:
    print("  None found")

print("\nSuffixes that appear alone frequently (>30%):")
only_pref = results_df[results_df['only_pct'] > 30].sort_values('only_pct', ascending=False)
if len(only_pref) > 0:
    for _, row in only_pref.iterrows():
        print(f"  {row['suffix']:10s}: {row['only_pct']:5.1f}%")
else:
    print("  None found")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\nNext step: Run m05_suffix_productivity.py")
