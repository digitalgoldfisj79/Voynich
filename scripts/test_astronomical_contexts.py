#!/usr/bin/env python3
"""
Astronomical Anomaly Investigation: Context Analysis

Tests: Do our stems appear in contexts that make sense for pharmaceutical terms?
Or are they just generic frequent words?
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

print("="*80)
print("ASTRONOMICAL SECTION: CONTEXT ANALYSIS")
print("="*80)

# Load data
HOME = Path.home()
t03_path = HOME / "randomization_test/t03_enriched_translations.tsv"
t3_path = HOME / "randomization_test/t3_lexical_lexicon.tsv"

t03 = pd.read_csv(t03_path, sep='\t')
t3 = pd.read_csv(t3_path, sep='\t')

# Get Astronomical section
astro = t03[t03['section'] == 'Astronomical'].copy()
non_astro = t03[t03['section'] != 'Astronomical'].copy()

print(f"\nAstronomical tokens: {len(astro)}")
print(f"Non-Astronomical tokens: {len(non_astro)}")

# Get our stems
our_stems = t3['stem'].tolist()
stem_to_lemma = dict(zip(t3['stem'], t3['lemma_latin']))

print(f"\n{'='*80}")
print(f"STEM DISTRIBUTION: ASTRONOMICAL vs REST")
print(f"{'='*80}")

enrichment_scores = []

for stem in our_stems:
    # Count in Astronomical
    astro_count = len(astro[astro['stem'] == stem])
    astro_freq = astro_count / len(astro) if len(astro) > 0 else 0
    
    # Count in rest
    non_astro_count = len(non_astro[non_astro['stem'] == stem])
    non_astro_freq = non_astro_count / len(non_astro) if len(non_astro) > 0 else 0
    
    # Enrichment ratio
    if non_astro_freq > 0:
        enrichment = astro_freq / non_astro_freq
    else:
        enrichment = float('inf') if astro_freq > 0 else 1.0
    
    lemma = stem_to_lemma.get(stem, '???')
    
    enrichment_scores.append({
        'stem': stem,
        'lemma': lemma,
        'astro_count': astro_count,
        'non_astro_count': non_astro_count,
        'astro_freq': astro_freq * 100,
        'non_astro_freq': non_astro_freq * 100,
        'enrichment': enrichment
    })

# Sort by enrichment
enrichment_df = pd.DataFrame(enrichment_scores).sort_values('enrichment', ascending=False)

print("\nStems ENRICHED in Astronomical (enrichment > 1.5):")
enriched = enrichment_df[enrichment_df['enrichment'] > 1.5]
for _, row in enriched.iterrows():
    print(f"  {row['stem']:10s} → {row['lemma']:20s} | Astro: {row['astro_count']:3.0f} ({row['astro_freq']:5.2f}%) | Rest: {row['non_astro_count']:4.0f} ({row['non_astro_freq']:5.2f}%) | Enrichment: {row['enrichment']:.2f}×")

print("\nStems DEPLETED in Astronomical (enrichment < 0.5):")
depleted = enrichment_df[enrichment_df['enrichment'] < 0.5]
for _, row in depleted.iterrows():
    print(f"  {row['stem']:10s} → {row['lemma']:20s} | Astro: {row['astro_count']:3.0f} ({row['astro_freq']:5.2f}%) | Rest: {row['non_astro_count']:4.0f} ({row['non_astro_freq']:5.2f}%) | Enrichment: {row['enrichment']:.2f}×")

print(f"\n{'='*80}")
print(f"CO-OCCURRENCE ANALYSIS")
print(f"{'='*80}")

print("\nIn Astronomical: What stems appear TOGETHER?")

# For each folio in Astronomical, get stem pairs that co-occur
astro_folios = astro['folio_norm'].unique()

cooccurrence = Counter()

for folio in astro_folios:
    folio_data = astro[astro['folio_norm'] == folio]
    folio_stems = [s for s in folio_data['stem'] if s in our_stems]
    
    # Count pairs
    for i, stem1 in enumerate(folio_stems):
        for stem2 in folio_stems[i+1:]:
            if stem1 != stem2:
                pair = tuple(sorted([stem1, stem2]))
                cooccurrence[pair] += 1

print("\nTop 15 stem pairs in Astronomical section:")
for (s1, s2), count in cooccurrence.most_common(15):
    lemma1 = stem_to_lemma.get(s1, '???')
    lemma2 = stem_to_lemma.get(s2, '???')
    print(f"  {s1:8s} ({lemma1:15s}) + {s2:8s} ({lemma2:15s}): {count} folios")

print(f"\n{'='*80}")
print(f"SEMANTIC COHERENCE TEST")
print(f"{'='*80}")

print("\nIf our mappings are correct, we expect:")
print("  - Herb stems (dar→rue, cho→mint) to co-occur")
print("  - Process stems (ar→grind, al→mix) to co-occur")
print("  - Herbs and processes to co-occur (recipes)")
print("\nIf our mappings are wrong:")
print("  - Random co-occurrence patterns")
print("  - No semantic clustering")

# Categorize our stems
herbs = []
processes = []
substances = []

for stem in our_stems:
    lemma = stem_to_lemma.get(stem, '')
    gloss = t3[t3['stem'] == stem]['gloss_en'].values
    gloss = gloss[0] if len(gloss) > 0 else ''
    
    # Simple categorization based on gloss
    if any(x in gloss.lower() for x in ['herb', 'mint', 'rue', 'rose', 'dill', 'parsley', 'sage', 'celery']):
        herbs.append(stem)
    elif any(x in gloss.lower() for x in ['grind', 'mix', 'cook', 'boil', 'pour', 'burn', 'place']):
        processes.append(stem)
    elif any(x in gloss.lower() for x in ['water', 'oil', 'juice', 'honey', 'humor', 'fluid']):
        substances.append(stem)

print(f"\nOur categorization:")
print(f"  Herbs: {herbs}")
print(f"  Processes: {processes}")
print(f"  Substances: {substances}")

# Check if herbs co-occur with processes in Astronomical
herb_process_pairs = []
for (s1, s2), count in cooccurrence.items():
    if (s1 in herbs and s2 in processes) or (s1 in processes and s2 in herbs):
        herb_process_pairs.append(((s1, s2), count))

herb_process_pairs.sort(key=lambda x: x[1], reverse=True)

print(f"\nHerb + Process pairs in Astronomical (recipe-like):")
if herb_process_pairs:
    for (s1, s2), count in herb_process_pairs[:10]:
        lemma1 = stem_to_lemma.get(s1, '???')
        lemma2 = stem_to_lemma.get(s2, '???')
        print(f"  {s1:8s} ({lemma1:15s}) + {s2:8s} ({lemma2:15s}): {count} folios")
else:
    print("  (No herb+process pairs found)")

print(f"\n{'='*80}")
print(f"INTERPRETATION")
print(f"{'='*80}")

if len(herb_process_pairs) > 5:
    print("✓ Strong evidence: Herbs and processes co-occur frequently")
    print("  This supports pharmaceutical/recipe interpretation")
    print("  Our Latin mappings may be correct")
elif len(herb_process_pairs) > 2:
    print("⚠ Moderate evidence: Some herb+process co-occurrence")
    print("  Weak support for recipe interpretation")
else:
    print("✗ No evidence: Herbs and processes don't co-occur")
    print("  This suggests our mappings may be incorrect")
    print("  Or Astronomical is not pharmaceutical content")

