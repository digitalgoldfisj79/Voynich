#!/usr/bin/env python3
"""
Randomization Test: Are our T3 lexicon results better than random chance?

This tests whether our 11.5% coverage and section-specific patterns could 
arise from randomly chosen stems and Latin words.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("="*80)
print("RANDOMIZATION TEST - T3 LEXICON VALIDATION")
print("="*80)

# Load data
HOME = Path.home()
t03_path = HOME / "randomization_test/t03_enriched_translations.tsv"
t3_path = HOME / "randomization_test/t3_lexical_lexicon.tsv"

print(f"\nLoading data...")
print(f"  T03: {t03_path}")
print(f"  T3:  {t3_path}")

t03 = pd.read_csv(t03_path, sep='\t')
t3_actual = pd.read_csv(t3_path, sep='\t')

print(f"\nT03 corpus: {len(t03)} tokens")
print(f"Our lexicon: {len(t3_actual)} stems")

# Get actual results
t03_with_lemma = t03.merge(t3_actual[['stem', 'lemma_latin']], on='stem', how='left')
actual_coverage = t03_with_lemma['lemma_latin'].notna().sum() / len(t03)

print(f"\n{'='*80}")
print(f"ACTUAL RESULTS")
print(f"{'='*80}")
print(f"Overall coverage: {actual_coverage*100:.2f}%")

# Coverage by section
section_coverage = {}
for section in t03['section'].dropna().unique():
    section_data = t03_with_lemma[t03_with_lemma['section'] == section]
    section_cov = section_data['lemma_latin'].notna().sum() / len(section_data)
    section_coverage[section] = section_cov
    print(f"  {section:20s}: {section_cov*100:.2f}%")

print(f"\n{'='*80}")
print(f"GENERATING RANDOM LEXICONS")
print(f"{'='*80}")

# Get stem frequency distribution
stem_freq = t03['stem'].value_counts()
print(f"\nCorpus has {len(stem_freq)} unique stems")

# Get our actual stem frequencies
our_stems = t3_actual['stem'].tolist()
our_stem_freqs = [stem_freq.get(stem, 0) for stem in our_stems]
print(f"Our stems: mean freq = {np.mean(our_stem_freqs):.1f}, median = {np.median(our_stem_freqs):.1f}")

# Strategy 1: Completely random stems
print(f"\nStrategy 1: COMPLETELY RANDOM")
print(f"  Pick {len(t3_actual)} random stems from corpus")

n_simulations = 100
random_coverages = []
random_astro_coverages = []

np.random.seed(42)  # Reproducibility

for sim in range(n_simulations):
    if (sim + 1) % 20 == 0:
        print(f"  Simulation {sim+1}/{n_simulations}...", file=sys.stderr)
    
    # Pick random stems
    random_stems = np.random.choice(stem_freq.index, size=len(t3_actual), replace=False)
    
    # Create random lexicon (just mark these stems as "mapped")
    random_lex = pd.DataFrame({'stem': random_stems, 'lemma_latin': 'RANDOM'})
    
    # Merge with corpus
    t03_random = t03.merge(random_lex[['stem', 'lemma_latin']], on='stem', how='left')
    
    # Calculate coverage
    rand_cov = t03_random['lemma_latin'].notna().sum() / len(t03)
    random_coverages.append(rand_cov)
    
    # Calculate Astronomical coverage
    astro_data = t03_random[t03_random['section'] == 'Astronomical']
    if len(astro_data) > 0:
        astro_cov = astro_data['lemma_latin'].notna().sum() / len(astro_data)
        random_astro_coverages.append(astro_cov)

random_coverages = np.array(random_coverages)
random_astro_coverages = np.array(random_astro_coverages)

print(f"\n{'='*80}")
print(f"RESULTS: COMPLETELY RANDOM LEXICONS")
print(f"{'='*80}")

print(f"\nOverall Coverage:")
print(f"  Actual:         {actual_coverage*100:.2f}%")
print(f"  Random mean:    {random_coverages.mean()*100:.2f}%")
print(f"  Random std:     {random_coverages.std()*100:.2f}%")
print(f"  Random range:   {random_coverages.min()*100:.2f}% - {random_coverages.max()*100:.2f}%")
print(f"  p-value:        {(random_coverages >= actual_coverage).sum() / len(random_coverages):.4f}")

print(f"\nAstronomical Section Coverage:")
astro_actual = section_coverage.get('Astronomical', 0)
print(f"  Actual:         {astro_actual*100:.2f}%")
print(f"  Random mean:    {random_astro_coverages.mean()*100:.2f}%")
print(f"  Random std:     {random_astro_coverages.std()*100:.2f}%")
print(f"  Random range:   {random_astro_coverages.min()*100:.2f}% - {random_astro_coverages.max()*100:.2f}%")
print(f"  p-value:        {(random_astro_coverages >= astro_actual).sum() / len(random_astro_coverages):.4f}")

print(f"\n{'='*80}")
print(f"INTERPRETATION")
print(f"{'='*80}")

overall_pval = (random_coverages >= actual_coverage).sum() / len(random_coverages)
astro_pval = (random_astro_coverages >= astro_actual).sum() / len(random_astro_coverages)

if overall_pval < 0.01:
    print(f"✓ Our overall coverage ({actual_coverage*100:.2f}%) is SIGNIFICANTLY better than random (p={overall_pval:.4f})")
elif overall_pval < 0.05:
    print(f"✓ Our overall coverage is marginally better than random (p={overall_pval:.4f})")
else:
    print(f"✗ Our overall coverage is NOT significantly better than random (p={overall_pval:.4f})")
    print(f"  WARNING: This suggests our lexicon may not contain real signal!")

if astro_pval < 0.01:
    print(f"✓ Astronomical anomaly ({astro_actual*100:.2f}%) is SIGNIFICANTLY better than random (p={astro_pval:.4f})")
elif astro_pval < 0.05:
    print(f"✓ Astronomical anomaly is marginally better than random (p={astro_pval:.4f})")
else:
    print(f"✗ Astronomical anomaly is NOT significantly better than random (p={astro_pval:.4f})")
    print(f"  This suggests high Astronomical coverage could occur by chance")

print(f"\n{'='*80}")
print(f"CONCLUSION")
print(f"{'='*80}")

if overall_pval < 0.05:
    print("Our lexicon performs better than random chance.")
    print("This validates that we are detecting real patterns, not noise.")
else:
    print("WARNING: Our lexicon does NOT perform significantly better than random.")
    print("This suggests we may be overfitting or our mappings are incorrect.")
    print("We should NOT proceed with further analysis until this is resolved.")

