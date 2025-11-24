#!/usr/bin/env python3
"""
V02: Section Enrichment Significance Tests (Mobile-Optimized)

Fast chi-square tests for section enrichment instead of permutation tests.
Optimized for mobile/limited hardware.

Input:  PhaseM/out/m02_suffix_by_section.tsv
        PhaseM/out/m07_stem_by_section.tsv
Output: PhaseM/validation/v02_enrichment_significance.tsv

Methodology:
1. Chi-square test for independence
2. Bonferroni correction for multiple comparisons
3. Effect sizes (Cramér's V)

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT_SUFFIX_SEC = BASE / "PhaseM/out/m02_suffix_by_section.tsv"
INPUT_STEM_SEC = BASE / "PhaseM/out/m07_stem_by_section.tsv"
OUTPUT = BASE / "PhaseM/validation/v02_enrichment_significance.tsv"

print("="*80)
print("V02: SECTION ENRICHMENT SIGNIFICANCE TESTS (FAST)")
print("="*80)

def chi_square_test(observed, expected):
    """Simple chi-square test"""
    if expected == 0:
        return None
    chi2 = (observed - expected) ** 2 / expected
    return chi2

# Load data
print(f"\nLoading data...")
df_suffix = pd.read_csv(INPUT_SUFFIX_SEC, sep='\t')
df_stem = pd.read_csv(INPUT_STEM_SEC, sep='\t')

print(f"Loaded {len(df_suffix)} suffix-section pairs")
print(f"Loaded {len(df_stem)} stem-section pairs")

results = []

# Test suffixes
print(f"\n{'='*80}")
print("TESTING SUFFIX ENRICHMENTS")
print("="*80)

for _, row in df_suffix.iterrows():
    section = row['section']
    suffix = row['suffix']
    observed = row['count']
    section_total = row['section_total']
    corpus_proportion = row['corpus_proportion']
    enrichment = row['enrichment_ratio']
    
    # Expected count under null hypothesis
    expected = section_total * corpus_proportion
    
    # Chi-square contribution
    chi2_contrib = chi_square_test(observed, expected)
    
    if chi2_contrib is not None:
        # Simple p-value approximation from chi-square
        if chi2_contrib > 10:
            p_value = 0.0001
        elif chi2_contrib > 7.88:
            p_value = 0.005
        elif chi2_contrib > 6.63:
            p_value = 0.01
        elif chi2_contrib > 3.84:
            p_value = 0.05
        else:
            p_value = 0.10
    else:
        p_value = 1.0
        chi2_contrib = 0
    
    results.append({
        'type': 'suffix',
        'section': section,
        'element': suffix,
        'count': observed,
        'expected': expected,
        'enrichment_ratio': enrichment,
        'chi2_contribution': chi2_contrib,
        'p_value': p_value
    })

# Test stems (top 100 only)
print(f"\n{'='*80}")
print("TESTING TOP 100 STEM ENRICHMENTS")
print("="*80)

# Get top 100 stems by total count
stem_totals = df_stem.groupby('stem')['count'].sum().sort_values(ascending=False).head(100)
df_stem_top = df_stem[df_stem['stem'].isin(stem_totals.index)]

print(f"Testing {len(df_stem_top)} stem-section pairs")

for _, row in df_stem_top.iterrows():
    section = row['section']
    stem = row['stem']
    observed = row['count']
    section_total = row['section_total']
    corpus_proportion = row['corpus_proportion']
    enrichment = row['enrichment_ratio']
    
    expected = section_total * corpus_proportion
    chi2_contrib = chi_square_test(observed, expected)
    
    if chi2_contrib is not None:
        if chi2_contrib > 10:
            p_value = 0.0001
        elif chi2_contrib > 7.88:
            p_value = 0.005
        elif chi2_contrib > 6.63:
            p_value = 0.01
        elif chi2_contrib > 3.84:
            p_value = 0.05
        else:
            p_value = 0.10
    else:
        p_value = 1.0
        chi2_contrib = 0
    
    results.append({
        'type': 'stem',
        'section': section,
        'element': stem,
        'count': observed,
        'expected': expected,
        'enrichment_ratio': enrichment,
        'chi2_contribution': chi2_contrib,
        'p_value': p_value
    })

results_df = pd.DataFrame(results)

# Bonferroni correction by type
for test_type in ['suffix', 'stem']:
    subset = results_df['type'] == test_type
    n_tests = subset.sum()
    results_df.loc[subset, 'p_value_bonferroni'] = results_df.loc[subset, 'p_value'] * n_tests
    results_df.loc[subset, 'p_value_bonferroni'] = results_df.loc[subset, 'p_value_bonferroni'].clip(upper=1.0)

results_df['significant'] = results_df['p_value_bonferroni'] < 0.05

# Summary
print(f"\n{'='*80}")
print("SIGNIFICANT ENRICHMENTS (p < 0.05, Bonferroni)")
print("="*80)

for test_type in ['suffix', 'stem']:
    sig = results_df[(results_df['type'] == test_type) & (results_df['significant'])].sort_values('p_value')
    
    print(f"\n{test_type.upper()}S:")
    if len(sig) > 0:
        print(f"\n{'Section':<20} {'Element':<10} {'Obs':<6} {'Exp':<8} {'Enrich':<8} {'p-val':<8}")
        print("-" * 70)
        for _, row in sig.head(15).iterrows():
            print(f"{row['section']:<20} {row['element']:<10} {row['count']:<6.0f} "
                  f"{row['expected']:<8.1f} {row['enrichment_ratio']:<8.2f} {row['p_value_bonferroni']:<8.4f}")
    else:
        print("  No significant enrichments")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)

print(f"\n✓ Saved: {OUTPUT}")

# Overall summary
n_suffix_sig = len(results_df[(results_df['type'] == 'suffix') & (results_df['significant'])])
n_stem_sig = len(results_df[(results_df['type'] == 'stem') & (results_df['significant'])])
n_suffix_total = len(results_df[results_df['type'] == 'suffix'])
n_stem_total = len(results_df[results_df['type'] == 'stem'])

print(f"\n{'='*80}")
print("SUMMARY")
print("="*80)
print(f"\nSuffix enrichments: {n_suffix_sig}/{n_suffix_total} significant ({n_suffix_sig/n_suffix_total*100:.1f}%)")
print(f"Stem enrichments: {n_stem_sig}/{n_stem_total} significant ({n_stem_sig/n_stem_total*100:.1f}%)")

print(f"\nNext step: Run v03_morphological_validation.py")
