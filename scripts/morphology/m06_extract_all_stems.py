#!/usr/bin/env python3
"""
M06: Extract All Stems

Extracts complete stem inventory from the Voynich corpus.

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m06_stem_inventory.tsv

Methodology:
1. Extract all unique stems from corpus
2. Count frequency of each stem
3. Calculate statistics (type count, token count, type-token ratio)
4. Identify most/least common stems

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
OUTPUT = BASE / "PhaseM/out/m06_stem_inventory.tsv"

print("="*80)
print("M06: EXTRACT ALL STEMS")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')
print(f"Loaded {len(df)} tokens")

# Extract stems
print("\nExtracting stems...")
stems = []
stem_examples = {}  # Store example tokens for each stem

for _, row in df.iterrows():
    token = str(row['token'])
    stem = str(row['stem'])
    
    if pd.isna(stem) or stem == 'nan':
        continue
    
    stems.append(stem)
    
    # Store example token
    if stem not in stem_examples:
        stem_examples[stem] = []
    if len(stem_examples[stem]) < 3:
        stem_examples[stem].append(token)

# Count stem frequencies
stem_counts = Counter(stems)

print(f"\nFound {len(stem_counts)} unique stems")
print(f"Total stem tokens: {len(stems)}")

# Create output dataframe
results = []
for stem, count in stem_counts.most_common():
    examples = '; '.join(stem_examples.get(stem, []))
    results.append({
        'stem': stem,
        'token_count': count,
        'frequency': count / len(stems),
        'cumulative_frequency': 0,  # Will calculate below
        'rank': len(results) + 1,
        'example_tokens': examples
    })

results_df = pd.DataFrame(results)

# Calculate cumulative frequency
results_df['cumulative_frequency'] = results_df['frequency'].cumsum()

# Calculate type-token ratio
ttr = len(stem_counts) / len(stems)
print(f"\nType-token ratio: {ttr:.4f}")

# Statistics
print(f"\nStem statistics:")
print(f"  Mean frequency: {results_df['frequency'].mean():.6f}")
print(f"  Median frequency: {results_df['frequency'].median():.6f}")
print(f"  Top 10 stems cover: {results_df.head(10)['frequency'].sum()*100:.1f}%")
print(f"  Top 100 stems cover: {results_df.head(100)['frequency'].sum()*100:.1f}%")
print(f"  Top 500 stems cover: {results_df.head(500)['frequency'].sum()*100:.1f}%")

# Stem length distribution
stem_lengths = [len(s) for s in stem_counts.keys()]
print(f"\nStem length statistics:")
print(f"  Mean length: {np.mean(stem_lengths):.2f} characters")
print(f"  Median length: {np.median(stem_lengths):.0f} characters")
print(f"  Range: {min(stem_lengths)}-{max(stem_lengths)} characters")

# Hapax legomena (stems appearing only once)
hapax = results_df[results_df['token_count'] == 1]
print(f"\nHapax legomena (stems appearing once): {len(hapax)} ({len(hapax)/len(results_df)*100:.1f}%)")

# Show top 30
print(f"\nTop 30 stems:")
print(results_df[['stem', 'token_count', 'frequency', 'example_tokens']].head(30).to_string(index=False))

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\nNext step: Run m07_stem_by_section.py")
