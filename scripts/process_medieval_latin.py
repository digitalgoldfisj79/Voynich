#!/usr/bin/env python3
"""
Process medieval Latin medical texts
"""

from pathlib import Path
import re

BASE = Path(__file__).parent.parent
OUT = BASE / "corpora/medieval_tokenized"

print("="*80)
print("PROCESSING MEDIEVAL LATIN MEDICAL CORPUS")
print("="*80)

# Find De Materia
materia_paths = [
    BASE / "corpora/latin_tokens_materia.txt",
    BASE / "corpora/medieval_sources/latin_tokens_materia.txt"
]

materia_text = ""
for path in materia_paths:
    if path.exists():
        materia_text = path.read_text(errors='ignore')
        print(f"\n✓ Found De Materia: {path}")
        print(f"  Size: {len(materia_text)} chars")
        break

if not materia_text:
    print("\n⚠️ De Materia not found, checking all files...")
    # Search
    import subprocess
    result = subprocess.run(['find', 'corpora', '-name', '*materia*'], 
                          capture_output=True, text=True)
    print(result.stdout)

# Load Macer Floridus
macer_file = BASE / "corpora/medieval_sources/macer_floridus_raw.txt"
if macer_file.exists():
    macer_text = macer_file.read_text(errors='ignore')
    
    # Clean
    if "START OF" in macer_text:
        macer_text = macer_text.split("START OF")[1]
    if "END OF" in macer_text:
        macer_text = macer_text.split("END OF")[0]
    
    macer_text = re.sub(r'\[.*?\]', ' ', macer_text)
    macer_text = re.sub(r'\d+', ' ', macer_text)
    
    print(f"\n✓ Macer Floridus: {len(macer_text)} chars")
else:
    macer_text = ""

# Combine
combined = materia_text + " " + macer_text
combined = combined.lower()
combined = re.sub(r'[^a-z\s]', ' ', combined)
combined = re.sub(r'\s+', ' ', combined).strip()

tokens = combined.split()

print(f"\nCombined medieval Latin medical:")
print(f"  Tokens: {len(tokens):,}")
print(f"  Unique: {len(set(tokens)):,}")

# Save
OUT.mkdir(exist_ok=True)
(OUT / "medieval_latin_medical.txt").write_text(' '.join(tokens))

print(f"\n✓ Saved to: medieval_tokenized/")
print(f"\nSample: {' '.join(tokens[:30])}")

