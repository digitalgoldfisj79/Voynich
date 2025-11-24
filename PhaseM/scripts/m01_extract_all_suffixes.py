#!/usr/bin/env python3
"""
M01: Extract All Suffixes

Extracts complete suffix inventory from the Voynich corpus.

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m01_suffix_inventory.tsv

Methodology:
1. For each token, extract suffix = token minus stem
2. Count frequency of each suffix
3. Calculate statistics (type count, token count, type-token ratio)
4. Identify null suffixes (stem-only words)

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT = BASE / "PhaseT/out/t03_enriched_translations.tsv"
OUTPUT = BASE / "PhaseM/out/m01_suffix_inventory.tsv"

print("="*80)
print("M01: EXTRACT ALL SUFFIXES")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')
print(f"Loaded {len(df)} tokens")

# Extract suffixes
print("\nExtracting suffixes...")
suffixes = []
suffix_examples = {}  # Store examples for each suffix

for _, row in df.iterrows():
    token = str(row['token'])
    stem = str(row['stem'])
    
    if pd.isna(stem) or stem == 'nan':
        continue
    
    # Suffix = token minus stem
    if token.startswith(stem):
        suffix = token[len(stem):]
        if suffix == '':
            suffix = 'NULL'  # Stem-only word
        suffixes.append(suffix)
        
        # Store example
        if suffix not in suffix_examples:
            suffix_examples[suffix] = []
        if len(suffix_examples[suffix]) < 5:  # Keep up to 5 examples
            suffix_examples[suffix].append(f"{stem}+{suffix if suffix != 'NULL' else '∅'}")
    else:
        # Shouldn't happen if stem extraction is correct
        suffixes.append('ERROR')

# Count suffix frequencies
suffix_counts = Counter(suffixes)

print(f"\nFound {len(suffix_counts)} unique suffixes")
print(f"Total suffix tokens: {len(suffixes)}")

# Create output dataframe
results = []
for suffix, count in suffix_counts.most_common():
    examples = '; '.join(suffix_examples.get(suffix, [])[:3])  # Top 3 examples
    results.append({
        'suffix': suffix,
        'token_count': count,
        'frequency': count / len(suffixes),
        'cumulative_frequency': 0,  # Will calculate below
        'rank': len(results) + 1,
        'examples': examples
    })

results_df = pd.DataFrame(results)

# Calculate cumulative frequency
results_df['cumulative_frequency'] = results_df['frequency'].cumsum()

# Calculate type-token ratio
ttr = len(suffix_counts) / len(suffixes)
print(f"\nType-token ratio: {ttr:.4f}")

# Statistics
print(f"\nSuffix statistics:")
print(f"  Mean frequency: {results_df['frequency'].mean():.6f}")
print(f"  Median frequency: {results_df['frequency'].median():.6f}")
print(f"  Top 10 suffixes cover: {results_df.head(10)['frequency'].sum()*100:.1f}%")
print(f"  Top 50 suffixes cover: {results_df.head(50)['frequency'].sum()*100:.1f}%")

# Suffix length distribution
suffix_lengths = [len(s) for s in suffix_counts.keys() if s not in ['NULL', 'ERROR']]
if suffix_lengths:
    print(f"\nSuffix length statistics:")
    print(f"  Mean length: {np.mean(suffix_lengths):.2f} characters")
    print(f"  Median length: {np.median(suffix_lengths):.0f} characters")
    print(f"  Range: {min(suffix_lengths)}-{max(suffix_lengths)} characters")

# Show top 20
print(f"\nTop 20 suffixes:")
print(results_df[['suffix', 'token_count', 'frequency', 'examples']].head(20).to_string(index=False))

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\nNext step: Run m02_suffix_frequencies.py")
