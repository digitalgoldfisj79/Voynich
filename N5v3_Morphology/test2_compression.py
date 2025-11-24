#!/usr/bin/env python3
"""
Test 2: Does each Voynich suffix map to MULTIPLE Romance endings?

If compressed, one Voynich suffix → many Latin endings
Example: Voynich "y" → Latin {-us, -um, -i, -o, -a}

Tests if Voynich affixes could be abbreviations
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("TEST 2: COMPRESSION MAPPING HYPOTHESIS")
print("="*80)

# Voynich suffixes with examples
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])

print(f"\nVoynich has {len(v_suf)} suffix types")
print("Testing: Could each map to MULTIPLE Romance endings?\n")

# Load Latin suffixes
latin_suf = pd.read_csv(TOK / "latin_suffixes.tsv", sep='\t')

# Hypothesis: Voynich suffixes are compressed classes
# Each Voynich suffix should correlate with a SET of Latin endings

# Group Latin endings by phonological similarity
latin_vowel_endings = latin_suf[latin_suf['suffix'].str.match(r'^[aeiou]', na=False)]
latin_cons_endings = latin_suf[~latin_suf['suffix'].str.match(r'^[aeiou]', na=False)]

print("HYPOTHESIS:")
print("  Voynich 'y' (vowel-like) → Latin vowel endings {-a, -e, -i, -o, -u}")
print("  Voynich 'aiin' (nasal) → Latin nasal endings {-am, -em, -im, -um}")
print("  Voynich 'ol/al' (liquid) → Latin liquid endings {-or, -er, -ar, -ur}")

print("\nLatin vowel endings:", list(latin_vowel_endings['suffix'][:10]))
print("Latin nasal endings:", [s for s in latin_suf['suffix'] if 'm' in s][:10])

print("\n✅ This test shows CONCEPT")
print("⚠️  Need actual compression rules to test properly")
print("💡 Suggests: Study medieval abbreviation systems")

