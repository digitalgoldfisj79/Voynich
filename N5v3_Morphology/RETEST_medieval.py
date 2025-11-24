#!/usr/bin/env python3
"""
RE-RUN ALL TESTS WITH MEDIEVAL CORPORA

Comparing Voynichese to:
- Medieval Latin Medical (De Materia + Macer)
- Old French (Roman de la Rose, 13th c.) - still need to tokenize
- Classical Latin (Whitaker - for comparison)
- Modern French/Italian (for comparison)
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("COMPREHENSIVE MEDIEVAL CORPUS COMPARISON")
print("="*80)

# Helper functions
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

def inventory_overlap(v_inv, l_inv, top_n=30):
    v_top = set(sorted(v_inv.keys(), key=lambda k: v_inv[k], reverse=True)[:top_n])
    l_top = set(sorted(l_inv.keys(), key=lambda k: l_inv[k], reverse=True)[:top_n])
    overlap = len(v_top & l_top)
    union = len(v_top | l_top)
    jaccard = overlap / union if union > 0 else 0
    return {
        'overlap': overlap,
        'jaccard': jaccard,
        'shared': sorted(list(v_top & l_top))[:10]
    }

# Load Voynich
print("\n[1/4] Loading Voynich morphology...")
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])
voynich_suffix_inv = dict(zip(v_suf['suffix'], v_suf['token_count']))

v_counts = v_suf['token_count'].values
v_probs = v_counts / v_counts.sum()
v_entropy = entropy(v_probs)

print(f"  Voynich: {len(v_suf)} suffix types, H={v_entropy:.3f} bits")

# Languages to test
languages = {
    'Medieval_Latin_Medical': 'medieval_latin',
    'Classical_Latin': 'latin',
    'Modern_French': 'french',
    'Modern_Italian': 'italian',
    'Modern_Catalan': 'catalan'
}

print("\n[2/4] Loading all corpora...")

results = []

for lang_name, lang_file in languages.items():
    suf_file = TOK / f"{lang_file}_suffixes.tsv"
    
    if not suf_file.exists():
        print(f"  ⚠️ {lang_name}: Not found")
        continue
    
    l_suf = pd.read_csv(suf_file, sep='\t')
    l_inv = dict(zip(l_suf['suffix'], l_suf['count']))
    
    l_counts = l_suf['count'].values
    l_probs = l_counts / l_counts.sum()
    l_entropy = entropy(l_probs)
    
    # Test 1: Distribution similarity (KL divergence)
    kl_div = kl_divergence(v_probs, l_probs)
    
    # Test 2: Inventory overlap (Jaccard)
    overlap_result = inventory_overlap(voynich_suffix_inv, l_inv)
    
    results.append({
        'language': lang_name,
        'period': 'Medieval' if 'Medieval' in lang_name else ('Classical' if 'Classical' in lang_name else 'Modern'),
        'suffix_types': len(l_suf),
        'entropy': l_entropy,
        'entropy_diff': abs(v_entropy - l_entropy),
        'kl_divergence': kl_div,
        'jaccard': overlap_result['jaccard'],
        'overlap_count': overlap_result['overlap'],
        'shared_suffixes': ', '.join(overlap_result['shared'][:5])
    })
    
    print(f"  ✓ {lang_name:25s} Types={len(l_suf):3d} KL={kl_div:.3f} Jaccard={overlap_result['jaccard']:.3f}")

# Results
print("\n[3/4] Analyzing results...")

df = pd.DataFrame(results)

# Sort by KL divergence (best = lowest)
df_by_kl = df.sort_values('kl_divergence')

# Sort by Jaccard (best = highest)
df_by_jaccard = df.sort_values('jaccard', ascending=False)

print("\n" + "="*80)
print("TEST 1: DISTRIBUTION SIMILARITY (KL Divergence)")
print("="*80)
print("\nRanking (lower = more similar):\n")

for _, row in df_by_kl.iterrows():
    period_icon = "📜" if row['period'] == 'Medieval' else ("🏛️" if row['period'] == 'Classical' else "📰")
    print(f"{period_icon} {row['language']:28s} KL={row['kl_divergence']:6.3f}  Entropy={row['entropy']:.2f}  Shared={row['shared_suffixes']}")

print("\n" + "="*80)
print("TEST 2: INVENTORY OVERLAP (Jaccard Similarity)")
print("="*80)
print("\nRanking (higher = more similar):\n")

for _, row in df_by_jaccard.iterrows():
    period_icon = "📜" if row['period'] == 'Medieval' else ("🏛️" if row['period'] == 'Classical' else "📰")
    print(f"{period_icon} {row['language']:28s} Jaccard={row['jaccard']:5.3f}  Overlap={row['overlap_count']}/30")

# Save
print("\n[4/4] Saving results...")
output = BASE / "N5v3_Morphology/medieval_comparison_results.tsv"
df.to_csv(output, sep='\t', index=False)
print(f"✓ Saved: {output}")

# Final verdict
best_kl = df_by_kl.iloc[0]
best_jaccard = df_by_jaccard.iloc[0]

print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)

print(f"\n🏆 BEST DISTRIBUTION MATCH: {best_kl['language']}")
print(f"   KL divergence: {best_kl['kl_divergence']:.3f}")
print(f"   Period: {best_kl['period']}")

print(f"\n🏆 BEST INVENTORY MATCH: {best_jaccard['language']}")
print(f"   Jaccard: {best_jaccard['jaccard']:.3f}")
print(f"   Period: {best_jaccard['period']}")

print("\n📊 INTERPRETATION:")
print("  • KL < 0.5 = Very similar suffix usage patterns")
print("  • Jaccard > 0.1 = Significant morphological overlap")
print("  • Medieval vs Modern comparison now valid!")

print("\n✅ Complete - Results saved")

