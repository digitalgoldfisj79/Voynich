#!/usr/bin/env python3
"""
FINAL TEST: Add Medieval Occitan to comparison
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("FINAL COMPARISON: WITH MEDIEVAL OCCITAN")
print("="*80)

def entropy(probs):
    probs = np.array(probs)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

def kl_divergence(p, q):
    p = np.array(p)
    q = np.array(q)
    min_len = min(len(p), len(q))
    p = p[:min_len]
    q = q[:min_len]
    p = p / p.sum()
    q = q / q.sum()
    eps = 1e-10
    return np.sum(p * np.log2((p + eps) / (q + eps)))

# Load Voynich
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])
v_counts = v_suf['token_count'].values
v_probs = v_counts / v_counts.sum()
v_entropy = entropy(v_probs)

print(f"\nVoynichese: H={v_entropy:.3f} bits\n")

# Languages
languages = [
    ('Medieval_Occitan', 'occitan_medieval'),
    ('Medieval_Latin_Medical', 'medieval_latin'),
    ('Classical_Latin', 'latin'),
    ('Modern_French', 'french'),
    ('Modern_Italian', 'italian'),
    ('Modern_Catalan', 'catalan')
]

results = []

for lang_name, lang_file in languages:
    suf_file = TOK / f"{lang_file}_suffixes.tsv"
    
    if not suf_file.exists():
        print(f"  ⚠️ {lang_name}: Not found")
        continue
    
    l_suf = pd.read_csv(suf_file, sep='\t')
    l_counts = l_suf['count'].values
    l_probs = l_counts / l_counts.sum()
    l_entropy = entropy(l_probs)
    kl = kl_divergence(v_probs, l_probs)
    
    period_icon = "📜" if 'Medieval' in lang_name else ("🏛️" if 'Classical' in lang_name else "📰")
    
    results.append({
        'language': lang_name,
        'period': lang_name.split('_')[0],
        'entropy': l_entropy,
        'kl': kl
    })
    
    print(f"{period_icon} {lang_name:25s} KL={kl:.3f}  H={l_entropy:.2f}")

df = pd.DataFrame(results).sort_values('kl')

print("\n" + "="*80)
print("FINAL RANKING")
print("="*80)

for i, row in df.iterrows():
    icon = "📜" if row['period'] == 'Medieval' else ("🏛️" if row['period'] == 'Classical' else "📰")
    print(f"\n{i+1}. {icon} {row['language']}")
    print(f"   KL divergence: {row['kl']:.3f}")
    print(f"   Entropy: {row['entropy']:.2f} bits")

best = df.iloc[0]
print(f"\n" + "="*80)
print(f"🏆 BEST MATCH: {best['language']}")
print(f"   KL = {best['kl']:.3f}")
print("="*80)

print("\n✅ Complete")

