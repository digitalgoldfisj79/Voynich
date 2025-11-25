#!/usr/bin/env python3
"""Verification Script: Table 4 - Compression Model Performance"""
import sys, csv
from pathlib import Path

EXPECTED_MODELS = {
    'Model 1': {'length': 6.23, 'types': 32, 'entropy': 3.67},
    'Model 2': {'length': 5.47, 'types': 18, 'entropy': 3.12},
    'Model 3': {'length': 4.82, 'types': 12, 'entropy': 2.29},
    'Model 4': {'length': 5.11, 'types': 15, 'entropy': 2.87},
    'Model 5': {'length': 3.55, 'types': 7, 'entropy': 1.95},
    'Model 6': {'length': 3.21, 'types': 4, 'entropy': 1.23},
}

def verify():
    print("="*70)
    print("VERIFICATION: Table 4 - Compression Models")
    print("="*70)
    
    results_file = "results/tables/table4_compression_models.csv"
    if not Path(results_file).exists():
        print(f"✗ Results file not found: {results_file}")
        return False
    
    with open(results_file) as f:
        reader = csv.DictReader(f)
        actual = {row['model']: row for row in reader}
    
    all_pass = True
    for model, expected in EXPECTED_MODELS.items():
        if model not in actual:
            print(f"✗ Missing model: {model}")
            all_pass = False
            continue
        
        length_actual = float(actual[model]['token_length'])
        if abs(length_actual - expected['length']) < 0.1:
            print(f"✓ {model}: length={length_actual:.2f}")
        else:
            print(f"✗ {model}: length={length_actual:.2f} (expected {expected['length']})")
            all_pass = False
    
    print("="*70 + "\n")
    if all_pass:
        print("✓✓✓ Table 4 VERIFIED")
    else:
        print("✗✗✗ Table 4 VERIFICATION FAILED")
    return all_pass

if __name__ == "__main__":
    sys.exit(0 if verify() else 1)
