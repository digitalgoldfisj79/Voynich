#!/usr/bin/env python3
"""
Visualize WHY modern French matches better than medieval Latin
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("DISTRIBUTION SHAPE COMPARISON")
print("="*80)

# Voynich
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])
v_total = v_suf['token_count'].sum()

print("\n📜 VOYNICHESE:")
for _, row in v_suf.iterrows():
    pct = row['token_count'] / v_total * 100
    bar = "█" * int(pct / 2)
    print(f"  {row['suffix']:8s} {pct:5.1f}% {bar}")

# Medieval Latin Medical
print("\n📚 MEDIEVAL LATIN MEDICAL:")
med_suf = pd.read_csv(TOK / "medieval_latin_suffixes.tsv", sep='\t')
med_total = med_suf['count'].sum()
for _, row in med_suf.head(10).iterrows():
    pct = row['count'] / med_total * 100
    bar = "█" * int(pct / 2)
    print(f"  -{row['suffix']:8s} {pct:5.1f}% {bar}")

# Modern French
print("\n🇫🇷 MODERN FRENCH:")
fr_suf = pd.read_csv(TOK / "french_suffixes.tsv", sep='\t')
fr_total = fr_suf['count'].sum()
for _, row in fr_suf.head(10).iterrows():
    pct = row['count'] / fr_total * 100
    bar = "█" * int(pct / 2)
    print(f"  -{row['suffix']:8s} {pct:5.1f}% {bar}")

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)

print("\nVoynichese pattern:")
print("  • ONE dominant suffix (y = 59%)")
print("  • Few types (8 total)")
print("  • Highly skewed distribution")

print("\nMedieval Latin:")
print("  • MANY suffixes (25 types)")
print("  • More even distribution")
print("  • High diversity (entropy=3.90)")

print("\nModern French:")
print("  • ONE dominant suffix (e = 49%)")
print("  • Moderate types (21)")
print("  • Skewed like Voynichese (entropy=2.70)")

print("\n💡 INSIGHT:")
print("  Modern French accidentally has Voynichese-like")
print("  distribution shape (one dominant suffix)")
print("  Medieval Latin has too much diversity")

