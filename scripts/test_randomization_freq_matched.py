#!/usr/bin/env python3
"""
Frequency-Matched Randomization Test

Tests whether our success is due to:
(a) Picking the RIGHT stems (signal), or
(b) Just picking HIGH-FREQUENCY stems (lucky)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("="*80)
print("FREQUENCY-MATCHED RANDOMIZATION TEST")
print("="*80)

# Load data
HOME = Path.home()
t03_path = HOME / "randomization_test/t03_enriched_translations.tsv"
t3_path = HOME / "randomization_test/t3_lexical_lexicon.tsv"

print(f"\nLoading data...")
t03 = pd.read_csv(t03_path, sep='\t')
t3_actual = pd.read_csv(t3_path, sep='\t')

print(f"T03 corpus: {len(t03)} tokens")
print(f"Our lexicon: {len(t3_actual)} stems")

# Get actual results
t03_with_lemma = t03.merge(t3_actual[['stem', 'lemma_latin']], on='stem', how='left')
actual_coverage = t03_with_lemma['lemma_latin'].notna().sum() / len(t03)

print(f"\n{'='*80}")
print(f"ACTUAL RESULTS")
print(f"{'='*80}")
print(f"Overall coverage: {actual_coverage*100:.2f}%")

section_coverage = {}
for section in ['Astronomical', 'Recipes', 'Herbal', 'Biological', 'Pharmaceutical']:
    section_data = t03_with_lemma[t03_with_lemma['section'] == section]
    if len(section_data) > 0:
        section_cov = section_data['lemma_latin'].notna().sum() / len(section_data)
        section_coverage[section] = section_cov
        print(f"  {section:20s}: {section_cov*100:.2f}%")

# Get stem frequencies
stem_freq = t03['stem'].value_counts()
print(f"\n{'='*80}")
print(f"OUR STEM FREQUENCY DISTRIBUTION")
print(f"{'='*80}")

our_stems = t3_actual['stem'].tolist()
our_stem_freqs = [stem_freq.get(stem, 0) for stem in our_stems]
our_stem_freqs_sorted = sorted(our_stem_freqs, reverse=True)

print(f"\nOur {len(our_stems)} stems:")
print(f"  Mean frequency:   {np.mean(our_stem_freqs):.1f}")
print(f"  Median frequency: {np.median(our_stem_freqs):.1f}")
print(f"  Total coverage:   {sum(our_stem_freqs)} tokens ({sum(our_stem_freqs)/len(t03)*100:.1f}%)")
print(f"  Min:              {min(our_stem_freqs)}")
print(f"  Max:              {max(our_stem_freqs)}")

print(f"\nTop 5 stems by frequency:")
for i, stem in enumerate(our_stems):
    freq = stem_freq.get(stem, 0)
    if i < 5 or i >= len(our_stems) - 2:
        print(f"  {stem:10s}: {freq:4d} tokens ({freq/len(t03)*100:.2f}%)")
    elif i == 5:
        print(f"  ...")

print(f"\n{'='*80}")
print(f"GENERATING FREQUENCY-MATCHED RANDOM LEXICONS")
print(f"{'='*80}")

print(f"""
Strategy: For each random lexicon, pick 22 stems such that:
  - Their frequency distribution matches ours closely
  - But they are DIFFERENT stems
  
This tests: Are we just lucky we picked common stems?
Or is there something special about WHICH stems we picked?
""")

n_simulations = 100
np.random.seed(43)  # Different seed from first test

# Create frequency bins for matching
all_stems = stem_freq.index.tolist()
all_freqs = stem_freq.values

# Sort stems by frequency
sorted_indices = np.argsort(all_freqs)[::-1]  # Descending
sorted_stems = [all_stems[i] for i in sorted_indices]
sorted_freqs = all_freqs[sorted_indices]

freq_matched_coverages = []
freq_matched_astro = []

for sim in range(n_simulations):
    if (sim + 1) % 20 == 0:
        print(f"  Simulation {sim+1}/{n_simulations}...", file=sys.stderr)
    
    # For each of our stems, find stems with similar frequency
    random_stems = []
    
    for our_stem in our_stems:
        our_freq = stem_freq.get(our_stem, 0)
        
        # Find stems within ±20% frequency range
        lower_bound = our_freq * 0.8
        upper_bound = our_freq * 1.2
        
        candidates = [s for s, f in zip(all_stems, all_freqs) 
                     if lower_bound <= f <= upper_bound 
                     and s != our_stem 
                     and s not in random_stems]
        
        if len(candidates) > 0:
            chosen = np.random.choice(candidates)
            random_stems.append(chosen)
        else:
            # If no exact match, pick closest
            freq_diffs = np.abs(all_freqs - our_freq)
            available_indices = [i for i, s in enumerate(all_stems) 
                               if s != our_stem and s not in random_stems]
            if available_indices:
                closest_idx = available_indices[np.argmin(freq_diffs[available_indices])]
                random_stems.append(all_stems[closest_idx])
    
    if len(random_stems) != len(our_stems):
        continue  # Skip this simulation if we couldn't match
    
    # Create random lexicon
    random_lex = pd.DataFrame({'stem': random_stems, 'lemma_latin': 'RANDOM'})
    
    # Merge with corpus
    t03_random = t03.merge(random_lex[['stem', 'lemma_latin']], on='stem', how='left')
    
    # Calculate coverage
    rand_cov = t03_random['lemma_latin'].notna().sum() / len(t03)
    freq_matched_coverages.append(rand_cov)
    
    # Astronomical coverage
    astro_data = t03_random[t03_random['section'] == 'Astronomical']
    if len(astro_data) > 0:
        astro_cov = astro_data['lemma_latin'].notna().sum() / len(astro_data)
        freq_matched_astro.append(astro_cov)

freq_matched_coverages = np.array(freq_matched_coverages)
freq_matched_astro = np.array(freq_matched_astro)

print(f"\n{'='*80}")
print(f"RESULTS: FREQUENCY-MATCHED RANDOM LEXICONS")
print(f"{'='*80}")

print(f"\nOverall Coverage:")
print(f"  Actual:         {actual_coverage*100:.2f}%")
print(f"  Random mean:    {freq_matched_coverages.mean()*100:.2f}%")
print(f"  Random std:     {freq_matched_coverages.std()*100:.2f}%")
print(f"  Random range:   {freq_matched_coverages.min()*100:.2f}% - {freq_matched_coverages.max()*100:.2f}%")
print(f"  p-value:        {(freq_matched_coverages >= actual_coverage).sum() / len(freq_matched_coverages):.4f}")

print(f"\nAstronomical Section Coverage:")
astro_actual = section_coverage.get('Astronomical', 0)
print(f"  Actual:         {astro_actual*100:.2f}%")
print(f"  Random mean:    {freq_matched_astro.mean()*100:.2f}%")
print(f"  Random std:     {freq_matched_astro.std()*100:.2f}%")
print(f"  Random range:   {freq_matched_astro.min()*100:.2f}% - {freq_matched_astro.max()*100:.2f}%")
print(f"  p-value:        {(freq_matched_astro >= astro_actual).sum() / len(freq_matched_astro):.4f}")

print(f"\n{'='*80}")
print(f"INTERPRETATION")
print(f"{'='*80}")

overall_pval = (freq_matched_coverages >= actual_coverage).sum() / len(freq_matched_coverages)
astro_pval = (freq_matched_astro >= astro_actual).sum() / len(freq_matched_astro)

print(f"\nCOMPARISON TO PREVIOUS TEST:")
print(f"  Completely random:     0.59% coverage")
print(f"  Frequency-matched:     {freq_matched_coverages.mean()*100:.2f}% coverage")
print(f"  Our actual:            {actual_coverage*100:.2f}% coverage")

if overall_pval < 0.01:
    print(f"\n✓ SUCCESS: Even controlling for frequency, we're significantly better (p={overall_pval:.4f})")
    print(f"  This means we picked the RIGHT stems, not just FREQUENT stems.")
elif overall_pval < 0.05:
    print(f"\n⚠ MARGINAL: Marginally better than frequency-matched random (p={overall_pval:.4f})")
    print(f"  Some signal, but frequency is a major factor.")
else:
    print(f"\n✗ WARNING: NOT significantly better than frequency-matched random (p={overall_pval:.4f})")
    print(f"  Our success may be primarily due to picking high-frequency stems.")
    print(f"  This suggests less linguistic signal than we hoped.")

print(f"\n{'='*80}")
print(f"CONCLUSION")
print(f"{'='*80}")

if overall_pval < 0.05:
    print("Our stem selection contains real linguistic signal beyond just frequency.")
    print("We are detecting meaningful patterns in the Voynich manuscript.")
else:
    print("WARNING: Our success appears to be primarily due to picking common stems.")
    print("The SPECIFIC stems we chose may not be as important as we thought.")
    print("Consider: Are our Latin mappings correct, or are we just marking frequent tokens?")

