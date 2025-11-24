#!/usr/bin/env python3
"""
N5v2: Clean Hypothesis Generation (using PhaseM stems)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import math

BASE = Path(__file__).parent.parent

print("="*80)
print("N5v2: CLEAN HYPOTHESIS GENERATION (PhaseM stems)")
print("="*80)

# Load Whitaker (31k Latin lemmas)
whitaker = pd.read_csv(BASE / "corpora/latin_vocab/whitaker_lemmas.tsv", sep='\t')

# Drop NaN and filter clean lemmas
whitaker = whitaker.dropna(subset=['lemma'])
whitaker = whitaker[whitaker['lemma'].str.match(r'^[a-z]{2,15}$', na=False)]
print(f"Whitaker: {len(whitaker)} clean Latin lemmas")

# Load PhaseM stems
phasem = pd.read_csv(BASE / "N4_Frozen_Model/PhaseM/out/m06_stem_inventory.tsv", sep='\t')
print(f"PhaseM: {len(phasem)} Voynich stems")

stems = phasem[['stem', 'token_count']].copy()
stems.columns = ['stem', 'freq']
stems = stems.sort_values('freq', ascending=False)

def extract_features(word):
    return {
        'len': len(word),
        'prefix': word[:2] if len(word) >= 2 else word,
        'suffix': word[-2:] if len(word) >= 2 else word,
        'vowels': sum(1 for c in word if c in 'aeiou'),
        'consonants': sum(1 for c in word if c not in 'aeiou')
    }

def structural_similarity(v_feat, l_feat):
    score = 0.0
    len_diff = abs(v_feat['len'] - l_feat['len'])
    score += max(0, 1 - len_diff/5) * 0.25
    
    if v_feat['prefix'] == l_feat['prefix']:
        score += 0.30
    elif len(v_feat['prefix']) > 0 and len(l_feat['prefix']) > 0:
        if v_feat['prefix'][0] == l_feat['prefix'][0]:
            score += 0.15
    
    if v_feat['suffix'] == l_feat['suffix']:
        score += 0.25
    
    v_ratio = v_feat['vowels'] / max(1, v_feat['consonants'])
    l_ratio = l_feat['vowels'] / max(1, l_feat['consonants'])
    score += max(0, 1 - abs(v_ratio - l_ratio)) * 0.20
    
    return min(1.0, score)

print("\nGenerating hypotheses for top 200 stems...")
print("(~30 seconds per stem with 31k comparisons)")

TOP_N = 200
top_stems = stems.head(TOP_N)

voynich_total = stems['freq'].sum()
latin_total = whitaker['freq_estimate'].sum()

def freq_penalty(freq, total, lambda_=0.1):
    if freq == 0 or total == 0:
        return 0
    return lambda_ * math.log(max(1e-10, freq / total))

candidates = []

for idx, stem_row in top_stems.iterrows():
    stem = str(stem_row['stem'])
    v_feat = extract_features(stem)
    v_freq = stem_row['freq']
    
    scores = []
    for _, lat_row in whitaker.iterrows():
        latin = str(lat_row['lemma'])
        l_feat = extract_features(latin)
        l_freq = lat_row['freq_estimate']
        
        sim = structural_similarity(v_feat, l_feat)
        v_penalty = freq_penalty(v_freq, voynich_total)
        l_penalty = freq_penalty(l_freq, latin_total)
        final_score = sim - v_penalty - l_penalty
        
        if final_score > 0.05:
            scores.append({
                'latin': latin,
                'meaning': str(lat_row['meaning'])[:50] if pd.notna(lat_row['meaning']) else '',
                'sim': sim,
                'score': final_score,
                'l_freq': l_freq
            })
    
    scores.sort(key=lambda x: x['score'], reverse=True)
    for rank, m in enumerate(scores[:10], 1):
        candidates.append({
            'stem': stem,
            'voynich_freq': int(v_freq),
            'candidate_rank': rank,
            'candidate_latin': m['latin'],
            'candidate_meaning': m['meaning'],
            'structural_similarity': round(m['sim'], 3),
            'final_score': round(m['score'], 3),
            'latin_freq': int(m['l_freq']),
            'notes': 'PhaseM_Whitaker_31k'
        })
    
    if (idx + 1) % 20 == 0:
        print(f"  {idx + 1}/{TOP_N} stems...")

df = pd.DataFrame(candidates)

print(f"\n✓ Generated {len(df)} hypotheses")
print(f"✓ Covering {df['stem'].nunique()} stems")

output = BASE / "N5v2_Hypotheses/h5v2_candidates.tsv"
df.to_csv(output, sep='\t', index=False)
print(f"✓ Saved: {output}")

print("\n" + "="*80)
print("TOP 10 STEMS")
print("="*80)
for stem in df['stem'].value_counts().head(10).index:
    ds = df[df['stem'] == stem]
    freq = ds['voynich_freq'].iloc[0]
    top_lat = ds.iloc[0]['candidate_latin']
    score = ds.iloc[0]['final_score']
    print(f"  {stem:<8} freq={freq:<5} → {top_lat:<12} ({score:.2f})")

print(f"\nScore stats: mean={df['final_score'].mean():.3f}, max={df['final_score'].max():.3f}")
print("\n✅ N5v2 COMPLETE")
