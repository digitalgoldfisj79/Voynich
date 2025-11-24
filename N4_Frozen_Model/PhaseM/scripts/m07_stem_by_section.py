#!/usr/bin/env python3
"""
M07: Stem Distribution by Section

Analyzes how stems are distributed across manuscript sections.

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m07_stem_by_section.tsv

Methodology:
1. For each section, identify unique stems and their frequencies
2. Calculate section-specific vocabularies
3. Identify stems enriched/depleted in specific sections
4. Measure vocabulary overlap between sections

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
OUTPUT = BASE / "PhaseM/out/m07_stem_by_section.tsv"

print("="*80)
print("M07: STEM DISTRIBUTION BY SECTION")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')

# Filter out rows without section
df_with_section = df[df['section'].notna()].copy()

print(f"Tokens with section labels: {len(df_with_section)}")

# Count stems per section
section_stem_counts = defaultdict(lambda: defaultdict(int))
section_totals = defaultdict(int)

for _, row in df_with_section.iterrows():
    stem = str(row['stem'])
    section = row['section']
    
    if pd.isna(stem) or stem == 'nan':
        continue
    
    section_stem_counts[section][stem] += 1
    section_totals[section] += 1

# Get all stems
all_stems = set()
for stem_dict in section_stem_counts.values():
    all_stems.update(stem_dict.keys())

print(f"\nTotal unique stems: {len(all_stems)}")

# Section vocabulary sizes
print(f"\n{'='*80}")
print("SECTION VOCABULARY SIZES")
print("="*80)

for section in sorted(section_totals.keys()):
    unique_stems = len(section_stem_counts[section])
    total_tokens = section_totals[section]
    ttr = unique_stems / total_tokens if total_tokens > 0 else 0
    
    print(f"\n{section}:")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Unique stems: {unique_stems}")
    print(f"  Type-token ratio: {ttr:.4f}")

# Top stems per section
print(f"\n{'='*80}")
print("TOP 10 STEMS PER SECTION")
print("="*80)

for section in sorted(section_stem_counts.keys()):
    print(f"\n{section}:")
    sorted_stems = sorted(section_stem_counts[section].items(), key=lambda x: x[1], reverse=True)
    for i, (stem, count) in enumerate(sorted_stems[:10]):
        pct = count / section_totals[section] * 100
        print(f"  {i+1:2d}. {stem:10s}: {count:4d} ({pct:5.2f}%)")

# Calculate enrichment for all stem-section pairs
print(f"\n{'='*80}")
print("CALCULATING ENRICHMENT SCORES")
print("="*80)

results = []
corpus_total = sum(section_totals.values())

for section in section_stem_counts:
    section_total = section_totals[section]
    
    for stem in all_stems:
        count = section_stem_counts[section].get(stem, 0)
        
        if count == 0:
            continue
        
        # Section proportion
        section_prop = count / section_total
        
        # Corpus proportion
        corpus_count = sum(section_stem_counts[s].get(stem, 0) for s in section_stem_counts)
        corpus_prop = corpus_count / corpus_total
        
        # Enrichment ratio
        enrichment = section_prop / corpus_prop if corpus_prop > 0 else 0
        
        results.append({
            'section': section,
            'stem': stem,
            'count': count,
            'section_total': section_total,
            'proportion_in_section': section_prop,
            'corpus_proportion': corpus_prop,
            'enrichment_ratio': enrichment
        })

results_df = pd.DataFrame(results)

# Highly enriched stems per section
print(f"\nHighly enriched stems per section (ratio > 3.0):")

for section in sorted(section_totals.keys()):
    section_data = results_df[
        (results_df['section'] == section) & 
        (results_df['enrichment_ratio'] > 3.0) &
        (results_df['count'] > 5)  # At least 5 occurrences
    ].sort_values('enrichment_ratio', ascending=False)
    
    if len(section_data) > 0:
        print(f"\n{section}:")
        for _, row in section_data.head(10).iterrows():
            print(f"  {row['stem']:10s}: {row['count']:3.0f} tokens, {row['enrichment_ratio']:5.2f}× enrichment")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\nNext step: Run m08_stem_suffix_combinations.py")
