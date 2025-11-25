#!/usr/bin/env python3
"""Verification Script: Table 3 - Compression Examples"""
import sys, csv
from pathlib import Path

# Key examples from manuscript
EXPECTED_EXAMPLES = {
    'matenedors': {'compressed': 'mats', 'length_change': '10→4'},
    'esperitz': {'compressed': 'esprt', 'length_change': '8→5'},
    'necessarias': {'compressed': 'necsras', 'length_change': '11→7'},
}

def verify():
    print("="*70)
    print("VERIFICATION: Table 3 - Compression Examples")
    print("="*70)
    
    results_file = "results/tables/table3_compression_examples.csv"
    if not Path(results_file).exists():
        print(f"✗ Results file not found: {results_file}")
        return False
    
    with open(results_file) as f:
        reader = csv.DictReader(f)
        actual = {row['original']: row for row in reader}
    
    all_pass = True
    for original, expected in EXPECTED_EXAMPLES.items():
        if original not in actual:
            print(f"✗ Missing example: {original}")
            all_pass = False
            continue
        
        compressed_actual = actual[original]['compressed']
        if compressed_actual == expected['compressed']:
            print(f"✓ {original} → {compressed_actual}")
        else:
            print(f"✗ {original}: {compressed_actual} (expected {expected['compressed']})")
            all_pass = False
    
    print("="*70 + "\n")
    if all_pass:
        print("✓✓✓ Table 3 VERIFIED")
    else:
        print("✗✗✗ Table 3 VERIFICATION FAILED")
    return all_pass

if __name__ == "__main__":
    sys.exit(0 if verify() else 1)
