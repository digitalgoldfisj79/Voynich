#!/usr/bin/env python3
"""
Individual Stem Validation Suite

For each stem in our lexicon, run comprehensive tests to determine
if we can defend the mapping with high confidence.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import sys

print("="*80)
print("INDIVIDUAL STEM VALIDATION SUITE")
print("="*80)

# Load data
HOME = Path.home()
t03_path = HOME / "randomization_test/t03_enriched_translations.tsv"
t3_path = HOME / "randomization_test/t3_lexical_lexicon.tsv"

t03 = pd.read_csv(t03_path, sep='\t')
t3 = pd.read_csv(t3_path, sep='\t')

stem_freq = t03['stem'].value_counts()
all_stems = stem_freq.index.tolist()
all_freqs = stem_freq.values

# Get our stems
our_stems = t3['stem'].tolist()
stem_to_lemma = dict(zip(t3['stem'], t3['lemma_latin']))
stem_to_gloss = dict(zip(t3['stem'], t3['gloss_en']))

# Type A (validated) for cross-validation
type_a_stems = ['al', 'ar', 'dar', 'cho', 'dair', 'aiin', 'okar', 'otar', 'air']

print(f"\nValidating {len(our_stems)} stems individually...")
print(f"Type A (Astronomical-validated): {len(type_a_stems)} stems")

# Results storage
validation_results = []

for stem in our_stems:
    print(f"\n{'='*80}")
    print(f"VALIDATING: {stem} → {stem_to_lemma.get(stem)} ({stem_to_gloss.get(stem)})")
    print("="*80)
    
    stem_count = stem_freq.get(stem, 0)
    
    if stem_count == 0:
        print("✗ ABSENT from corpus")
        validation_results.append({
            'stem': stem,
            'lemma': stem_to_lemma.get(stem),
            'frequency': 0,
            'test1_pval': 1.0,
            'test2_score': 0,
            'test3_score': 0,
            'test4_score': 0,
            'confidence': 'REJECT'
        })
        continue
    
    print(f"Frequency: {stem_count} ({stem_count/len(t03)*100:.2f}%)")
    
    # TEST 1: Frequency-matched baseline
    print(f"\n[TEST 1] Frequency-Matched Baseline")
    print(f"  Question: Is {stem} better than random stems of similar frequency?")
    
    # Find stems within ±20% frequency
    lower = stem_count * 0.8
    upper = stem_count * 1.2
    freq_matched_stems = [s for s, f in zip(all_stems, all_freqs) 
                          if lower <= f <= upper and s != stem and s not in our_stems]
    
    if len(freq_matched_stems) < 10:
        print(f"  WARNING: Only {len(freq_matched_stems)} frequency-matched stems available")
    
    # For this stem, measure its section distribution
    stem_sections = t03[t03['stem'] == stem]['section'].value_counts()
    stem_in_astro = len(t03[(t03['stem'] == stem) & (t03['section'] == 'Astronomical')])
    astro_rate = stem_in_astro / stem_count if stem_count > 0 else 0
    
    # Compare to random frequency-matched stems
    random_astro_rates = []
    for rand_stem in freq_matched_stems[:50]:  # Sample 50
        rand_in_astro = len(t03[(t03['stem'] == rand_stem) & (t03['section'] == 'Astronomical')])
        rand_count = stem_freq.get(rand_stem, 0)
        if rand_count > 0:
            random_astro_rates.append(rand_in_astro / rand_count)
    
    if random_astro_rates:
        pval = (np.array(random_astro_rates) >= astro_rate).sum() / len(random_astro_rates)
        print(f"  Astronomical enrichment: {astro_rate*100:.1f}% vs random mean {np.mean(random_astro_rates)*100:.1f}%")
        print(f"  p-value: {pval:.3f}")
        test1_result = pval
    else:
        print(f"  Cannot compute p-value")
        test1_result = 1.0
    
    # TEST 2: Section coherence
    print(f"\n[TEST 2] Section Coherence")
    print(f"  Question: Does {stem} appear in expected sections?")
    
    gloss = stem_to_gloss.get(stem, '')
    expected_sections = []
    
    # Determine expected sections based on gloss
    if any(x in gloss.lower() for x in ['herb', 'mint', 'rue', 'rose', 'dill', 'parsley', 'sage', 'celery']):
        expected_sections = ['Herbal', 'Recipes']
    elif any(x in gloss.lower() for x in ['grind', 'mix', 'cook', 'boil', 'pour', 'burn', 'place']):
        expected_sections = ['Recipes', 'Pharmaceutical']
    elif any(x in gloss.lower() for x in ['water', 'oil', 'juice', 'honey']):
        expected_sections = ['Recipes', 'Pharmaceutical', 'Biological']
    else:
        expected_sections = ['Recipes', 'Herbal']
    
    in_expected = 0
    for section in expected_sections:
        section_count = len(t03[(t03['stem'] == stem) & (t03['section'] == section)])
        in_expected += section_count
    
    coherence_score = in_expected / stem_count if stem_count > 0 else 0
    print(f"  Expected sections: {expected_sections}")
    print(f"  Appears in expected: {in_expected}/{stem_count} ({coherence_score*100:.1f}%)")
    
    test2_result = coherence_score
    
    # TEST 3: Co-occurrence specificity
    print(f"\n[TEST 3] Co-occurrence Specificity")
    print(f"  Question: Does {stem} co-occur with semantically appropriate stems?")
    
    # Get folios where this stem appears
    stem_folios = t03[t03['stem'] == stem]['folio_norm'].unique()
    
    # Count co-occurrence with Type A stems
    type_a_cooccur = 0
    for folio in stem_folios:
        folio_stems = t03[t03['folio_norm'] == folio]['stem'].tolist()
        if any(ta in folio_stems for ta in type_a_stems):
            type_a_cooccur += 1
    
    cooccur_rate = type_a_cooccur / len(stem_folios) if len(stem_folios) > 0 else 0
    print(f"  Co-occurs with Type A stems: {type_a_cooccur}/{len(stem_folios)} folios ({cooccur_rate*100:.1f}%)")
    
    test3_result = cooccur_rate
    
    # TEST 4: Exclusion test (simplified)
    print(f"\n[TEST 4] Exclusion Test")
    print(f"  Question: Does {stem} avoid inappropriate contexts?")
    
    # Check if it appears in Unassigned (shouldn't have much signal there)
    unassigned_count = len(t03[(t03['stem'] == stem) & (t03['section'] == 'Unassigned')])
    unassigned_rate = unassigned_count / stem_count if stem_count > 0 else 0
    
    exclusion_score = 1.0 - unassigned_rate  # Higher is better
    print(f"  In Unassigned: {unassigned_count}/{stem_count} ({unassigned_rate*100:.1f}%)")
    print(f"  Exclusion score: {exclusion_score:.2f}")
    
    test4_result = exclusion_score
    
    # OVERALL ASSESSMENT
    print(f"\n[OVERALL ASSESSMENT]")
    
    # Decision criteria
    confidence = "UNKNOWN"
    
    if test1_result < 0.05 and test2_result > 0.5 and test3_result > 0.6:
        confidence = "HIGH"
        print("  ✓✓ HIGH CONFIDENCE")
        print("    - Significantly enriched vs frequency-matched random")
        print("    - Appears in expected sections")
        print("    - Strong co-occurrence with validated stems")
    elif test1_result < 0.10 and test2_result > 0.3 and test3_result > 0.4:
        confidence = "MEDIUM"
        print("  ✓ MEDIUM CONFIDENCE")
        print("    - Some evidence above random")
        print("    - Moderate section coherence")
    elif test1_result < 0.20:
        confidence = "LOW"
        print("  ⚠ LOW CONFIDENCE")
        print("    - Weak evidence above random")
    else:
        confidence = "REJECT"
        print("  ✗ REJECT")
        print("    - Not distinguishable from random")
    
    validation_results.append({
        'stem': stem,
        'lemma': stem_to_lemma.get(stem),
        'gloss': stem_to_gloss.get(stem),
        'frequency': stem_count,
        'test1_pval': test1_result,
        'test2_section_coherence': test2_result,
        'test3_cooccurrence': test3_result,
        'test4_exclusion': test4_result,
        'confidence': confidence
    })

# Summary
print(f"\n{'='*80}")
print(f"VALIDATION SUMMARY")
print("="*80)

results_df = pd.DataFrame(validation_results)

print(f"\nConfidence Distribution:")
for conf in ['HIGH', 'MEDIUM', 'LOW', 'REJECT']:
    count = (results_df['confidence'] == conf).sum()
    stems = results_df[results_df['confidence'] == conf]['stem'].tolist()
    print(f"  {conf:10s}: {count:2d} stems - {stems}")

print(f"\n{'='*80}")
print(f"RECOMMENDED BASE LEXICON")
print("="*80)

high_conf = results_df[results_df['confidence'] == 'HIGH']
med_conf = results_df[results_df['confidence'] == 'MEDIUM']

print(f"\nHIGH CONFIDENCE ({len(high_conf)} stems):")
print("  These should form our base lexicon")
for _, row in high_conf.iterrows():
    print(f"    {row['stem']:10s} → {row['lemma']:20s} ({row['gloss']})")

print(f"\nMEDIUM CONFIDENCE ({len(med_conf)} stems):")
print("  Include with caveats in documentation")
for _, row in med_conf.iterrows():
    print(f"    {row['stem']:10s} → {row['lemma']:20s} ({row['gloss']})")

# Save results
results_df.to_csv(HOME / 'randomization_test/stem_validation_results.tsv', sep='\t', index=False)
print(f"\n✓ Saved validation results to ~/randomization_test/stem_validation_results.tsv")

