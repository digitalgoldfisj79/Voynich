#!/usr/bin/env python3
"""
Generate Rugg Basic Controls - Grid-based synthetic Voynich

Gordon Rugg's table/grid method:
1. Create columns of common Voynich morphemes/patterns
2. Create rows of constraints/rules
3. Generate tokens by randomly selecting from grid
4. Results in long, repetitive tokens (mean ~25 chars)

This simulates the "hoax hypothesis" where Voynich was created
mechanically using tables/grilles rather than encoding real language.
"""

import random
from pathlib import Path
from collections import Counter

# Set random seed for reproducibility
random.seed(42)

# Voynich-like morphemes (from actual Voynich patterns) - EXPANDED for more variety
PREFIXES = ['o', 'd', 'q', 'ok', 'qo', 'or', 'ol', 'ot', 'op', 'yk', 'dy', 'y', 'sh', 'ch', 'ke', 'te', 'lk', 'k', 's', 't', 'f', 'p', 'r', 'l', 'da', 'de', 'do', 'ky', 'ty', 'ko', 'to', 'so']
MIDDLES = ['che', 'she', 'qok', 'chol', 'shol', 'chor', 'shor', 'ar', 'or', 'al', 'ol', 'ain', 'aiin', 'iir', 'iin', 'dy', 'ty', 'ky', 'da', 'de', 'do', 'ko', 'to', 'so', 'ra', 're', 'ro', 'la', 'le', 'lo', 'ke', 'te', 'ka', 'ta', 'sa']
ENDINGS = ['dy', 'y', 'edy', 'ol', 'al', 'or', 'ar', 'in', 'ain', 'aiin', 'eedy', 'edy', 'am', 'iin', 'iir', 'te', 'to', 'sh', 'om', 'em', 'im', 'um', 'an', 'en', 'on', 'od', 'ad', 'ed', 'id']

def generate_rugg_basic_token():
    """
    Generate a token using Rugg's grid method.
    Randomly concatenate morphemes to create long tokens.
    """
    # Rugg method tends to create VERY LONG tokens (20-30 chars)
    # by stringing together MANY morphemes
    
    token_parts = []
    
    # Start with optional prefix
    if random.random() < 0.7:
        token_parts.append(random.choice(PREFIXES))
    
    # Add 7-10 middle morphemes (creates very long tokens with variety)
    n_middles = random.randint(7, 10)
    for _ in range(n_middles):
        token_parts.append(random.choice(MIDDLES))
    
    # Add ending
    if random.random() < 0.9:
        token_parts.append(random.choice(ENDINGS))
    
    token = ''.join(token_parts)
    
    # Ensure minimum length (Rugg tokens are VERY LONG)
    # Target: 20-30 chars to match real data
    while len(token) < 20:
        token += random.choice(MIDDLES)
    
    return token

def generate_rugg_basic_corpus(n_tokens=10000, output_file='rugg_basic.tsv'):
    """Generate complete Rugg basic corpus"""
    
    print("="*80)
    print("GENERATING RUGG BASIC CONTROLS (Grid-based method)")
    print("="*80)
    print()
    print(f"Target: {n_tokens:,} tokens")
    print(f"Method: Random grid selection (Rugg hoax hypothesis)")
    print(f"Expected: Long tokens (mean ~25 chars)")
    print()
    
    tokens = []
    folio = 1
    line = 1
    pos = 1
    
    for i in range(n_tokens):
        token = generate_rugg_basic_token()
        tokens.append({
            'folio': f'f{folio}',
            'line': line,
            'pos': pos,
            'token': token
        })
        
        # Advance position
        pos += 1
        if pos > 20:  # ~20 tokens per line
            pos = 1
            line += 1
            if line > 30:  # ~30 lines per folio
                line = 1
                folio += 1
        
        if (i+1) % 1000 == 0:
            print(f"  Generated {i+1:,} tokens...")
    
    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write('folio\tline\tpos\ttoken\n')
        for t in tokens:
            f.write(f"{t['folio']}\t{t['line']}\t{t['pos']}\t{t['token']}\n")
    
    # Calculate statistics
    lengths = [len(t['token']) for t in tokens]
    chars_total = sum(lengths)
    len_mean = chars_total / len(lengths)
    len_median = sorted(lengths)[len(lengths)//2]
    len_stdev = (sum((x - len_mean)**2 for x in lengths) / len(lengths)) ** 0.5
    
    print()
    print("="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Tokens generated: {len(tokens):,}")
    print(f"Total characters: {chars_total:,}")
    print(f"Mean token length: {len_mean:.2f} chars")
    print(f"Median token length: {len_median:.0f} chars")
    print(f"Stdev token length: {len_stdev:.2f} chars")
    print()
    print(f"✓ Saved: {output_path}")
    print()
    print("INTERPRETATION:")
    print("  • Rugg basic tokens are VERY LONG (mean ~25 chars)")
    print("  • Real Voynich tokens are much shorter (mean ~5 chars)")
    print("  • This discriminates mechanical hoax from real text")
    
    return tokens

if __name__ == '__main__':
    generate_rugg_basic_corpus(
        n_tokens=10000,
        output_file='results/hoax/rugg_basic.tsv'
    )
