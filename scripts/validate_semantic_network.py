#!/usr/bin/env python3
"""
Semantic Network Validation

Tests if our stems behave as a coherent semantic system.
If translations are correct, we expect:
- Process verbs cluster together
- Herbs cluster with processes
- Substances appear with processes
- Each appears in appropriate sections
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

print("="*80)
print("SEMANTIC NETWORK VALIDATION")
print("="*80)

# Load data
HOME = Path.home()
t03 = pd.read_csv(HOME / "randomization_test/t03_enriched_translations.tsv", sep='\t')
t3 = pd.read_csv(HOME / "randomization_test/t3_lexical_lexicon.tsv", sep='\t')

# Categorize stems by semantic type
CATEGORIES = {
    'PROCESS': ['ar', 'al', 'aiin', 'air', 'okar', 'otar', 'am', 'ain', 'cheo'],
    'HERB': ['dar', 'cho', 'dair', 'kar', 'char', 'sho', 'dal'],
    'SUBSTANCE': ['ol', 'qokar', 'qokal', 'qotal', 'qol'],
    'OTHER': ['qotar']  # Structural placeholder
}

# Create reverse mapping
stem_to_category = {}
for cat, stems in CATEGORIES.items():
    for stem in stems:
        stem_to_category[stem] = cat

stem_to_lemma = dict(zip(t3['stem'], t3['lemma_latin']))
stem_to_gloss = dict(zip(t3['stem'], t3['gloss_en']))

print("\nCategorization:")
for cat, stems in CATEGORIES.items():
    print(f"  {cat:12s}: {len(stems)} stems - {stems}")

# PREDICTION 1: Within-category clustering
print(f"\n{'='*80}")
print("PREDICTION 1: Stems in same category should co-occur")
print("="*80)

print("\nFor each category, measure how often stems co-occur with same-category stems")

category_scores = {}

for category, cat_stems in CATEGORIES.items():
    if len(cat_stems) < 2:
        continue
    
    print(f"\n{category} category:")
    
    # For each stem in category, count co-occurrence with other category members
    within_category_cooccur = []
    
    for stem in cat_stems:
        stem_folios = t03[t03['stem'] == stem]['folio_norm'].unique()
        
        if len(stem_folios) == 0:
            continue
        
        # Count how many folios have other stems from same category
        cooccur_count = 0
        for folio in stem_folios:
            folio_stems = t03[t03['folio_norm'] == folio]['stem'].tolist()
            other_cat_stems = [s for s in cat_stems if s != stem and s in folio_stems]
            if other_cat_stems:
                cooccur_count += 1
        
        cooccur_rate = cooccur_count / len(stem_folios) if len(stem_folios) > 0 else 0
        within_category_cooccur.append(cooccur_rate)
        
        print(f"  {stem:8s}: {cooccur_count}/{len(stem_folios):3d} folios ({cooccur_rate*100:5.1f}%) co-occur with other {category} stems")
    
    if within_category_cooccur:
        avg_score = np.mean(within_category_cooccur)
        category_scores[category] = avg_score
        print(f"  → Category average: {avg_score*100:.1f}%")

# PREDICTION 2: Cross-category clustering (herbs with processes, substances with processes)
print(f"\n{'='*80}")
print("PREDICTION 2: Herbs/Substances should co-occur with Processes")
print("="*80)

print("\nIf translations correct: recipes mention herbs WITH processes (grind rue, mix mint)")

cross_category_scores = {}

# Test: Herbs co-occur with Processes
print(f"\nHERBS + PROCESSES:")
herb_process_scores = []
for herb_stem in CATEGORIES['HERB']:
    herb_folios = t03[t03['stem'] == herb_stem]['folio_norm'].unique()
    if len(herb_folios) == 0:
        continue
    
    cooccur = 0
    for folio in herb_folios:
        folio_stems = t03[t03['folio_norm'] == folio]['stem'].tolist()
        if any(p in folio_stems for p in CATEGORIES['PROCESS']):
            cooccur += 1
    
    rate = cooccur / len(herb_folios)
    herb_process_scores.append(rate)
    print(f"  {herb_stem:8s} ({stem_to_gloss.get(herb_stem, '???'):15s}): {cooccur}/{len(herb_folios):3d} ({rate*100:5.1f}%) with processes")

if herb_process_scores:
    avg = np.mean(herb_process_scores)
    cross_category_scores['HERB+PROCESS'] = avg
    print(f"  → Average: {avg*100:.1f}%")

# Test: Substances co-occur with Processes
print(f"\nSUBSTANCES + PROCESSES:")
substance_process_scores = []
for subst_stem in CATEGORIES['SUBSTANCE']:
    subst_folios = t03[t03['stem'] == subst_stem]['folio_norm'].unique()
    if len(subst_folios) == 0:
        continue
    
    cooccur = 0
    for folio in subst_folios:
        folio_stems = t03[t03['folio_norm'] == folio]['stem'].tolist()
        if any(p in folio_stems for p in CATEGORIES['PROCESS']):
            cooccur += 1
    
    rate = cooccur / len(subst_folios)
    substance_process_scores.append(rate)
    print(f"  {subst_stem:8s} ({stem_to_gloss.get(subst_stem, '???'):15s}): {cooccur}/{len(subst_folios):3d} ({rate*100:5.1f}%) with processes")

if substance_process_scores:
    avg = np.mean(substance_process_scores)
    cross_category_scores['SUBSTANCE+PROCESS'] = avg
    print(f"  → Average: {avg*100:.1f}%")

# PREDICTION 3: Section distributions match semantic types
print(f"\n{'='*80}")
print("PREDICTION 3: Section distributions match meanings")
print("="*80)

print("\nExpected distributions:")
print("  PROCESS    → Recipes, Pharmaceutical (where instructions are)")
print("  HERB       → Herbal, Recipes (where plants discussed)")
print("  SUBSTANCE  → Biological, Recipes (where liquids/materials are)")

for category, cat_stems in CATEGORIES.items():
    if category == 'OTHER':
        continue
    
    print(f"\n{category}:")
    
    # Expected sections for this category
    if category == 'PROCESS':
        expected = ['Recipes', 'Pharmaceutical']
    elif category == 'HERB':
        expected = ['Herbal', 'Recipes']
    elif category == 'SUBSTANCE':
        expected = ['Biological', 'Recipes']
    else:
        expected = ['Recipes']
    
    print(f"  Expected sections: {expected}")
    
    # Measure how much of each stem appears in expected sections
    for stem in cat_stems:
        stem_data = t03[t03['stem'] == stem]
        total = len(stem_data)
        
        if total == 0:
            continue
        
        in_expected = len(stem_data[stem_data['section'].isin(expected)])
        rate = in_expected / total
        
        print(f"    {stem:8s}: {in_expected}/{total:3d} ({rate*100:5.1f}%) in expected sections")

# OVERALL ASSESSMENT
print(f"\n{'='*80}")
print("OVERALL ASSESSMENT")
print("="*80)

print("\nIf our translations are correct, we expect:")
print("  1. High within-category co-occurrence (>50%)")
print("  2. High herb+process co-occurrence (>60%)")
print("  3. High substance+process co-occurrence (>60%)")
print("  4. Stems appear in semantically appropriate sections")

print("\nResults:")
print(f"  Within-category clustering:")
for cat, score in category_scores.items():
    status = "✓" if score > 0.5 else "⚠" if score > 0.3 else "✗"
    print(f"    {status} {cat:12s}: {score*100:.1f}%")

print(f"\n  Cross-category (herbs/substances with processes):")
for pair, score in cross_category_scores.items():
    status = "✓" if score > 0.6 else "⚠" if score > 0.4 else "✗"
    print(f"    {status} {pair:20s}: {score*100:.1f}%")

# Count how many predictions are met
predictions_met = 0
total_predictions = 0

# Within-category
for score in category_scores.values():
    total_predictions += 1
    if score > 0.5:
        predictions_met += 1

# Cross-category
for score in cross_category_scores.values():
    total_predictions += 1
    if score > 0.6:
        predictions_met += 1

print(f"\n{'='*80}")
print(f"CONCLUSION")
print("="*80)

print(f"\nPredictions met: {predictions_met}/{total_predictions}")

if predictions_met >= total_predictions * 0.75:
    print("\n✓✓ STRONG EVIDENCE: Semantic network behaves as predicted")
    print("   Our categorization and translations are likely correct")
elif predictions_met >= total_predictions * 0.5:
    print("\n✓ MODERATE EVIDENCE: Some predictions met")
    print("   Translations partially supported")
else:
    print("\n✗ WEAK EVIDENCE: Few predictions met")
    print("   Translations questionable")

print("\nThis test validates the SYSTEM of translations, not individual stems.")
print("If the system works, individual stems are likely correct.")

