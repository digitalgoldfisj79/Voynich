#!/usr/bin/env python3
"""
Generate bigrams for "d" analysis
"""

import pandas as pd
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "Lexicon_Expansion/lex03b_d_bigrams.tsv"

print("="*80)
print("GENERATING BIGRAMS FOR 'd' ANALYSIS")
print("="*80)

# Load canonical token file
token_file = BASE / "corpora/p6_voynich_tokens.txt"

print(f"\nLoading tokens from: {token_file}")

with open(token_file, 'r') as f:
    tokens = f.read().split()

print(f"Loaded {len(tokens)} tokens")

# Generate bigrams with "d"
print("\nGenerating bigrams starting with 'd'...")

d_bigrams = Counter()

for i in range(len(tokens) - 1):
    if tokens[i] == 'd':
        bigram = f"{tokens[i]} {tokens[i+1]}"
        d_bigrams[bigram] += 1

print(f"Found {len(d_bigrams)} unique bigrams starting with 'd'")
print(f"Total 'd' bigrams: {sum(d_bigrams.values())}")

# Convert to dataframe
bigrams_df = pd.DataFrame([
    {'bigram': bigram, 'count': count, 'second_stem': bigram.split()[1]}
    for bigram, count in d_bigrams.items()
])

bigrams_df = bigrams_df.sort_values('count', ascending=False)

# Display top 30
print(f"\nTop 30 bigrams: 'd + X'")
print(f"{'Bigram':<20} {'Count':<8}")
print("-" * 30)

for _, row in bigrams_df.head(30).iterrows():
    print(f"{row['bigram']:<20} {row['count']:<8}")

# Save
bigrams_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

# Now analyze with T3 data
print(f"\n{'='*80}")
print("WHAT ARE THE STEMS AFTER 'd'?")
print("="*80)

t3 = pd.read_csv(BASE / "metadata/t3_candidates_domains_filtered.tsv", sep='\t')

followers_in_t3 = bigrams_df[bigrams_df['second_stem'].isin(t3['stem'])]

print(f"\nValidated T3 stems that follow 'd': {len(followers_in_t3)}/{len(bigrams_df)}")

if len(followers_in_t3) > 0:
    print(f"\n{'Bigram':<20} {'Count':<8} {'Latin':<15} {'Gloss':<20} {'Domain':<15}")
    print("-" * 90)
    
    for _, row in followers_in_t3.head(20).iterrows():
        t3_match = t3[t3['stem'] == row['second_stem']].iloc[0]
        print(f"{row['bigram']:<20} {row['count']:<8} {t3_match['lemma_latin']:<15} {t3_match['gloss_en']:<20} {t3_match['latin_domain']:<15}")
    
    # Analyze domains
    follower_matches = bigrams_df.merge(t3, left_on='second_stem', right_on='stem', how='inner')
    domain_counts = follower_matches.groupby('latin_domain')['count'].sum().sort_values(ascending=False)
    
    print(f"\n{'='*80}")
    print("DOMAIN ANALYSIS OF FOLLOWERS")
    print("="*80)
    
    print(f"\nDomains of stems following 'd' (weighted by frequency):")
    for domain, count in domain_counts.items():
        print(f"  {domain:<20}: {count} occurrences")
    
    # Are they nouns or verbs?
    noun_like = domain_counts[[d for d in domain_counts.index if 'BOT' in d or 'BIO' in d]].sum()
    verb_like = domain_counts[[d for d in domain_counts.index if 'PROC' in d]].sum()
    
    print(f"\nNoun-like (BOT/BIO): {noun_like} occurrences")
    print(f"Verb-like (PROC): {verb_like} occurrences")
    
    if noun_like > verb_like * 2:
        print(f"\n  → 'd' is followed mostly by NOUNS/BOTANICAL terms")
    elif verb_like > noun_like * 2:
        print(f"\n  → 'd' is followed mostly by VERBS/PROCESSING terms")
    else:
        print(f"\n  → 'd' is followed by MIXED types")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)

print("""
Given:
1. 'd' appears 90% in Herbal section (not uniform)
2. CV = 1.2 (highly section-specific)
3. Frequency = 4.93% (similar to Latin 'et' at 3.69%)

Possibilities:
A. 'd' is a botanical prefix/term dominant in Herbal
B. 'd' is herbal-specific article/determiner
C. 'd' is contracted form used more in botanical contexts

Next: Check if 'd' + botanical stems form patterns
""")

print("\nRun: python3 Lexicon_Expansion/lex03c_d_botanical_pattern.py")
