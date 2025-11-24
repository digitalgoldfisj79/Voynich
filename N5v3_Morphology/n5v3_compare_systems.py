#!/usr/bin/env python3
"""
N5v3: Morphological System Comparison
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"
OUTPUT = BASE / "N5v3_Morphology"

print("="*80)
print("N5v3: MORPHOLOGICAL SYSTEM COMPARISON")
print("="*80)

# Load Voynich morphology
print("\n[1/4] Loading Voynich morphology...")

v_suffixes = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
# Use token_count column
v_suffixes = v_suffixes.dropna(subset=['suffix'])  # Drop NULL
voynich_suffix_inv = dict(zip(v_suffixes['suffix'], v_suffixes['token_count']))

v_stems_df = pd.read_csv(N4 / "PhaseM/out/m06_stem_inventory.tsv", sep='\t')
v_stems = v_stems_df['stem'].tolist()

voynich_prefix_inv = Counter()
for stem in v_stems:
    s = str(stem)
    if len(s) >= 2:
        voynich_prefix_inv[s[:2]] += 1
    if len(s) >= 3:
        voynich_prefix_inv[s[:3]] += 1

print(f"  Voynich: {len(v_stems)} stems, {len(voynich_suffix_inv)} suffix types")
print(f"  Top suffixes: {list(voynich_suffix_inv.keys())[:5]}")

# Load Romance languages
print("\n[2/4] Loading Romance languages...")

languages = ['latin', 'occitan', 'catalan', 'italian', 'french']
romance_morph = {}

for lang in languages:
    stem_file = TOK / f"{lang}_stems.txt"
    stems = stem_file.read_text().strip().split('\n') if stem_file.exists() else []
    
    suffix_file = TOK / f"{lang}_suffixes.tsv"
    if suffix_file.exists():
        suf_df = pd.read_csv(suffix_file, sep='\t')
        suffixes = dict(zip(suf_df['suffix'], suf_df['count']))
    else:
        suffixes = {}
    
    prefix_file = TOK / f"{lang}_prefixes.tsv"
    if prefix_file.exists():
        pre_df = pd.read_csv(prefix_file, sep='\t')
        prefixes = dict(zip(pre_df['prefix'], pre_df['count']))
    else:
        prefixes = {}
    
    romance_morph[lang] = {
        'stems': stems,
        'suffixes': suffixes,
        'prefixes': prefixes
    }
    
    print(f"  {lang.capitalize()}: {len(stems)} stems, {len(suffixes)} suffixes, {len(prefixes)} prefixes")

# Compare systems
print("\n[3/4] Comparing morphological systems...")

def inventory_overlap(v_inv, l_inv, top_n=30):
    """Compare top N patterns from each inventory"""
    v_top = set(sorted(v_inv.keys(), key=lambda k: v_inv[k], reverse=True)[:top_n])
    l_top = set(sorted(l_inv.keys(), key=lambda k: l_inv[k], reverse=True)[:top_n])
    
    overlap = len(v_top & l_top)
    union = len(v_top | l_top)
    jaccard = overlap / union if union > 0 else 0
    
    return {
        'overlap': overlap,
        'jaccard': jaccard,
        'shared': sorted(list(v_top & l_top))[:10]  # Top 10 shared
    }

results = []

for lang, morph in romance_morph.items():
    suf_match = inventory_overlap(voynich_suffix_inv, morph['suffixes'])
    pre_match = inventory_overlap(dict(voynich_prefix_inv), morph['prefixes'])
    
    combined = (suf_match['jaccard'] + pre_match['jaccard']) / 2
    
    results.append({
        'language': lang.capitalize(),
        'suffix_overlap': suf_match['overlap'],
        'suffix_jaccard': round(suf_match['jaccard'], 3),
        'suffix_shared': ', '.join(suf_match['shared'][:5]),
        'prefix_overlap': pre_match['overlap'],
        'prefix_jaccard': round(pre_match['jaccard'], 3),
        'prefix_shared': ', '.join(pre_match['shared'][:5]),
        'combined_score': round(combined, 3)
    })

df = pd.DataFrame(results)
df = df.sort_values('combined_score', ascending=False)

# Save
print("\n[4/4] Saving results...")

OUTPUT.mkdir(exist_ok=True)
output_file = OUTPUT / "n5v3_morphology_comparison.tsv"
df.to_csv(output_file, sep='\t', index=False)
print(f"✓ Saved: {output_file}")

# Display
print("\n" + "="*80)
print("MORPHOLOGICAL SYSTEM RANKINGS")
print("="*80)

for _, row in df.iterrows():
    print(f"\n{row['language']}:")
    print(f"  Suffixes: {row['suffix_overlap']}/30 overlap (Jaccard={row['suffix_jaccard']:.3f})")
    if row['suffix_shared']:
        print(f"    Shared: {row['suffix_shared']}")
    print(f"  Prefixes: {row['prefix_overlap']}/30 overlap (Jaccard={row['prefix_jaccard']:.3f})")
    if row['prefix_shared']:
        print(f"    Shared: {row['prefix_shared']}")
    print(f"  COMBINED: {row['combined_score']:.3f}")

best = df.iloc[0]
print("\n" + "="*80)
print(f"🏆 BEST MORPHOLOGICAL MATCH: {best['language']}")
print(f"   Combined score: {best['combined_score']:.3f}")
print("="*80)

print("\n📊 INTERPRETATION:")
print("  • Jaccard > 0.3 = Strong morphological similarity")
print("  • Jaccard 0.1-0.3 = Moderate (expected for Romance family)")
print("  • Jaccard < 0.1 = Weak or unrelated")

print("\n⚠️ IMPORTANT:")
print("  • This tests MORPHOLOGICAL SYSTEMS (affix patterns)")
print("  • NOT individual word translations")
print("  • High score = similar grammatical structure")
print("  • Does NOT prove it IS that language")

print("\n✅ N5v3 Morphological System Comparison Complete")
