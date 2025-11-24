#!/usr/bin/env python3
"""
Extract medieval Occitan from MHT dictionary file
"""

from pathlib import Path
import re

BASE = Path(__file__).parent.parent
MHT = BASE / "corpora/medieval_sources/Lexic_occitan_medieval.mht"

print("="*80)
print("EXTRACTING MEDIEVAL OCCITAN DICTIONARY")
print("="*80)

if not MHT.exists():
    print(f"\n❌ File not found: {MHT}")
    print("\nSearching for it...")
    import subprocess
    result = subprocess.run(['find', '/storage/emulated/0', '-name', '*occitan*'], 
                          capture_output=True, text=True, timeout=10)
    print(result.stdout)
    exit(1)

# Read MHT (MIME HTML archive)
text = MHT.read_text(encoding='utf-8', errors='ignore')
print(f"\nFile size: {len(text):,} chars")

# Extract words (Occitan uses Romance alphabet)
words = set()

# Look for dictionary entries (usually marked up)
lines = text.split('\n')
for line in lines:
    # Remove HTML/XML tags
    clean = re.sub(r'<[^>]+>', ' ', line)
    clean = re.sub(r'&[^;]+;', ' ', clean)
    
    # Extract Occitan words (2-15 chars, Romance alphabet)
    tokens = re.findall(r'\b[a-zàâäçèéêëìîïòôöùûü]{2,15}\b', clean.lower())
    words.update(tokens)

words = sorted(list(words))

print(f"\nExtracted {len(words):,} unique words")
print(f"\nSample: {words[:50]}")

# Save
out_file = BASE / "corpora/medieval_sources/occitan_medieval_dict.txt"
out_file.write_text(' '.join(words))

print(f"\n✓ Saved: {out_file}")

