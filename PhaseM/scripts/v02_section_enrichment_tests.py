#!/usr/bin/env python3
"""
V02: Section Enrichment Significance Tests

Tests if observed section-specific enrichments are statistically significant
using permutation tests with multiple comparison correction.

Input:  PhaseM/out/m02_suffix_by_section.tsv
        PhaseM/out/m07_stem_by_section.tsv
        PhaseT/out/t03_enriched_translations.tsv
Output: PhaseM/validation/v02_enrichment_significance.tsv

Methodology:
1. Permutation tests (1000 permutations)
2. Calculate p-values for enrichment ratios
3. Bonferroni correction for multiple comparisons
4. Identify truly significant patterns

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT_SUFFIX_SEC = BASE / "PhaseM/out/m02_suffix_by_section.tsv"
INPUT_STEM_SEC = BASE / "PhaseM/out/m07_stem_by_section.tsv"
INPUT_TOKENS = BASE / "PhaseT/out/t03_enriched_translations.tsv"
OUTPUT = BASE / "PhaseM/validation/v02_enrichment_significance.tsv"

N_PERMUTATIONS = 1000
RANDOM_SEED = 42

print("="*80)
print("V02: SECTION ENRICHMENT SIGNIFICANCE TESTS")
print("="*80)

np.random.seed(RANDOM_SEED)

# Load data
print(f"\nLoading data...")
df_tokens = pd.read_csv(INPUT_TOKENS, sep='\t')
df_suffix_sec = pd.read_csv(INPUT_SUFFIX_SEC, sep='\t')
df_stem_sec = pd.read_csv(INPUT_STEM_SEC, sep='\t')

# Filter to tokens with sections
df_tokens = df_tokens[df_tokens['section'].notna()].copy()

print(f"Loaded {len(df_tokens)} tokens with section labels")

def permutation_test_enrichment(df, element_col, n_permutations=1000):
    """
    Permutation test for section enrichment.
    
    Returns: DataFrame with p-values for each element-section pair
    """
    # Get observed enrichment ratios
    observed_enrichments = {}
    
    # Calculate observed statistics
    section_totals = df['section'].value_counts()
    element_counts = defaultdict(lambda: defaultdict(int))
    
    for _, row in df.iterrows():
        element = row[element_col]
        section = row['section']
        if pd.isna(element) or element == 'nan':
            continue
        element_counts[section][element] += 1
    
    # Store observed enrichments
    total_tokens = len(df)
    for section in element_counts:
        section_total = section_totals[section]
        for element in element_counts[section]:
            count = element_counts[section][element]
            section_prop = count / section_total
            
            # Corpus proportion
            corpus_count = sum(element_counts[s].get(element, 0) for s in element_counts)
            corpus_prop = corpus_count / total_tokens
            
            enrichment = section_prop / corpus_prop if corpus_prop > 0 else 0
            observed_enrichments[(section, element)] = {
                'enrichment': enrichment,
                'count': count
            }
    
    # Permutation test
    print(f"  Running {n_permutations} permutations...")
    
    permutation_enrichments = defaultdict(list)
    
    for perm in range(n_permutations):
        if perm % 100 == 0:
            print(f"    Permutation {perm}/{n_permutations}")
        
        # Shuffle sections
        shuffled_sections = df['section'].sample(frac=1, random_state=RANDOM_SEED + perm).values
        
        # Recalculate enrichments with shuffled data
        perm_counts = defaultdict(lambda: defaultdict(int))
        for i, row in df.iterrows():
            element = row[element_col]
            section = shuffled_sections[list(df.index).index(i)]
            if pd.isna(element) or element == 'nan':
                continue
            perm_counts[section][element] += 1
        
        # Calculate enrichments for this permutation
        for section in perm_counts:
            section_total = sum(perm_counts[section].values())
            for element in perm_counts[section]:
                count = perm_counts[section][element]
                section_prop = count / section_total
                
                corpus_count = sum(perm_counts[s].get(element, 0) for s in perm_counts)
                corpus_prop = corpus_count / total_tokens
                
                enrichment = section_prop / corpus_prop if corpus_prop > 0 else 0
                permutation_enrichments[(section, element)].append(enrichment)
    
    # Calculate p-values
    print("  Calculating p-values...")
    results = []
    
    for (section, element), obs_data in observed_enrichments.items():
        observed = obs_data['enrichment']
        count = obs_data['count']
        
        # Get null distribution
        null_dist = permutation_enrichments.get((section, element), [])
        
        if len(null_dist) > 0:
            # Two-tailed p-value: how many permutations are as extreme?
            p_value = np.mean([abs(perm - 1.0) >= abs(observed - 1.0) for perm in null_dist])
        else:
            p_value = 1.0
        
        results.append({
            'section': section,
            'element': element,
            'count': count,
            'observed_enrichment': observed,
            'p_value': p_value
        })
    
    return pd.DataFrame(results)

# Test suffix enrichments
print(f"\n{'='*80}")
print("TESTING SUFFIX ENRICHMENTS")
print("="*80)

# Extract suffixes
df_tokens['suffix_extracted'] = df_tokens.apply(
    lambda row: (row['token'][len(row['stem']):] if str(row['token']).startswith(str(row['stem'])) else 'NULL') 
    if pd.notna(row['stem']) and row['stem'] != 'nan' else None,
    axis=1
)
df_tokens['suffix_extracted'] = df_tokens['suffix_extracted'].fillna('NULL')
df_tokens['suffix_extracted'] = df_tokens['suffix_extracted'].replace('', 'NULL')

suffix_results = permutation_test_enrichment(df_tokens, 'suffix_extracted', N_PERMUTATIONS)

# Apply Bonferroni correction
n_tests_suffix = len(suffix_results)
suffix_results['p_value_bonferroni'] = suffix_results['p_value'] * n_tests_suffix
suffix_results['p_value_bonferroni'] = suffix_results['p_value_bonferroni'].clip(upper=1.0)
suffix_results['significant_bonferroni'] = suffix_results['p_value_bonferroni'] < 0.05

# Show significant suffix enrichments
print(f"\nSignificant suffix enrichments (p < 0.05, Bonferroni corrected):")
sig_suffixes = suffix_results[suffix_results['significant_bonferroni']].sort_values('p_value')

if len(sig_suffixes) > 0:
    print(f"\n{'Section':<20} {'Suffix':<10} {'Count':<8} {'Enrichment':<12} {'p-value':<10}")
    print("-" * 70)
    for _, row in sig_suffixes.head(20).iterrows():
        print(f"{row['section']:<20} {row['element']:<10} {row['count']:<8.0f} "
              f"{row['observed_enrichment']:<12.2f} {row['p_value_bonferroni']:<10.4f}")
else:
    print("  No significant enrichments after correction")

# Test top stem enrichments (top 100 stems only, to reduce multiple comparisons)
print(f"\n{'='*80}")
print("TESTING TOP 100 STEM ENRICHMENTS")
print("="*80)

# Get top 100 stems
top_stems = df_tokens['stem'].value_counts().head(100).index
df_tokens_top = df_tokens[df_tokens['stem'].isin(top_stems)].copy()

stem_results = permutation_test_enrichment(df_tokens_top, 'stem', N_PERMUTATIONS)

# Apply Bonferroni correction
n_tests_stem = len(stem_results)
stem_results['p_value_bonferroni'] = stem_results['p_value'] * n_tests_stem
stem_results['p_value_bonferroni'] = stem_results['p_value_bonferroni'].clip(upper=1.0)
stem_results['significant_bonferroni'] = stem_results['p_value_bonferroni'] < 0.05

# Show significant stem enrichments
print(f"\nSignificant stem enrichments (p < 0.05, Bonferroni corrected):")
sig_stems = stem_results[stem_results['significant_bonferroni']].sort_values('p_value')

if len(sig_stems) > 0:
    print(f"\n{'Section':<20} {'Stem':<10} {'Count':<8} {'Enrichment':<12} {'p-value':<10}")
    print("-" * 70)
    for _, row in sig_stems.head(20).iterrows():
        print(f"{row['section']:<20} {row['element']:<10} {row['count']:<8.0f} "
              f"{row['observed_enrichment']:<12.2f} {row['p_value_bonferroni']:<10.4f}")
else:
    print("  No significant enrichments after correction")

# Combine and save
suffix_results['type'] = 'suffix'
stem_results['type'] = 'stem'
all_results = pd.concat([suffix_results, stem_results], ignore_index=True)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
all_results.to_csv(OUTPUT, sep='\t', index=False)

print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("SUMMARY")
print("="*80)
print(f"\nSuffix tests: {n_tests_suffix} comparisons")
print(f"  Significant: {len(sig_suffixes)} ({len(sig_suffixes)/n_tests_suffix*100:.1f}%)")
print(f"\nStem tests: {n_tests_stem} comparisons")
print(f"  Significant: {len(sig_stems)} ({len(sig_stems)/n_tests_stem*100:.1f}%)")

print(f"\nNext step: Run v03_morphological_validation.py")
