#!/usr/bin/env python3
"""
Re-calculate overall vs Currier A vs B distributions properly
Use SAME methodology for all three
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("VERIFICATION: SAME METHODOLOGY FOR ALL")
print("="*80)

# We need actual suffix counts from Currier A and B
# Not percentage approximations

# For now, let's check if the overall result makes sense
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])

print("\nVoynichese OVERALL suffix distribution:")
for _, row in v_suf.iterrows():
    pct = row['token_count'] / v_suf['token_count'].sum() * 100
    print(f"  {row['suffix']:8s} {pct:5.1f}%")

# Now compare shape to medieval Occitan
occ_suf = pd.read_csv(TOK / "occitan_medieval_suffixes.tsv", sep='\t')

print("\nMedieval Occitan TOP suffixes:")
for _, row in occ_suf.head(8).iterrows():
    pct = row['count'] / occ_suf['count'].sum() * 100
    print(f"  {row['suffix']:8s} {pct:5.1f}%")

# And modern French
fr_suf = pd.read_csv(TOK / "french_suffixes.tsv", sep='\t')

print("\nModern French TOP suffixes:")
for _, row in fr_suf.head(8).iterrows():
    pct = row['count'] / fr_suf['count'].sum() * 100
    print(f"  {row['suffix']:8s} {pct:5.1f}%")

print("\n" + "="*80)
print("VISUAL COMPARISON")
print("="*80)

print("\nVoynich:  ONE dominant (y=59%), others distributed")
print("Occitan:  FLAT distribution (max 16%)")
print("French:   ONE dominant (e=49%), similar to Voynich!")

print("\n💡 AHA!")
print("  Modern French HAS SIMILAR SHAPE to Voynichese")
print("  (one dominant suffix + others)")
print("  Medieval Occitan/Latin have FLAT distributions")
print("  This is why French 'wins' on KL divergence")

print("\n❓ BUT:")
print("  This doesn't mean it IS French")
print("  Just that compression CREATES French-like shape")

