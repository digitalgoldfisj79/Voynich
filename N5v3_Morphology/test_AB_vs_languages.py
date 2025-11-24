#!/usr/bin/env python3
"""
Compare Currier A and B separately to all languages
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("CURRIER A vs B vs LANGUAGES")
print("="*80)

# Currier A and B distributions (from previous test)
currier_data = {
    'A': {'y': 37.3, 'aiin': 16.8, 'ol': 15.7, 'or': 9.0, 'al': 7.8, 'ain': 5.0, 'ody': 5.0, 'am': 3.3},
    'B': {'y': 60.8, 'aiin': 8.9, 'ol': 8.2, 'al': 6.3, 'ain': 6.1, 'or': 4.3, 'ody': 3.2, 'am': 2.2}
}

def kl_divergence(p_dict, q_dict):
    """KL divergence between two distributions"""
    # Align keys
    all_keys = set(p_dict.keys()) | set(q_dict.keys())
    p = np.array([p_dict.get(k, 0.01) for k in all_keys])
    q = np.array([q_dict.get(k, 0.01) for k in all_keys])
    
    # Normalize
    p = p / p.sum()
    q = q / q.sum()
    
    eps = 1e-10
    return np.sum(p * np.log2((p + eps) / (q + eps)))

# Load language distributions
languages = {
    'Medieval_Latin': 'medieval_latin',
    'Classical_Latin': 'latin',
    'Modern_French': 'french',
    'Modern_Italian': 'italian',
    'Modern_Catalan': 'catalan'
}

print("\nComparing Currier A (Herbal - Formal):\n")

for lang_name, lang_file in languages.items():
    suf_file = TOK / f"{lang_file}_suffixes.tsv"
    if not suf_file.exists():
        continue
    
    l_suf = pd.read_csv(suf_file, sep='\t')
    l_dict = dict(zip(l_suf['suffix'], l_suf['count'] / l_suf['count'].sum() * 100))
    
    kl = kl_divergence(currier_data['A'], l_dict)
    print(f"  {lang_name:20s} KL={kl:.3f}")

print("\nComparing Currier B (Other - Informal):\n")

for lang_name, lang_file in languages.items():
    suf_file = TOK / f"{lang_file}_suffixes.tsv"
    if not suf_file.exists():
        continue
    
    l_suf = pd.read_csv(suf_file, sep='\t')
    l_dict = dict(zip(l_suf['suffix'], l_suf['count'] / l_suf['count'].sum() * 100))
    
    kl = kl_divergence(currier_data['B'], l_dict)
    print(f"  {lang_name:20s} KL={kl:.3f}")

print("\n✅ Complete")

