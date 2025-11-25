#!/usr/bin/env python3
"""
Verification Script: Table 2 - Stem Paradigms

Checks that high-frequency stems match manuscript claims
"""
import sys, csv
from pathlib import Path

EXPECTED_STEMS = {
    'qok-': {'total': 156, 'variants': 8},
    'shed-': {'total': 143, 'variants': 7},
    'chd-': {'total': 127, 'variants': 9},
    'dar-': {'total': 118, 'variants': 7},
    'che-': {'total': 112, 'variants': 8},
}

def verify():
    print("="*70)
    print("VERIFICATION: Table 2 - Stem Paradigms")
    print("="*70)
    
    results_file = "results/tables/table2_stem_paradigms.csv"
    if not Path(results_file).exists():
        print(f"✗ Results file not found: {results_file}")
        return False
    
    with open(results_file) as f:
        reader = csv.DictReader(f)
        actual = {row['stem']: row for row in reader}
    
    all_pass = True
    for stem, expected in EXPECTED_STEMS.items():
        if stem not in actual:
            print(f"✗ Missing stem: {stem}")
            all_pass = False
            continue
        
        total_actual = int(actual[stem]['total_occurrences'])
        variants_actual = int(actual[stem]['suffix_variants'])
        
        if abs(total_actual - expected['total']) > 5:
            print(f"✗ {stem}: {total_actual} occurrences (expected {expected['total']})")
            all_pass = False
        elif variants_actual != expected['variants']:
            print(f"✗ {stem}: {variants_actual} variants (expected {expected['variants']})")
            all_pass = False
        else:
            print(f"✓ {stem}: {total_actual} occurrences, {variants_actual} variants")
    
    print("="*70 + "\n")
    if all_pass:
        print("✓✓✓ Table 2 VERIFIED")
    else:
        print("✗✗✗ Table 2 VERIFICATION FAILED")
    return all_pass

if __name__ == "__main__":
    sys.exit(0 if verify() else 1)
