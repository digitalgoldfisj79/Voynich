#!/usr/bin/env python3
"""
Test Currier A and B separately against medieval Occitan
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("CURRIER A vs B vs MEDIEVAL OCCITAN")
print("="*80)

# From previous analysis
currier_data = {
    'A': {'y': 37.3, 'aiin': 16.8, 'ol': 15.7, 'or': 9.0, 'al': 7.8, 'ain': 5.0, 'ody': 5.0, 'am': 3.3},
    'B': {'y': 60.8, 'aiin': 8.9, 'ol': 8.2, 'al': 6.3, 'ain': 6.1, 'or': 4.3, 'ody': 3.2, 'am': 2.2}
}

def kl_divergence(p_dict, q_dict):
    all_keys = set(p_dict.keys()) | set(q_dict.keys())
    p = np.array([p_dict.get(k, 0.01) for k in all_keys])
    q = np.array([q_dict.get(k, 0.01) for k in all_keys])
    p = p / p.sum()
    q = q / q.sum()
    eps = 1e-10
    return np.sum(p * np.log2((p + eps) / (q + eps)))

# Load medieval Occitan
occ_suf = pd.read_csv(TOK / "occitan_medieval_suffixes.tsv", sep='\t')
occ_dict = dict(zip(occ_suf['suffix'], occ_suf['count'] / occ_suf['count'].sum() * 100))

# Load modern French
fr_suf = pd.read_csv(TOK / "french_suffixes.tsv", sep='\t')
fr_dict = dict(zip(fr_suf['suffix'], fr_suf['count'] / fr_suf['count'].sum() * 100))

# Load medieval Latin
lat_suf = pd.read_csv(TOK / "medieval_latin_suffixes.tsv", sep='\t')
lat_dict = dict(zip(lat_suf['suffix'], lat_suf['count'] / lat_suf['count'].sum() * 100))

print("\nCURRIER A (Herbal - Formal, H=2.578):")
print(f"  vs Medieval Occitan:  KL={kl_divergence(currier_data['A'], occ_dict):.3f}")
print(f"  vs Modern French:     KL={kl_divergence(currier_data['A'], fr_dict):.3f}")
print(f"  vs Medieval Latin:    KL={kl_divergence(currier_data['A'], lat_dict):.3f}")

print("\nCURRIER B (Other - Informal, H=2.017):")
print(f"  vs Medieval Occitan:  KL={kl_divergence(currier_data['B'], occ_dict):.3f}")
print(f"  vs Modern French:     KL={kl_divergence(currier_data['B'], fr_dict):.3f}")
print(f"  vs Medieval Latin:    KL={kl_divergence(currier_data['B'], lat_dict):.3f}")

print("\n" + "="*80)
print("CRITICAL QUESTION")
print("="*80)

print("\n❓ Why does modern French (1845) match better than")
print("   medieval Occitan (correct period/region)?")
print("\n   Possible explanations:")
print("   A) Compression creates modern-like distribution")
print("   B) It's NOT medieval at all")
print("   C) Modern French accidentally similar")
print("   D) Occitan dictionary incomplete/biased")

