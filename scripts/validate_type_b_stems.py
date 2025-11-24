#!/usr/bin/env python3
"""
Type B Stem Validation

Tests whether depleted/absent Astronomical stems are:
(a) Correctly mapped but used in different sections, OR
(b) Incorrectly mapped
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

print("="*80)
print("TYPE B STEM VALIDATION")
print("="*80)

# Load data
HOME = Path.home()
t03_path = HOME / "randomization_test/t03_enriched_translations.tsv"
t3_path = HOME / "randomization_test/t3_lexical_lexicon.tsv"

t03 = pd.read_csv(t03_path, sep='\t')
t3 = pd.read_csv(t3_path, sep='\t')

# Type A (validated) vs Type B (questionable)
type_a_stems = ['al', 'ar', 'dar', 'cho', 'dair', 'aiin', 'okar', 'otar', 'air']
type_b_stems = ['ol', 'qokar', 'kar', 'qol', 'qotal', 'qotar']

stem_to_lemma = dict(zip(t3['stem'], t3['lemma_latin']))
stem_to_gloss = dict(zip(t3['stem'], t3['gloss_en']))

print(f"\nType A (Astronomical-enriched, validated): {len(type_a_stems)} stems")
print(f"Type B (Astronomical-depleted, questionable): {len(type_b_stems)} stems")

print(f"\n{'='*80}")
print(f"TEST 1: SECTION DISTRIBUTION")
print(f"{'='*80}")

print("\nIf Type B mappings are correct, they should appear in sections where")
print("their meanings make sense (Recipes/Herbal for ingredients).\n")

sections = ['Recipes', 'Herbal', 'Biological', 'Pharmaceutical', 'Astronomical']

for stem in type_b_stems:
    lemma = stem_to_lemma.get(stem, '???')
    gloss = stem_to_gloss.get(stem, '???')
    
    print(f"\n{stem:10s} → {lemma:20s} ({gloss})")
    
    total_count = len(t03[t03['stem'] == stem])
    print(f"  Total corpus: {total_count} tokens ({total_count/len(t03)*100:.2f}%)")
    
    if total_count == 0:
        print("  ✗ ABSENT from corpus entirely!")
        continue
    
    for section in sections:
        section_data = t03[t03['section'] == section]
        section_count = len(section_data[section_data['stem'] == stem])
        section_pct = section_count / total_count * 100 if total_count > 0 else 0
        section_freq = section_count / len(section_data) * 100 if len(section_data) > 0 else 0
        
        marker = ""
        if section_pct > 30:
            marker = " ← PRIMARY"
        elif section_count == 0:
            marker = " (absent)"
            
        print(f"    {section:15s}: {section_count:4d} ({section_pct:5.1f}% of stem, {section_freq:5.2f}% of section){marker}")

print(f"\n{'='*80}")
print(f"TEST 2: CO-OCCURRENCE WITH TYPE A STEMS")
print(f"{'='*80}")

print("\nIf Type B mappings are correct, they should co-occur with Type A stems")
print("in recipe-like patterns (ingredients with processes).\n")

# For each Type B stem, find co-occurrence with Type A
for stem_b in type_b_stems:
    lemma_b = stem_to_lemma.get(stem_b, '???')
    gloss_b = stem_to_gloss.get(stem_b, '???')
    
    print(f"\n{stem_b:10s} → {lemma_b:20s} ({gloss_b})")
    
    # Get folios where this stem appears
    folios_with_b = t03[t03['stem'] == stem_b]['folio_norm'].unique()
    
    if len(folios_with_b) == 0:
        print("  ✗ Does not appear in corpus")
        continue
    
    # Count co-occurrence with Type A stems
    cooccur = Counter()
    
    for folio in folios_with_b:
        folio_data = t03[t03['folio_norm'] == folio]
        folio_stems = folio_data['stem'].tolist()
        
        for stem_a in type_a_stems:
            if stem_a in folio_stems:
                cooccur[stem_a] += 1
    
    if len(cooccur) == 0:
        print("  ✗ NEVER co-occurs with Type A stems!")
        print("    This suggests incorrect mapping")
        continue
    
    print(f"  Co-occurs with Type A stems in {len(folios_with_b)} folios:")
    for stem_a, count in cooccur.most_common(5):
        lemma_a = stem_to_lemma.get(stem_a, '???')
        pct = count / len(folios_with_b) * 100
        print(f"    {stem_a:8s} ({lemma_a:15s}): {count:3d} folios ({pct:5.1f}%)")

print(f"\n{'='*80}")
print(f"TEST 3: SEMANTIC COHERENCE CHECK")
print(f"{'='*80}")

print("\nExpected patterns if mappings are correct:")
print("  ol (water)  → should appear in Recipes/Pharmaceutical, co-occur with processes")
print("  qokar (oil) → should appear in Recipes/Herbal, co-occur with herbs")
print("  kar (parsley) → should appear in Herbal/Recipes, co-occur with other herbs")
print("  qotal (honey) → should appear in Recipes, co-occur with substances/processes")

# Check specific predictions
print("\n" + "="*80)
print("SPECIFIC PREDICTIONS")
print("="*80)

# Prediction 1: ol (water) should co-occur with cooking verbs
if 'ol' in type_b_stems:
    ol_folios = t03[t03['stem'] == 'ol']['folio_norm'].unique()
    cooking_verbs = ['aiin', 'okar', 'al']  # cook, boil, mix
    
    cooccur_count = 0
    for folio in ol_folios:
        folio_stems = t03[t03['folio_norm'] == folio]['stem'].tolist()
        if any(v in folio_stems for v in cooking_verbs):
            cooccur_count += 1
    
    pct = cooccur_count / len(ol_folios) * 100 if len(ol_folios) > 0 else 0
    print(f"\nol (water) + cooking verbs: {cooccur_count}/{len(ol_folios)} folios ({pct:.1f}%)")
    
    if pct > 50:
        print("  ✓ Strong co-occurrence - supports 'water' mapping")
    elif pct > 30:
        print("  ⚠ Moderate co-occurrence - weak support")
    else:
        print("  ✗ Weak co-occurrence - challenges 'water' mapping")

# Prediction 2: qokar (oil) should appear in Herbal section
if 'qokar' in type_b_stems:
    qokar_total = len(t03[t03['stem'] == 'qokar'])
    qokar_herbal = len(t03[(t03['stem'] == 'qokar') & (t03['section'] == 'Herbal')])
    
    if qokar_total > 0:
        pct = qokar_herbal / qokar_total * 100
        print(f"\nqokar (oil) in Herbal: {qokar_herbal}/{qokar_total} ({pct:.1f}%)")
        
        if pct > 40:
            print("  ✓ Predominantly in Herbal - supports 'oil' mapping")
        elif pct > 20:
            print("  ⚠ Some Herbal presence - weak support")
        else:
            print("  ✗ Rare in Herbal - challenges 'oil' mapping")

# Prediction 3: kar (parsley) should co-occur with other herbs
if 'kar' in type_b_stems:
    kar_folios = t03[t03['stem'] == 'kar']['folio_norm'].unique()
    herb_stems = ['dar', 'cho', 'dair', 'sho']  # rue, mint, celery, rose
    
    if len(kar_folios) > 0:
        cooccur_count = 0
        for folio in kar_folios:
            folio_stems = t03[t03['folio_norm'] == folio]['stem'].tolist()
            if any(h in folio_stems for h in herb_stems):
                cooccur_count += 1
        
        pct = cooccur_count / len(kar_folios) * 100
        print(f"\nkar (parsley) + other herbs: {cooccur_count}/{len(kar_folios)} folios ({pct:.1f}%)")
        
        if pct > 50:
            print("  ✓ Strong herb co-occurrence - supports 'parsley' mapping")
        elif pct > 30:
            print("  ⚠ Moderate co-occurrence - weak support")
        else:
            print("  ✗ Weak co-occurrence - challenges 'parsley' mapping")

print(f"\n{'='*80}")
print(f"OVERALL ASSESSMENT")
print(f"{'='*80}")

print("\nFor each Type B stem, evaluate:")
print("  1. Does it appear in expected sections?")
print("  2. Does it co-occur with Type A stems?")
print("  3. Do co-occurrence patterns make semantic sense?")
print("\nStems that fail 2+ tests should be considered INCORRECT mappings.")

