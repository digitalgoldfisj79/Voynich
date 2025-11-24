#!/usr/bin/env python3
"""
Deep Analysis: "d" stem

Hypothesis: d = "de" (of/from) or "et" (and)

Tests:
1. Positional analysis (does it appear before nouns like "de"?)
2. Frequency by section (is it uniform like a preposition?)
3. Context patterns (what stems appear after "d"?)
4. Validation against known T3 stems
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "Lexicon_Expansion/lex03_d_analysis.tsv"

print("="*80)
print("DEEP ANALYSIS: 'd' STEM")
print("="*80)

# Load data
section_dist = pd.read_csv(BASE / "PhaseS/out/s4_stem_section_distribution.tsv", sep='\t')
section_dist = section_dist.rename(columns={'token': 'stem'})
t3_validated = pd.read_csv(BASE / "metadata/t3_candidates_domains_filtered.tsv", sep='\t')

# Get "d" distribution
d_row = section_dist[section_dist['stem'] == 'd'].iloc[0]

print("\n" + "="*80)
print("TEST 1: SECTION DISTRIBUTION")
print("="*80)

print("\nHypothesis: If 'd' is functional (de/et), it should appear")
print("uniformly across all sections (like a preposition/conjunction).\n")

sections = ['Herbal', 'Biological', 'Recipes', 'Pharmaceutical', 'Astronomical']
d_counts = {s: d_row[f'count_{s}'] for s in sections}
d_total = sum(d_counts.values())

print(f"'d' distribution across sections:")
print(f"{'Section':<20} {'Count':<8} {'%':<8} {'Expected %':<12}")
print("-" * 55)

# Expected: proportional to section size
section_sizes = section_dist[[f'count_{s}' for s in sections]].sum()
total_tokens = section_sizes.sum()

for section in sections:
    count = d_counts[section]
    pct = (count / d_total) * 100 if d_total > 0 else 0
    expected_pct = (section_sizes[f'count_{section}'] / total_tokens) * 100
    diff = pct - expected_pct
    
    print(f"{section:<20} {count:<8} {pct:<8.1f} {expected_pct:<8.1f} ({diff:+.1f})")

# Calculate uniformity (coefficient of variation)
proportions = [d_counts[s]/d_total for s in sections if d_counts[s] > 0]
cv = np.std(proportions) / np.mean(proportions) if len(proportions) > 0 else 0

print(f"\nCoefficient of variation: {cv:.3f}")
print(f"  < 0.3: Uniform (functional)")
print(f"  > 0.5: Section-specific (content)")

test1_result = "FUNCTIONAL" if cv < 0.3 else "CONTENT-SPECIFIC"
print(f"\nResult: {test1_result}")

# TEST 2: Bigram analysis
print("\n" + "="*80)
print("TEST 2: WHAT FOLLOWS 'd'?")
print("="*80)

print("\nHypothesis: If 'd' = 'de' (of/from), stems after 'd' should be")
print("nouns/adjectives (like in Latin 'de + ablative')\n")

# Load bigram data if available
bigram_file = BASE / "PhaseM/out/m04_bigrams.tsv"

if bigram_file.exists():
    bigrams = pd.read_csv(bigram_file, sep='\t')
    
    # Find bigrams starting with 'd'
    d_bigrams = bigrams[bigrams['bigram'].str.startswith('d ')].copy()
    d_bigrams['second_stem'] = d_bigrams['bigram'].str.split().str[1]
    
    if len(d_bigrams) > 0:
        top_followers = d_bigrams.nlargest(20, 'count')
        
        print("Top 20 bigrams: 'd + X'")
        print(f"{'Bigram':<20} {'Count':<8} {'Second stem in T3?':<20}")
        print("-" * 50)
        
        for _, row in top_followers.iterrows():
            bigram = row['bigram']
            count = row['count']
            second = row['second_stem']
            
            in_t3 = "✓ " + t3_validated[t3_validated['stem'] == second]['lemma_latin'].iloc[0] if second in t3_validated['stem'].values else "✗ not validated"
            
            print(f"{bigram:<20} {count:<8} {in_t3:<20}")
        
        # Check if second stems are in T3
        followers_in_t3 = [s for s in d_bigrams['second_stem'] if s in t3_validated['stem'].values]
        
        print(f"\nStems following 'd' that are in validated T3: {len(followers_in_t3)}/{len(d_bigrams)}")
        
        if len(followers_in_t3) > 0:
            # Get their domains
            follower_domains = t3_validated[t3_validated['stem'].isin(followers_in_t3)]['latin_domain'].value_counts()
            
            print(f"\nDomains of validated stems following 'd':")
            for domain, count in follower_domains.items():
                print(f"  {domain}: {count}")
            
            # Are they mostly nouns (BOT_HERB)?
            noun_like = sum(count for domain, count in follower_domains.items() if 'BOT' in domain or 'BIO' in domain)
            verb_like = sum(count for domain, count in follower_domains.items() if 'PROC' in domain)
            
            print(f"\nNoun-like (BOT/BIO): {noun_like}")
            print(f"Verb-like (PROC): {verb_like}")
            
            if noun_like > verb_like:
                print(f"\n  ✓ Followers are mostly NOUNS (consistent with 'de + noun')")
                test2_result = "PREPOSITION"
            else:
                print(f"\n  ? Mixed followers (may be conjunction 'et')")
                test2_result = "CONJUNCTION"
        else:
            test2_result = "UNKNOWN"
    else:
        print("No bigrams starting with 'd' found")
        test2_result = "UNKNOWN"
else:
    print("Bigram data not available")
    print("Recommendation: Generate bigrams with PhaseM tools")
    test2_result = "UNKNOWN"

# TEST 3: Compare with Latin "de" and "et"
print("\n" + "="*80)
print("TEST 3: FREQUENCY COMPARISON")
print("="*80)

# Load Latin corpus
latin_corpus = pd.read_csv(BASE / "PhaseS/out/s6_materia_token_freq.tsv", sep='\t')

de_latin = latin_corpus[latin_corpus['token'] == 'de']
et_latin = latin_corpus[latin_corpus['token'] == 'et']

if len(de_latin) > 0:
    de_count = de_latin.iloc[0]['total_count']
    de_pct = (de_count / latin_corpus['total_count'].sum()) * 100
    print(f"\nLatin 'de': {de_count} occurrences ({de_pct:.2f}%)")

if len(et_latin) > 0:
    et_count = et_latin.iloc[0]['total_count']
    et_pct = (et_count / latin_corpus['total_count'].sum()) * 100
    print(f"Latin 'et': {et_count} occurrences ({et_pct:.2f}%)")

# Voynich 'd'
voynich_stems = pd.read_csv(BASE / "metadata/t03_stem_frequencies.tsv", sep='\t')
d_voynich = voynich_stems[voynich_stems['stem'] == 'd'].iloc[0]
d_voynich_count = d_voynich['stem_freq']
d_voynich_pct = (d_voynich_count / voynich_stems['stem_freq'].sum()) * 100

print(f"Voynich 'd': {d_voynich_count} occurrences ({d_voynich_pct:.2f}%)")

print(f"\nComparison:")
if len(et_latin) > 0:
    print(f"  Voynich 'd' ({d_voynich_pct:.2f}%) vs Latin 'et' ({et_pct:.2f}%): {abs(d_voynich_pct - et_pct):.2f}% difference")
if len(de_latin) > 0:
    print(f"  Voynich 'd' ({d_voynich_pct:.2f}%) vs Latin 'de' ({de_pct:.2f}%): {abs(d_voynich_pct - de_pct):.2f}% difference")

# VERDICT
print("\n" + "="*80)
print("VERDICT: 'd' STEM ANALYSIS")
print("="*80)

print(f"\nTest 1 (Distribution): {test1_result}")
print(f"Test 2 (Followers): {test2_result}")

print(f"\nMOST LIKELY INTERPRETATION:")

if test1_result == "FUNCTIONAL" and test2_result == "PREPOSITION":
    verdict = "d = de (of/from)"
    confidence = "HIGH"
elif test1_result == "FUNCTIONAL" and test2_result == "CONJUNCTION":
    verdict = "d = et (and)"
    confidence = "MEDIUM"
elif test1_result == "FUNCTIONAL":
    verdict = "d = de OR et (functional)"
    confidence = "MEDIUM"
else:
    verdict = "d = unknown"
    confidence = "LOW"

print(f"  {verdict}")
print(f"  Confidence: {confidence}")

# Save
results = pd.DataFrame([{
    'stem': 'd',
    'frequency': d_voynich_count,
    'distribution_cv': cv,
    'test1_result': test1_result,
    'test2_result': test2_result,
    'verdict': verdict,
    'confidence': confidence
}])

results.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("NEXT STEPS")
print("="*80)

if confidence == "HIGH":
    print("\n✓ Strong evidence for interpretation")
    print("  → Add 'd' to expanded lexicon")
    print("  → Test predictions with 'd + validated_stems'")
    print("  → Look for phrases like 'd aiin' = 'de [botanical]'")
elif confidence == "MEDIUM":
    print("\n? Suggestive but not conclusive")
    print("  → Need context analysis")
    print("  → Generate bigrams if not available")
    print("  → Look at 'd' in actual folio sequences")
else:
    print("\n✗ Insufficient evidence")
    print("  → More data needed")

print("\nRun: python3 Lexicon_Expansion/lex04_batch_validate.py")
print("     (To test 50-stem expansion with 'd' included)")
