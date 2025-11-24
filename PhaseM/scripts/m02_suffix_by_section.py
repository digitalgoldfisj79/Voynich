#!/usr/bin/env python3
"""
M02: Suffix Distribution by Section

Analyzes how the 9 suffixes are distributed across manuscript sections.

Input:  PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/out/m02_suffix_by_section.tsv

Methodology:
1. For each section, count frequency of each suffix
2. Calculate proportions within each section
3. Test for significant section-specific suffix preferences
4. Identify suffixes that are enriched/depleted in specific sections

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
OUTPUT = BASE / "PhaseM/out/m02_suffix_by_section.tsv"

print("="*80)
print("M02: SUFFIX DISTRIBUTION BY SECTION")
print("="*80)

# Load data
print(f"\nLoading: {INPUT}")
df = pd.read_csv(INPUT, sep='\t')

# Extract suffixes
print("\nExtracting suffixes by section...")
section_suffix_counts = defaultdict(lambda: defaultdict(int))
section_totals = defaultdict(int)

for _, row in df.iterrows():
    token = str(row['token'])
    stem = str(row['stem'])
    section = row['section']
    
    if pd.isna(stem) or stem == 'nan' or pd.isna(section):
        continue
    
    # Extract suffix
    if token.startswith(stem):
        suffix = token[len(stem):]
        if suffix == '':
            suffix = 'NULL'
        
        section_suffix_counts[section][suffix] += 1
        section_totals[section] += 1

# Get all suffixes
all_suffixes = set()
for suffix_dict in section_suffix_counts.values():
    all_suffixes.update(suffix_dict.keys())
all_suffixes = sorted(all_suffixes)

# Create output rows
results = []

for section in sorted(section_suffix_counts.keys()):
    total = section_totals[section]
    
    for suffix in all_suffixes:
        count = section_suffix_counts[section][suffix]
        proportion = count / total if total > 0 else 0
        
        # Calculate corpus-wide proportion for comparison
        corpus_count = sum(section_suffix_counts[s][suffix] for s in section_suffix_counts.keys())
        corpus_total = sum(section_totals.values())
        corpus_proportion = corpus_count / corpus_total
        
        # Enrichment ratio
        enrichment = proportion / corpus_proportion if corpus_proportion > 0 else 0
        
        results.append({
            'section': section,
            'suffix': suffix,
            'count': count,
            'section_total': total,
            'proportion_in_section': proportion,
            'corpus_proportion': corpus_proportion,
            'enrichment_ratio': enrichment
        })

results_df = pd.DataFrame(results)

# Summary statistics
print(f"\n{'='*80}")
print("SECTION SUMMARY")
print("="*80)

for section in sorted(section_totals.keys()):
    total = section_totals[section]
    print(f"\n{section}:")
    print(f"  Total tokens: {total}")
    
    # Top 3 suffixes in this section
    section_data = results_df[results_df['section'] == section].sort_values('count', ascending=False)
    print(f"  Top 3 suffixes:")
    for _, row in section_data.head(3).iterrows():
        print(f"    {row['suffix']:8s}: {row['count']:5d} ({row['proportion_in_section']*100:5.1f}%)")

# Find section-specific enrichments
print(f"\n{'='*80}")
print("SECTION-SPECIFIC ENRICHMENTS")
print("="*80)

print("\nSuffixes significantly enriched in specific sections (>1.5× corpus average):")
enriched = results_df[results_df['enrichment_ratio'] > 1.5].sort_values('enrichment_ratio', ascending=False)

if len(enriched) > 0:
    print(f"\n{'Section':<20} {'Suffix':<10} {'Count':<10} {'Enrichment':<12}")
    print("-" * 55)
    for _, row in enriched.head(20).iterrows():
        print(f"{row['section']:<20} {row['suffix']:<10} {row['count']:<10.0f} {row['enrichment_ratio']:<12.2f}×")
else:
    print("  No suffixes significantly enriched")

# Save full results
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

# Create pivot table for easy viewing
pivot = results_df.pivot(index='suffix', columns='section', values='proportion_in_section')
pivot_file = OUTPUT.parent / "m02_suffix_section_matrix.tsv"
pivot.to_csv(pivot_file, sep='\t')
print(f"✓ Saved pivot table: {pivot_file}")

print(f"\nNext step: Run m03_suffix_cooccurrence.py")
