#!/usr/bin/env python3
"""
FINAL TEST: Does compression reduce Latin suffix diversity to Voynich levels?

Key hypothesis: Compression should MERGE Latin's 32 suffix types → ~9 types
"""

import re
from collections import Counter
import numpy as np

print("="*80)
print("FINAL COMPRESSION TEST")
print("="*80)

# The 9 Voynich suffix types
VOYNICH_SUFFIXES = ['y', 'aiin', 'ain', 'ol', 'al', 'or', 'ody', 'am', 'NULL']

def get_suffix_stats(tokens, name, extract_voynich_style=False):
    """Calculate suffix statistics for a corpus"""
    suffix_counts = Counter()
    
    for token in tokens:
        if extract_voynich_style:
            # Try to match Voynich suffixes
            matched = False
            for suf in ['aiin', 'ain', 'ody', 'ol', 'al', 'or', 'am', 'y']:
                if token.endswith(suf):
                    suffix_counts[suf] += 1
                    matched = True
                    break
            if not matched:
                suffix_counts['NULL'] += 1
        else:
            # Extract actual Latin suffixes
            if len(token) >= 3 and token[-3:] in ['bus', 'rum', 'ris', 'mus']:
                suffix_counts[token[-3:]] += 1
            elif len(token) >= 2 and token[-2:] in ['am', 'um', 'em', 'us', 'is', 'ae', 'or', 'as', 'os']:
                suffix_counts[token[-2:]] += 1
            elif len(token) >= 1 and token[-1] in 'aeiou':
                suffix_counts[token[-1]] += 1
            else:
                suffix_counts['NULL'] += 1
    
    # Calculate stats
    total = sum(suffix_counts.values())
    props = {k: v/total for k, v in suffix_counts.items()}
    
    # Entropy
    probs = np.array([p for p in props.values() if p > 0])
    entropy = -np.sum(probs * np.log2(probs))
    
    n_types = len(suffix_counts)
    mean_len = sum(len(t) for t in tokens) / len(tokens)
    
    return {
        'name': name,
        'n_tokens': len(tokens),
        'n_types': n_types,
        'mean_len': mean_len,
        'entropy': entropy,
        'suffix_counts': suffix_counts,
        'suffix_props': props
    }

# Load all corpora
print("\n1. Loading corpora...")

# Voynich
with open('p6_voynich_tokens.txt', 'r') as f:
    voynich_tokens = [line.strip() for line in f if line.strip()]

# Expanded Latin
with open('corpora/latin_abbrev_expanded.txt', 'r') as f:
    expanded_tokens = re.findall(r'\b[a-z]+\b', f.read().lower())

# Smart Compressed Latin
with open('corpora/latin_smart_compressed.txt', 'r') as f:
    compressed_tokens = [line.strip() for line in f if line.strip()]

print(f"   Voynich: {len(voynich_tokens):,} tokens")
print(f"   Expanded Latin: {len(expanded_tokens):,} tokens")
print(f"   Compressed Latin: {len(compressed_tokens):,} tokens")

# Analyze all three
print("\n2. Analyzing suffix distributions...")

voy_stats = get_suffix_stats(voynich_tokens, "VOYNICH", extract_voynich_style=True)
exp_stats = get_suffix_stats(expanded_tokens, "LATIN (FULL)")
comp_stats = get_suffix_stats(compressed_tokens, "LATIN (COMPRESSED)")

# Display results
print("\n" + "="*80)
print("RESULTS")
print("="*80)

for stats in [voy_stats, exp_stats, comp_stats]:
    print(f"\n{stats['name']}:")
    print(f"  Tokens: {stats['n_tokens']:,}")
    print(f"  Mean length: {stats['mean_len']:.2f} chars")
    print(f"  Suffix types: {stats['n_types']}")
    print(f"  Entropy: {stats['entropy']:.3f} bits")
    print(f"  Top 5 suffixes:")
    for suffix, count in stats['suffix_counts'].most_common(5):
        print(f"    {suffix:4s}: {stats['suffix_props'][suffix]*100:5.1f}%")

print("\n" + "="*80)
print("KEY COMPARISONS")
print("="*80)

print("\n1. SUFFIX TYPE COUNT (target: ~9 like Voynich):")
print(f"   Voynich:    {voy_stats['n_types']} types")
print(f"   Full Latin: {exp_stats['n_types']} types ({exp_stats['n_types']/voy_stats['n_types']:.1f}× more)")
print(f"   Compressed: {comp_stats['n_types']} types ({comp_stats['n_types']/voy_stats['n_types']:.1f}× more)")

reduction = ((exp_stats['n_types'] - comp_stats['n_types']) / exp_stats['n_types']) * 100
print(f"   → Compression reduced types by {reduction:.1f}%")

if comp_stats['n_types'] <= voy_stats['n_types'] + 3:
    print("   ✓ Compressed Latin approaches Voynich type count!")
else:
    print(f"   ⚠️ Still {comp_stats['n_types'] - voy_stats['n_types']} types too many")

print("\n2. ENTROPY (target: ~2.5 bits like Voynich):")
print(f"   Voynich:    {voy_stats['entropy']:.3f} bits")
print(f"   Full Latin: {exp_stats['entropy']:.3f} bits")
print(f"   Compressed: {comp_stats['entropy']:.3f} bits")

entropy_improvement = abs(exp_stats['entropy'] - voy_stats['entropy']) - abs(comp_stats['entropy'] - voy_stats['entropy'])
print(f"   → Compression moved {entropy_improvement:.3f} bits closer to Voynich")

if abs(comp_stats['entropy'] - voy_stats['entropy']) < 1.0:
    print("   ✓ Entropy approaching Voynich range!")
else:
    print(f"   ⚠️ Still {abs(comp_stats['entropy'] - voy_stats['entropy']):.3f} bits off")

print("\n3. TOKEN LENGTH (target: ~5 chars like Voynich):")
print(f"   Voynich:    {voy_stats['mean_len']:.2f} chars")
print(f"   Full Latin: {exp_stats['mean_len']:.2f} chars")
print(f"   Compressed: {comp_stats['mean_len']:.2f} chars")

if abs(comp_stats['mean_len'] - voy_stats['mean_len']) < 0.5:
    print("   ✓ Length MATCHES!")

print("\n" + "="*80)
print("FINAL VERDICT")
print("="*80)

# Score the hypothesis
scores = []
if abs(comp_stats['mean_len'] - voy_stats['mean_len']) < 1.0:
    scores.append("Length matches")
if comp_stats['n_types'] <= voy_stats['n_types'] + 5:
    scores.append("Type count close")
if abs(comp_stats['entropy'] - voy_stats['entropy']) < abs(exp_stats['entropy'] - voy_stats['entropy']):
    scores.append("Entropy improved")

print(f"\nHypothesis support: {len(scores)}/3 criteria met")
for s in scores:
    print(f"  ✓ {s}")

if len(scores) >= 2:
    print("\n✓ HYPOTHESIS SUPPORTED:")
    print("  Compression moves Latin closer to Voynichese statistics")
    print("  (even if perfect match not achieved)")
else:
    print("\n⚠️ HYPOTHESIS WEAK:")
    print("  Compression helps but major differences remain")

