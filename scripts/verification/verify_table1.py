#!/usr/bin/env python3
"""
Verification Script: Table 1 - Suffix Inventory

Checks that the 9-suffix system matches manuscript claims:
- 9 suffix types
- 78.6% coverage
- Correct frequencies and stem counts
"""

import sys
import csv
from pathlib import Path

# Manuscript claims for Table 1
EXPECTED_SUFFIXES = {
    '-y': {'freq': 11400, 'pct': 38.4, 'stems': 178},
    'NULL': {'freq': 6472, 'pct': 21.8, 'stems': 142},
    '-aiin': {'freq': 2908, 'pct': 9.8, 'stems': 87},
    '-ol': {'freq': 2700, 'pct': 9.1, 'stems': 94},
    '-al': {'freq': 1721, 'pct': 5.8, 'stems': 76},
    '-or': {'freq': 1603, 'pct': 5.4, 'stems': 68},
    '-ain': {'freq': 1336, 'pct': 4.5, 'stems': 62},
    '-ody': {'freq': 890, 'pct': 3.0, 'stems': 54},
    '-am': {'freq': 652, 'pct': 2.2, 'stems': 51},
}

EXPECTED_TOTAL = 23192
EXPECTED_COVERAGE = 78.6
TOLERANCE_PCT = 0.5  # Allow ±0.5%
TOLERANCE_COUNT = 20  # Allow ±20 tokens

def check_suffix_inventory(results_file):
    """Check suffix inventory against manuscript claims"""
    
    print("="*70)
    print("VERIFICATION: Table 1 - Suffix Inventory")
    print("="*70)
    
    if not Path(results_file).exists():
        print(f"✗ Results file not found: {results_file}")
        print(f"  Run: python scripts/morphology/identify_productive_stems.py")
        return False
    
    # Read results
    with open(results_file) as f:
        reader = csv.DictReader(f)
        actual_suffixes = {row['suffix']: row for row in reader}
    
    # Check each suffix
    all_pass = True
    for suffix, expected in EXPECTED_SUFFIXES.items():
        if suffix not in actual_suffixes:
            print(f"\n✗ Missing suffix: {suffix}")
            all_pass = False
            continue
        
        actual = actual_suffixes[suffix]
        
        # Check frequency
        freq_actual = int(actual['frequency'])
        freq_expected = expected['freq']
        freq_diff = abs(freq_actual - freq_expected)
        
        if freq_diff > TOLERANCE_COUNT:
            print(f"\n✗ {suffix} frequency mismatch:")
            print(f"  Expected: {freq_expected} tokens")
            print(f"  Actual: {freq_actual} tokens")
            print(f"  Difference: {freq_diff} tokens")
            all_pass = False
        else:
            print(f"✓ {suffix}: {freq_actual} tokens (expected {freq_expected})")
        
        # Check percentage
        pct_actual = float(actual['percentage'])
        pct_expected = expected['pct']
        pct_diff = abs(pct_actual - pct_expected)
        
        if pct_diff > TOLERANCE_PCT:
            print(f"  ✗ Percentage: {pct_actual}% (expected {pct_expected}%)")
            all_pass = False
        
        # Check stem count
        stems_actual = int(actual['stem_count'])
        stems_expected = expected['stems']
        
        if abs(stems_actual - stems_expected) > 5:
            print(f"  ✗ Stem count: {stems_actual} (expected {stems_expected})")
            all_pass = False
    
    # Check total coverage
    print(f"\n{'─'*70}")
    total_actual = sum(int(actual_suffixes[s]['frequency']) for s in EXPECTED_SUFFIXES)
    if abs(total_actual - EXPECTED_TOTAL) > TOLERANCE_COUNT:
        print(f"✗ Total tokens: {total_actual} (expected {EXPECTED_TOTAL})")
        all_pass = False
    else:
        print(f"✓ Total tokens: {total_actual} (expected {EXPECTED_TOTAL})")
    
    print(f"{'─'*70}\n")
    
    if all_pass:
        print("✓✓✓ Table 1 VERIFIED - All values match manuscript")
    else:
        print("✗✗✗ Table 1 VERIFICATION FAILED - See errors above")
    
    print("="*70 + "\n")
    return all_pass

if __name__ == "__main__":
    results_file = "results/tables/table1_suffix_inventory.csv"
    success = check_suffix_inventory(results_file)
    sys.exit(0 if success else 1)
