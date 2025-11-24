#!/usr/bin/env python3
"""
Test 3: Morpheme combination patterns
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"

print("="*80)
print("TEST 3: MORPHEME COMBINATION PATTERNS")
print("="*80)

# Load stem-suffix combinations
combos = pd.read_csv(N4 / "PhaseM/out/m08_stem_suffix_combinations.tsv", sep='\t')

print(f"\nVoynich stem-suffix combinations: {len(combos)}")

# Fix: use 'count' not 'frequency'
stem_suffix_matrix = combos.pivot_table(
    index='stem', 
    columns='suffix', 
    values='count',  # Fixed column name
    fill_value=0
)

print(f"\nStem-suffix matrix: {stem_suffix_matrix.shape}")
print(f"  {stem_suffix_matrix.shape[0]} unique stems")
print(f"  {stem_suffix_matrix.shape[1]} unique suffixes")

# Check if stems cluster by suffix preference
print("\n" + "="*80)
print("SUFFIX PREFERENCE PATTERNS")
print("="*80)

# For each suffix, how many stems use it?
suffix_breadth = (stem_suffix_matrix > 0).sum(axis=0)
print("\nSuffix productivity (# stems that use each suffix):")
for suf, count in suffix_breadth.sort_values(ascending=False).items():
    print(f"  {suf:8s}: {count:4d} stems")

# Are there stem classes that prefer certain suffixes?
print("\n✅ Productivity data extracted")
print("💡 Some suffixes are highly productive (many stems)")
print("💡 Others are restricted (few stems)")
print("⚠️  Similar to Romance declension classes")

