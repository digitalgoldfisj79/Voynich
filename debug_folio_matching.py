#!/usr/bin/env python3
import os

folio_tokens_file = os.path.expanduser("~/Voynich/ATTIC/PhaseS_dir/out/p6_folio_tokens.tsv")
folio_currier_file = os.path.expanduser("~/Voynich/ATTIC/PhaseS_dir/tmp/s49b_folio_hand_currier_section.tsv")

# Get sample folios from each file
print("=== FOLIO IDENTIFIERS IN p6_folio_tokens.tsv ===")
with open(folio_tokens_file, 'r') as f:
    next(f)  # skip header
    folios_in_tokens = set()
    for i, line in enumerate(f):
        if i >= 100:
            break
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            folios_in_tokens.add(parts[1])
    
print(f"Sample folios (first 100 tokens): {sorted(folios_in_tokens)[:20]}")

print("\n=== FOLIO IDENTIFIERS IN s49b_folio_hand_currier_section.tsv ===")
with open(folio_currier_file, 'r') as f:
    folios_in_currier = set()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 1:
            folios_in_currier.add(parts[0])

print(f"All folios: {sorted(folios_in_currier)[:20]}")

print("\n=== CHECKING IF THEY OVERLAP ===")
# Try different cleaning methods
tokens_cleaned = {f.rstrip('>').rstrip('<') for f in folios_in_tokens}
currier_cleaned = {f.rstrip('>').rstrip('<') for f in folios_in_currier}

overlap = tokens_cleaned & currier_cleaned
print(f"After cleaning > and <:")
print(f"  Overlap: {len(overlap)} folios match")
print(f"  Sample matches: {sorted(overlap)[:10]}")

if not overlap:
    print("\n⚠️ NO OVERLAP! Folio identifiers use different formats.")
    print("\nFrom tokens file:", sorted(tokens_cleaned)[:10])
    print("From Currier file:", sorted(currier_cleaned)[:10])

