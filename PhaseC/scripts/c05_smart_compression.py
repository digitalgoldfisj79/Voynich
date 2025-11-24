#!/usr/bin/env python3
"""
Smart Compression: Remove internal letters but PRESERVE suffix structure

Goal: Create abbreviated Latin that looks like Voynichese
- Target length: ~5 chars
- Preserve inflectional endings
- Maintain morphological diversity
"""

import re
from collections import Counter

print("="*80)
print("SMART COMPRESSION ALGORITHM")
print("="*80)

def smart_compress(word):
    """
    Compression rules:
    1. Keep first consonant cluster
    2. Remove most internal vowels/consonants  
    3. PRESERVE last 1-2 characters (the suffix!)
    4. Target: reduce by ~30-40% while keeping endings
    """
    if len(word) <= 3:
        return word
    
    # Identify the suffix (last 1-2 chars if vowel/common ending)
    if len(word) >= 2 and word[-2:] in ['am', 'um', 'em', 'is', 'us', 'as', 'os', 'ae', 'or']:
        suffix_len = 2
    elif word[-1] in 'aeiouy':
        suffix_len = 1
    else:
        suffix_len = 0
    
    if len(word) <= suffix_len + 2:
        return word
    
    # Split into: start + middle + suffix
    suffix = word[-suffix_len:] if suffix_len > 0 else ''
    middle_end = len(word) - suffix_len
    
    # Keep first 1-2 consonants
    start = ''
    i = 0
    while i < min(2, middle_end) and i < len(word):
        if word[i] not in 'aeiouy':
            start += word[i]
            i += 1
        else:
            break
    
    # Compress middle: remove most vowels, keep some consonants
    middle = word[len(start):middle_end]
    compressed_middle = ''
    
    # Keep ~50% of consonants, remove most vowels
    for i, c in enumerate(middle):
        if c not in 'aeiouy':
            # Keep every other consonant roughly
            if i % 2 == 0 or len(compressed_middle) < 2:
                compressed_middle += c
        elif len(compressed_middle) == 0 or i == 0:
            # Keep one vowel if nothing yet
            compressed_middle += c
    
    result = start + compressed_middle + suffix
    
    # Ensure minimum length of 3
    if len(result) < 3:
        return word
    
    return result

# Test on expanded Latin
print("\n1. Loading expanded Latin corpus...")
with open('corpora/latin_abbrev_expanded.txt', 'r') as f:
    expanded_text = f.read().lower()

# Extract words
expanded_tokens = re.findall(r'\b[a-z]+\b', expanded_text)
print(f"   {len(expanded_tokens):,} tokens")

# Apply smart compression
print("\n2. Applying smart compression...")
compressed_tokens = [smart_compress(token) for token in expanded_tokens]

# Calculate statistics
print("\n3. Comparing results...")

def analyze_corpus(tokens, name):
    # Token length
    lengths = [len(t) for t in tokens]
    mean_len = sum(lengths) / len(lengths)
    
    # Suffix extraction (same as Voynich)
    voynich_suffixes = ['aiin', 'ain', 'ody', 'ol', 'al', 'or', 'am', 'y']
    suffix_counts = Counter()
    
    for token in tokens:
        matched = False
        for suf in voynich_suffixes:
            if token.endswith(suf):
                suffix_counts[suf] += 1
                matched = True
                break
        
        if not matched:
            suffix_counts['NULL'] += 1
    
    total = sum(suffix_counts.values())
    suffix_props = {k: v/total for k, v in suffix_counts.items()}
    
    # Entropy
    import numpy as np
    probs = np.array([p for p in suffix_props.values() if p > 0])
    entropy = -np.sum(probs * np.log2(probs))
    
    print(f"\n{name}:")
    print(f"  Mean length: {mean_len:.2f} chars")
    print(f"  Entropy: {entropy:.3f} bits")
    print(f"  Suffix distribution:")
    for suf in ['y', 'am', 'or', 'ol', 'al', 'NULL']:
        if suf in suffix_props:
            print(f"    {suf:4s}: {suffix_props[suf]*100:5.1f}%")
    
    return mean_len, entropy, suffix_props

# Analyze all three
print("\n" + "="*80)
print("COMPARISON")
print("="*80)

# Voynich (reference)
print("\nVOYNICH (reference from Phase M):")
print("  Mean length: 5.09 chars")
print("  Entropy: 2.488 bits")
print("  y=38.7%, NULL=26.6%, aiin=8.5%")

# Expanded Latin
exp_len, exp_ent, exp_suf = analyze_corpus(expanded_tokens, "EXPANDED LATIN")

# Smart compressed
comp_len, comp_ent, comp_suf = analyze_corpus(compressed_tokens, "SMART COMPRESSED LATIN")

# Save compressed version
with open('corpora/latin_smart_compressed.txt', 'w') as f:
    f.write('\n'.join(compressed_tokens))

print("\n" + "="*80)
print("RESULTS")
print("="*80)

# Check if smart compression matches Voynich
length_match = abs(comp_len - 5.09) < 1.0
entropy_match = abs(comp_ent - 2.488) < 0.5

print(f"\nToken length: {comp_len:.2f} vs Voynich 5.09")
print(f"  {'✓ MATCH' if length_match else '⚠️ Different'}")

print(f"\nEntropy: {comp_ent:.3f} vs Voynich 2.488")
print(f"  {'✓ MATCH' if entropy_match else '⚠️ Different'}")

if length_match and entropy_match:
    print("\n✓✓✓ SUCCESS! Smart compression produces Voynichese-like statistics!")
else:
    print("\n⚠️ Partial match - may need further tuning")

# Show examples
print("\n" + "="*80)
print("EXAMPLE COMPRESSIONS")
print("="*80)
examples = [
    'medicina', 'herba', 'aqua', 'temperamentum', 
    'sanguinem', 'cholera', 'phlegma', 'melancholia'
]
for word in examples:
    if word in expanded_tokens:
        idx = expanded_tokens.index(word)
        compressed = compressed_tokens[idx]
        print(f"  {word:15s} → {compressed:8s} ({len(word)} → {len(compressed)} chars)")

