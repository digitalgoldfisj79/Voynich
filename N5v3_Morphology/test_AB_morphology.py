#!/usr/bin/env python3
"""
CURRIER A/B MORPHOLOGICAL SPLIT
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
ATTIC = BASE.parent / "ATTIC/PhaseS_dir/out"

print("="*80)
print("CURRIER A/B MORPHOLOGICAL ANALYSIS")
print("="*80)

# Section to Currier mapping (from hand analysis)
section_to_currier = {
    'Herbal': 'A',           # Hand 1 - 100% Currier A
    'Astronomical': 'B',     # Hand 2 - 100% Currier B
    'Biological': 'B',       # Hand 2 - 100% Currier B
    'Pharmaceutical': 'B',   # Hand 3 - 92% Currier B
    'Recipes': 'B',          # Hand 3 - 92% Currier B
}

print("\nSection → Currier mapping:")
for section, currier in section_to_currier.items():
    print(f"  {section:15s} → Currier {currier}")

# Load stem-by-section (has section column)
stems_section = pd.read_csv(N4 / "PhaseM/out/m07_stem_by_section.tsv", sep='\t')
print(f"\n✓ Loaded {len(stems_section)} stem-section entries")
print(f"  Columns: {list(stems_section.columns)}")

# Map to Currier
stems_section['currier'] = stems_section['section'].map(section_to_currier)

# Load stem-suffix combinations
combos = pd.read_csv(N4 / "PhaseM/out/m08_stem_suffix_combinations.tsv", sep='\t')
print(f"\n✓ Loaded {len(combos)} stem-suffix combinations")
print(f"  Columns: {list(combos.columns)}")

# Get stem-to-dominant-section mapping
stem_to_section = stems_section.loc[stems_section.groupby('stem')['count'].idxmax()]
stem_to_currier = dict(zip(stem_to_section['stem'], stem_to_section['currier']))

# Map stem-suffix combos to Currier via stem
combos['currier'] = combos['stem'].map(stem_to_currier)

print(f"\nDistribution by Currier:")
print(combos['currier'].value_counts())

# Calculate suffix distributions
print("\n" + "="*80)
print("SUFFIX DISTRIBUTIONS BY CURRIER HAND")
print("="*80)

def entropy(probs):
    probs = np.array(probs)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

for currier in ['A', 'B']:
    subset = combos[combos['currier'] == currier]
    
    if len(subset) == 0:
        continue
    
    suffix_counts = subset.groupby('suffix')['count'].sum().sort_values(ascending=False)
    total = suffix_counts.sum()
    probs = suffix_counts / total
    H = entropy(probs)
    
    print(f"\nCURRIER {currier} ({currier == 'A' and 'HERBAL - LATIN-LIKE?' or 'OTHER - VERNACULAR?'}):")
    print(f"  Tokens: {total:,}")
    print(f"  Suffix types: {len(suffix_counts)}")
    print(f"  Entropy: {H:.3f} bits")
    
    for suf, cnt in suffix_counts.head(8).items():
        pct = cnt / total * 100
        bar = "█" * int(pct / 2)
        print(f"    {str(suf):8s} {pct:5.1f}% {bar}")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)

print("\n✅ If hypothesis is correct:")
print("  • Currier A (Herbal) should have LOWER entropy (more diverse)")
print("  • Currier B (Other) should have HIGHER peaked distribution")
print("  • Overall = weighted average")

print("\n✅ Complete")

