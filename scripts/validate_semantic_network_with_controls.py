#!/usr/bin/env python3
"""
Semantic Network Validation with Proper Controls

Tests if our semantic clustering is better than random stems
of similar frequencies.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import sys

print("="*80)
print("SEMANTIC NETWORK VALIDATION - WITH CONTROLS")
print("="*80)

# Load data
HOME = Path.home()
t03 = pd.read_csv(HOME / "randomization_test/t03_enriched_translations.tsv", sep='\t')
t3 = pd.read_csv(HOME / "randomization_test/t3_lexical_lexicon.tsv", sep='\t')

# Get stem frequencies
stem_freq = t03['stem'].value_counts()
all_stems = stem_freq.index.tolist()
all_freqs = stem_freq.values

# Our actual categorization
OUR_CATEGORIES = {
    'PROCESS': ['ar', 'al', 'aiin', 'air', 'okar', 'otar', 'am', 'ain', 'cheo'],
    'HERB': ['dar', 'cho', 'dair', 'kar', 'char', 'sho', 'dal'],
    'SUBSTANCE': ['ol', 'qokar', 'qokal', 'qotal', 'qol']
}

our_stems = []
for stems in OUR_CATEGORIES.values():
    our_stems.extend(stems)

print("\nOur actual categorization:")
for cat, stems in OUR_CATEGORIES.items():
    freqs = [stem_freq.get(s, 0) for s in stems]
    print(f"  {cat:12s}: {len(stems)} stems, freq range: {min(freqs)}-{max(freqs)}, mean: {np.mean(freqs):.0f}")

# Function to measure clustering
def measure_clustering(categories, t03_data):
    """
    Measures within-category and cross-category clustering.
    Returns: (within_process, within_herb, within_substance, herb_process, substance_process)
    """
    results = {}
    
    # Within-category clustering
    for cat_name, cat_stems in categories.items():
        if len(cat_stems) < 2:
            continue
            
        cooccur_rates = []
        for stem in cat_stems:
            stem_folios = t03_data[t03_data['stem'] == stem]['folio_norm'].unique()
            if len(stem_folios) == 0:
                continue
            
            cooccur = 0
            for folio in stem_folios:
                folio_stems = t03_data[t03_data['folio_norm'] == folio]['stem'].tolist()
                other_cat_stems = [s for s in cat_stems if s != stem and s in folio_stems]
                if other_cat_stems:
                    cooccur += 1
            
            rate = cooccur / len(stem_folios) if len(stem_folios) > 0 else 0
            cooccur_rates.append(rate)
        
        if cooccur_rates:
            results[f'within_{cat_name.lower()}'] = np.mean(cooccur_rates)
    
    # Cross-category clustering: HERB + PROCESS
    if 'HERB' in categories and 'PROCESS' in categories:
        herb_process_rates = []
        for herb_stem in categories['HERB']:
            herb_folios = t03_data[t03_data['stem'] == herb_stem]['folio_norm'].unique()
            if len(herb_folios) == 0:
                continue
            
            cooccur = 0
            for folio in herb_folios:
                folio_stems = t03_data[t03_data['folio_norm'] == folio]['stem'].tolist()
                if any(p in folio_stems for p in categories['PROCESS']):
                    cooccur += 1
            
            rate = cooccur / len(herb_folios)
            herb_process_rates.append(rate)
        
        if herb_process_rates:
            results['herb_process'] = np.mean(herb_process_rates)
    
    # Cross-category clustering: SUBSTANCE + PROCESS
    if 'SUBSTANCE' in categories and 'PROCESS' in categories:
        subst_process_rates = []
        for subst_stem in categories['SUBSTANCE']:
            subst_folios = t03_data[t03_data['stem'] == subst_stem]['folio_norm'].unique()
            if len(subst_folios) == 0:
                continue
            
            cooccur = 0
            for folio in subst_folios:
                folio_stems = t03_data[t03_data['folio_norm'] == folio]['stem'].tolist()
                if any(p in folio_stems for p in categories['PROCESS']):
                    cooccur += 1
            
            rate = cooccur / len(subst_folios)
            subst_process_rates.append(rate)
        
        if subst_process_rates:
            results['substance_process'] = np.mean(subst_process_rates)
    
    return results

# Measure our actual clustering
print(f"\n{'='*80}")
print("ACTUAL RESULTS")
print("="*80)

our_results = measure_clustering(OUR_CATEGORIES, t03)
print("\nOur clustering scores:")
for metric, score in our_results.items():
    print(f"  {metric:25s}: {score*100:5.1f}%")

# Generate random controls
print(f"\n{'='*80}")
print("GENERATING RANDOM CONTROLS")
print("="*80)

print("\nFor each iteration:")
print("  1. Pick 9 random stems (similar freq to our PROCESS stems)")
print("  2. Pick 7 random stems (similar freq to our HERB stems)")
print("  3. Pick 5 random stems (similar freq to our SUBSTANCE stems)")
print("  4. Measure clustering")
print("  5. Compare to our results")

n_simulations = 100
np.random.seed(44)

random_results = {
    'within_process': [],
    'within_herb': [],
    'within_substance': [],
    'herb_process': [],
    'substance_process': []
}

# Get frequency ranges for each category
process_freqs = [stem_freq.get(s, 0) for s in OUR_CATEGORIES['PROCESS']]
herb_freqs = [stem_freq.get(s, 0) for s in OUR_CATEGORIES['HERB']]
substance_freqs = [stem_freq.get(s, 0) for s in OUR_CATEGORIES['SUBSTANCE']]

process_freq_range = (min(process_freqs) * 0.7, max(process_freqs) * 1.3)
herb_freq_range = (min(herb_freqs) * 0.7, max(herb_freqs) * 1.3)
substance_freq_range = (min(substance_freqs) * 0.7, max(substance_freqs) * 1.3)

for sim in range(n_simulations):
    if (sim + 1) % 20 == 0:
        print(f"  Simulation {sim+1}/{n_simulations}...", file=sys.stderr)
    
    # Pick random stems matching frequency distributions
    # Avoid our actual stems
    available_stems = [s for s in all_stems if s not in our_stems]
    available_freqs = [stem_freq.get(s, 0) for s in available_stems]
    
    # PROCESS: pick 9 stems
    process_candidates = [s for s, f in zip(available_stems, available_freqs)
                         if process_freq_range[0] <= f <= process_freq_range[1]]
    if len(process_candidates) < 9:
        continue
    random_process = list(np.random.choice(process_candidates, size=9, replace=False))
    
    # HERB: pick 7 stems (excluding already picked)
    herb_candidates = [s for s, f in zip(available_stems, available_freqs)
                      if herb_freq_range[0] <= f <= herb_freq_range[1]
                      and s not in random_process]
    if len(herb_candidates) < 7:
        continue
    random_herb = list(np.random.choice(herb_candidates, size=7, replace=False))
    
    # SUBSTANCE: pick 5 stems (excluding already picked)
    substance_candidates = [s for s, f in zip(available_stems, available_freqs)
                           if substance_freq_range[0] <= f <= substance_freq_range[1]
                           and s not in random_process
                           and s not in random_herb]
    if len(substance_candidates) < 5:
        continue
    random_substance = list(np.random.choice(substance_candidates, size=5, replace=False))
    
    # Create random categorization
    random_categories = {
        'PROCESS': random_process,
        'HERB': random_herb,
        'SUBSTANCE': random_substance
    }
    
    # Measure clustering
    rand_results = measure_clustering(random_categories, t03)
    
    for metric, score in rand_results.items():
        if metric in random_results:
            random_results[metric].append(score)

# Convert to arrays
for key in random_results:
    random_results[key] = np.array(random_results[key])

# Compare our results to random
print(f"\n{'='*80}")
print("COMPARISON TO RANDOM CONTROLS")
print("="*80)

print(f"\nRan {n_simulations} random simulations")
print("\nFor each metric, compare our result to random distribution:\n")

significant_count = 0
total_metrics = len(our_results)

for metric in our_results:
    our_score = our_results[metric]
    random_scores = random_results[metric]
    
    if len(random_scores) == 0:
        continue
    
    # Calculate p-value (what % of random trials were >= our score)
    p_value = (random_scores >= our_score).sum() / len(random_scores)
    
    # Calculate z-score
    random_mean = random_scores.mean()
    random_std = random_scores.std()
    z_score = (our_score - random_mean) / random_std if random_std > 0 else 0
    
    print(f"{metric:25s}:")
    print(f"  Our result:      {our_score*100:5.1f}%")
    print(f"  Random mean:     {random_mean*100:5.1f}%")
    print(f"  Random std:      {random_std*100:5.1f}%")
    print(f"  Random range:    {random_scores.min()*100:5.1f}% - {random_scores.max()*100:5.1f}%")
    print(f"  Z-score:         {z_score:5.2f}")
    print(f"  P-value:         {p_value:.4f}")
    
    if p_value < 0.05:
        print(f"  ✓ SIGNIFICANT: Better than random (p<0.05)")
        significant_count += 1
    elif p_value < 0.10:
        print(f"  ⚠ MARGINAL: Slightly better than random (p<0.10)")
    else:
        print(f"  ✗ NOT SIGNIFICANT: Not better than random")
    print()

# Overall assessment
print("="*80)
print("FINAL VERDICT")
print("="*80)

print(f"\nSignificant results: {significant_count}/{total_metrics}")

if significant_count == total_metrics:
    print("\n✓✓ ALL METRICS SIGNIFICANT")
    print("   Our semantic network is genuinely better than random")
    print("   Strong evidence for correct translations")
elif significant_count >= total_metrics * 0.6:
    print("\n✓ MAJORITY SIGNIFICANT")
    print("   Our semantic network shows real signal")
    print("   Moderate evidence for correct translations")
else:
    print("\n✗ MOST METRICS NOT SIGNIFICANT")
    print("   Our clustering may be frequency artifacts")
    print("   Weak evidence for correct translations")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)

print("\nThis test compares our specific categorization to random categorizations")
print("of stems with similar frequencies.")
print("\nIf we pass: Our stems genuinely cluster in semantic categories")
print("If we fail: Any random stems cluster just as well (frequency artifact)")

