#!/usr/bin/env python3
import os
import csv

folio_tokens_file = os.path.expanduser("~/Voynich/ATTIC/PhaseS_dir/out/p6_folio_tokens.tsv")

print("=== CHECKING FILE FORMAT ===")
with open(folio_tokens_file, 'r') as f:
    # Read header
    header = f.readline().strip()
    print(f"Header: {header}")
    print(f"Columns: {header.split(chr(9))}")  # tab
    
    # Read first 5 data rows
    for i in range(5):
        line = f.readline()
        parts = line.split('\t')
        print(f"\nRow {i+1}: {len(parts)} columns")
        for j, part in enumerate(parts[:6]):
            print(f"  Col {j}: '{part[:50]}'")

