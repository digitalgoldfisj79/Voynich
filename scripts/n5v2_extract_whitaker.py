#!/usr/bin/env python3
"""
Extract lemmas from Whitaker's DICTLINE.GEN
This is the main dictionary database
"""

from pathlib import Path
import re

BASE = Path(__file__).parent.parent
DICTLINE = BASE / "corpora/latin_raw/whitaker/DICTLINE.GEN"
OUTPUT = BASE / "corpora/latin_vocab/whitaker_lemmas.tsv"

print("="*80)
print("EXTRACTING WHITAKER'S DICTIONARY")
print("="*80)

if not DICTLINE.exists():
    print(f"ERROR: {DICTLINE} not found")
    exit(1)

print(f"\nReading: {DICTLINE}")
print(f"Size: {DICTLINE.stat().st_size / 1024 / 1024:.1f} MB")

# Parse DICTLINE.GEN format
# Each line is a dictionary entry
lemmas = {}

with open(DICTLINE, 'r', encoding='latin-1', errors='ignore') as f:
    for line_num, line in enumerate(f, 1):
        # Whitaker format is complex, but lemmas typically appear at start
        # Format varies: "word  PART  DECL...  [meaning]"
        
        # Try to extract word at start of line (before whitespace/brackets)
        parts = line.strip().split()
        if not parts:
            continue
        
        # First token is usually the lemma
        word = parts[0].lower()
        
        # Filter: only lowercase letters, 2-20 chars
        if not re.match(r'^[a-z]{2,20}$', word):
            continue
        
        # Try to get part of speech (second field often)
        pos = parts[1] if len(parts) > 1 else "?"
        
        # Extract meaning in brackets
        meaning_match = re.search(r'\[(.*?)\]', line)
        meaning = meaning_match.group(1) if meaning_match else ""
        
        if word in lemmas:
            lemmas[word]['freq'] += 1
        else:
            lemmas[word] = {
                'pos': pos,
                'meaning': meaning[:50],  # Truncate long definitions
                'freq': 1
            }
        
        if (line_num % 10000 == 0):
            print(f"  Processed {line_num} lines, {len(lemmas)} unique lemmas...")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, 'w') as f:
    f.write("lemma\tpos\tmeaning\tfreq_estimate\tsource\n")
    for lemma, data in sorted(lemmas.items()):
        f.write(f"{lemma}\t{data['pos']}\t{data['meaning']}\t{data['freq']}\twhitaker\n")

print(f"\n✓ Extracted {len(lemmas)} unique Latin lemmas")
print(f"✓ Saved: {OUTPUT}")

# Show sample
print(f"\nSample entries:")
for i, (lemma, data) in enumerate(sorted(lemmas.items())[:20]):
    print(f"  {lemma:<15} {data['pos']:<5} {data['meaning'][:30]}")

print(f"\nMost common patterns (freq > 5):")
common = sorted([(l, d['freq']) for l, d in lemmas.items() if d['freq'] > 5], 
                key=lambda x: x[1], reverse=True)[:20]
for lemma, freq in common:
    print(f"  {lemma:<15} {freq}")

