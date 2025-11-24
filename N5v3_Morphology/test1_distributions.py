#!/usr/bin/env python3
"""
Test 1: Distribution comparison (no scipy)
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("TEST 1: MORPHOLOGICAL DISTRIBUTION COMPARISON")
print("="*80)

def entropy(probs):
    """Shannon entropy in bits"""
    probs = np.array(probs)
    probs = probs[probs > 0]  # Remove zeros
    return -np.sum(probs * np.log2(probs))

def kl_divergence(p, q):
    """KL divergence: how different is q from p"""
    p = np.array(p)
    q = np.array(q)
    
    # Align lengths
    min_len = min(len(p), len(q))
    p = p[:min_len]
    q = q[:min_len]
    
    # Normalize
    p = p / p.sum()
    q = q / q.sum()
    
    # KL divergence (with epsilon to avoid log(0))
    eps = 1e-10
    return np.sum(p * np.log2((p + eps) / (q + eps)))

# Load Voynich suffixes
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])

v_counts = v_suf['token_count'].values
v_probs = v_counts / v_counts.sum()
v_entropy = entropy(v_probs)

print(f"\nVoynich suffix distribution:")
print(f"  Types: {len(v_suf)}")
print(f"  Entropy: {v_entropy:.3f} bits")
print(f"  Top 5 suffixes: {list(v_suf['suffix'][:5])}")
print(f"  Top 5 frequencies: {[f'{p:.3f}' for p in v_probs[:5]]}")

# Compare to Romance languages
results = []

for lang in ['latin', 'italian', 'french', 'catalan']:
    suf_file = TOK / f"{lang}_suffixes.tsv"
    if not suf_file.exists():
        continue
    
    l_suf = pd.read_csv(suf_file, sep='\t')
    l_counts = l_suf['count'].values
    l_probs = l_counts / l_counts.sum()
    
    l_entropy = entropy(l_probs)
    entropy_diff = abs(v_entropy - l_entropy)
    kl_div = kl_divergence(v_probs, l_probs)
    
    results.append({
        'language': lang.capitalize(),
        'types': len(l_suf),
        'entropy': l_entropy,
        'entropy_diff': entropy_diff,
        'kl_divergence': kl_div
    })
    
    print(f"\n{lang.capitalize()}:")
    print(f"  Types: {len(l_suf)}")
    print(f"  Entropy: {l_entropy:.3f} bits")
    print(f"  Entropy diff: {entropy_diff:.3f}")
    print(f"  KL divergence: {kl_div:.3f}")

df = pd.DataFrame(results)
df = df.sort_values('kl_divergence')

print("\n" + "="*80)
print("RANKING BY DISTRIBUTION SIMILARITY")
print("="*80)

for _, row in df.iterrows():
    print(f"\n{row['language']}:")
    print(f"  KL divergence: {row['kl_divergence']:.3f} ⭐ (lower = more similar)")
    print(f"  Entropy match: {row['entropy_diff']:.3f}")

best = df.iloc[0]
print(f"\n🏆 BEST DISTRIBUTION MATCH: {best['language']}")
print(f"   KL divergence: {best['kl_divergence']:.3f}")

print("\n📊 INTERPRETATION:")
print("  KL < 0.5 = Very similar distributions")
print("  KL 0.5-1.5 = Moderately similar")
print("  KL > 1.5 = Different distributions")

print("\n✅ Test 1 complete")

