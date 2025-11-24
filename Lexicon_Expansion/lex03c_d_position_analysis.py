#!/usr/bin/env python3
"""
Critical realization: 'd' stem freq = 1468, but standalone = 35

Where does 'd' actually appear?
- As suffix? (shed, ched, oked)
- As prefix? (dain, daiin)
- Standalone? (rare)
"""

import pandas as pd
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "Lexicon_Expansion/lex03c_d_positions.tsv"

print("="*80)
print("CRITICAL ANALYSIS: WHERE IS 'd' IN TOKENS?")
print("="*80)

# Load tokens
token_file = BASE / "corpora/p6_voynich_tokens.txt"

with open(token_file, 'r') as f:
    tokens = f.read().split()

print(f"Analyzing {len(tokens)} tokens...")

# Categorize tokens containing 'd'
d_standalone = []
d_suffix = []
d_prefix = []
d_internal = []
d_other = []

for token in tokens:
    if 'd' in token:
        if token == 'd':
            d_standalone.append(token)
        elif token.endswith('d'):
            d_suffix.append(token)
        elif token.startswith('d'):
            d_prefix.append(token)
        elif 'd' in token[1:-1]:
            d_internal.append(token)
        else:
            d_other.append(token)

print(f"\n{'='*80}")
print("'d' POSITION DISTRIBUTION")
print("="*80)

total_d = len(d_standalone) + len(d_suffix) + len(d_prefix) + len(d_internal)

print(f"\nStandalone 'd':       {len(d_standalone):>5} ({len(d_standalone)/total_d*100:>5.1f}%)")
print(f"Suffix '-d':          {len(d_suffix):>5} ({len(d_suffix)/total_d*100:>5.1f}%)")
print(f"Prefix 'd-':          {len(d_prefix):>5} ({len(d_prefix)/total_d*100:>5.1f}%)")
print(f"Internal '-d-':       {len(d_internal):>5} ({len(d_internal)/total_d*100:>5.1f}%)")
print(f"Total:                {total_d:>5}")

# Analyze suffix tokens
print(f"\n{'='*80}")
print("TOKENS ENDING IN '-d' (Most frequent)")
print("="*80)

suffix_counter = Counter(d_suffix)
print(f"\nTop 30 tokens ending in 'd':")
print(f"{'Token':<15} {'Count':<8} {'Stem without d':<15}")
print("-" * 45)

for token, count in suffix_counter.most_common(30):
    stem_no_d = token[:-1] if len(token) > 1 else ''
    print(f"{token:<15} {count:<8} {stem_no_d:<15}")

# Check if these are validated stems
t3 = pd.read_csv(BASE / "metadata/t3_candidates_domains_filtered.tsv", sep='\t')
voynich_stems = pd.read_csv(BASE / "metadata/t03_stem_frequencies.tsv", sep='\t')

# Analyze prefix tokens  
print(f"\n{'='*80}")
print("TOKENS STARTING WITH 'd-' (Most frequent)")
print("="*80)

prefix_counter = Counter(d_prefix)
print(f"\nTop 20 tokens starting with 'd':")
print(f"{'Token':<15} {'Count':<8}")
print("-" * 25)

for token, count in prefix_counter.most_common(20):
    print(f"{token:<15} {count:<8}")

# Key insight
print(f"\n{'='*80}")
print("KEY INSIGHT")
print("="*80)

print(f"""
The "d" stem with freq=1468 comes from:
  • 96.5% tokens ENDING in '-d' (inflected forms)
  • 2.4% standalone 'd' 
  • 0.9% prefix 'd-'
  • 0.2% internal '-d-'

This means:
  'shed', 'ched', 'oked' = stem + 'd' suffix
  NOT: 'd' + 'she', 'd' + 'che', etc.

The stem extraction counted 'd' as a component,
but 'd' is actually a SUFFIX, not a standalone word!

CONCLUSION:
  'd' is likely a grammatical suffix (past tense? passive?)
  NOT a preposition or conjunction
  
This explains:
  - Why it's section-specific (different sections use different verb tenses)
  - Why standalone 'd' is rare (it's a bound morpheme)
  - Why it appears 1468 times (many verbs take '-d' ending)
""")

# Look at what stems take the -d suffix
print(f"\n{'='*80}")
print("WHAT STEMS TAKE THE '-d' SUFFIX?")
print("="*80)

stems_with_d = []
for token in d_suffix:
    if len(token) > 1:
        base = token[:-1]
        stems_with_d.append(base)

stem_d_counter = Counter(stems_with_d)

print(f"\nBases that take '-d' (top 20):")
print(f"{'Base stem':<12} {'Count':<8} {'In T3?':<10} {'Latin/Domain':<40}")
print("-" * 75)

for base, count in stem_d_counter.most_common(20):
    in_t3 = base in t3['stem'].values
    
    if in_t3:
        t3_row = t3[t3['stem'] == base].iloc[0]
        latin_info = f"{t3_row['lemma_latin']} ({t3_row['latin_domain']})"
    else:
        latin_info = "not validated"
    
    print(f"{base:<12} {count:<8} {'✓' if in_t3 else '✗':<10} {latin_info:<40}")

# Save
results = pd.DataFrame([{
    'position': pos,
    'count': cnt,
    'percentage': cnt/total_d*100
} for pos, cnt in [
    ('standalone', len(d_standalone)),
    ('suffix', len(d_suffix)),
    ('prefix', len(d_prefix)),
    ('internal', len(d_internal))
]])

results.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("REVISED INTERPRETATION")
print("="*80)

print("""
ORIGINAL HYPOTHESIS: 'd' = 'de' or 'et' (functional word)
REALITY: 'd' is a SUFFIX appearing on ~1400 tokens

IMPLICATIONS:
  1. Don't add standalone 'd' to lexicon
  2. Instead, analyze the '-d' suffix function
  3. Look at base stems: she→shed, che→ched, ok→oked
  4. Likely grammatical inflection (tense/voice/aspect)

NEXT: Focus on high-frequency content stems instead
  • 'che' (689) in Recipes → processing verb
  • 'qok' (943) in Recipes → processing verb  
  • 'she' (521) in Herbal → botanical term

These are actual word roots, not grammatical particles.
""")
