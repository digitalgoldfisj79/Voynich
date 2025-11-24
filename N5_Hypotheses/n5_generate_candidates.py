#!/usr/bin/env python3
"""
N5 Hypothesis Generation: Structural Similarity to Latin
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
N5_OUT = BASE / "N5_Hypotheses"

print("="*80)
print("N5: HYPOTHESIS GENERATION (V-SPACE → E-SPACE)")
print("="*80)

# ============================================
# LOAD V-SPACE FEATURES
# ============================================

print("\n[1/6] Loading V-space features from N4...")

# Load Phase90 and aggregate to unique tokens
phase90 = pd.read_csv(N4 / "Phase90/out/p90_token_profiles.tsv", sep='\t')

# Get unique tokens with their max frequency
stems_with_freq = phase90.groupby('token')['freq'].max().reset_index()
stems_with_freq.columns = ['stem', 'stem_freq']
stems_with_freq = stems_with_freq.sort_values('stem_freq', ascending=False)

print(f"  ✓ Loaded {len(stems_with_freq)} unique stems")

# ============================================
# LOAD LATIN CORPUS
# ============================================

print("\n[2/6] Loading Latin corpus...")

latin_file = BASE / "../ATTIC/metadata_contaminated/latin_lemmas_by_domain.tsv"

if latin_file.exists():
    latin_corpus = pd.read_csv(latin_file, sep='\t')
    latin_corpus = latin_corpus[['lemma', 'gloss_en', 'frequency', 'source']].drop_duplicates()
    print(f"  ✓ Loaded {len(latin_corpus)} Latin lemmas")
else:
    latin_corpus = pd.DataFrame({
        'lemma': ['coquo', 'misceo', 'tero', 'aqua', 'ruta', 'rosa'],
        'gloss_en': ['cook', 'mix', 'grind', 'water', 'rue', 'rose'],
        'frequency': [17, 8, 12, 45, 30, 12],
        'source': ['fallback'] * 6
    })
    print(f"  ✓ Using fallback ({len(latin_corpus)} lemmas)")

# ============================================
# STRUCTURAL FEATURES
# ============================================

print("\n[3/6] Computing structural features...")

def extract_features(stem):
    return {
        'length': len(stem),
        'prefix': stem[:2] if len(stem) >= 2 else stem,
        'suffix': stem[-2:] if len(stem) >= 2 else stem,
        'vowels': sum(1 for c in stem if c in 'aeiou'),
        'consonants': sum(1 for c in stem if c not in 'aeiou')
    }

def structural_similarity(v_feat, l_stem):
    l_feat = extract_features(l_stem)
    score = 0.0
    
    # Length
    score += max(0, 1 - abs(v_feat['length'] - l_feat['length'])/5) * 0.3
    
    # Prefix
    if v_feat['prefix'] == l_feat['prefix']:
        score += 0.3
    elif v_feat['prefix'][0] == l_feat['prefix'][0]:
        score += 0.15
    
    # Suffix
    if v_feat['suffix'] == l_feat['suffix']:
        score += 0.2
    
    # Vowel ratio
    v_ratio = v_feat['vowels'] / max(1, v_feat['consonants'])
    l_ratio = l_feat['vowels'] / max(1, l_feat['consonants'])
    score += max(0, 1 - abs(v_ratio - l_ratio)) * 0.2
    
    return min(1.0, score)

# ============================================
# GENERATE HYPOTHESES
# ============================================

print("\n[4/6] Generating hypotheses for top 100 stems...")

TOP_N = 100
top_stems = stems_with_freq.head(TOP_N)

candidates = []

for idx, stem_row in top_stems.iterrows():
    stem = str(stem_row['stem'])
    v_feat = extract_features(stem)
    
    # Match against Latin
    matches = []
    for _, lat_row in latin_corpus.iterrows():
        lat = str(lat_row['lemma'])
        sim = structural_similarity(v_feat, lat)
        
        if sim > 0.15:  # Threshold
            matches.append({
                'latin': lat,
                'gloss': lat_row['gloss_en'],
                'sim': sim,
                'lat_freq': lat_row['frequency']
            })
    
    # Top 5 matches
    matches.sort(key=lambda x: x['sim'], reverse=True)
    for rank, m in enumerate(matches[:5], 1):
        candidates.append({
            'stem': stem,
            'voynich_freq': int(stem_row['stem_freq']),
            'structural_signature': f"L{v_feat['length']}_P{v_feat['prefix']}_S{v_feat['suffix']}",
            'candidate_rank': rank,
            'candidate_latin': m['latin'],
            'candidate_gloss': m['gloss'],
            'confidence_structural': round(m['sim'], 3),
            'latin_frequency': m['lat_freq'],
            'notes': 'Structural_only'
        })

candidates_df = pd.DataFrame(candidates)

print(f"  ✓ Generated {len(candidates_df)} hypotheses")
print(f"  ✓ Covering {candidates_df['stem'].nunique()} unique stems")

# ============================================
# SAVE
# ============================================

print("\n[5/6] Saving...")

output = N5_OUT / "h5_candidates.tsv"
candidates_df.to_csv(output, sep='\t', index=False)

print(f"  ✓ Saved: {output}")

# ============================================
# SUMMARY
# ============================================

print("\n[6/6] Summary...")

print(f"\nTop 10 stems by candidate count:")
for stem in candidates_df['stem'].value_counts().head(10).index:
    count = len(candidates_df[candidates_df['stem'] == stem])
    freq = candidates_df[candidates_df['stem'] == stem]['voynich_freq'].iloc[0]
    top_match = candidates_df[candidates_df['stem'] == stem].iloc[0]['candidate_latin']
    conf = candidates_df[candidates_df['stem'] == stem].iloc[0]['confidence_structural']
    print(f"  {stem:<10} freq={freq:<4} candidates={count} top={top_match} ({conf:.2f})")

print(f"\nConfidence: mean={candidates_df['confidence_structural'].mean():.3f}, max={candidates_df['confidence_structural'].max():.3f}")

print("\n" + "="*80)
print("✅ N5 COMPLETE - Hypotheses generated (NOT validated!)")
print("="*80)
print("\nNext: Build N6 validation tests")

