#!/usr/bin/env python3
"""Verification Script: Table 5 - Hoax Discriminants"""
import sys, csv
from pathlib import Path

EXPECTED_CONTROLS = {
    'Basic Grille': {'MI1': 1.24, 'FSM_violations': 7.6, 'morph_coverage': 0},
    'Enhanced Grille': {'MI1': 1.38, 'FSM_violations': 6.8, 'morph_coverage': 7},
    'Rule-Augmented': {'MI1': 1.43, 'FSM_violations': 5.4, 'morph_coverage': 21},
}

VOYNICHESE_TARGET = {'MI1': 1.69, 'FSM_violations': 6.2, 'morph_coverage': 78.6}

def verify():
    print("="*70)
    print("VERIFICATION: Table 5 - Hoax Discriminants")
    print("="*70)
    
    results_file = "results/tables/table5_hoax_discriminants.csv"
    if not Path(results_file).exists():
        print(f"✗ Results file not found: {results_file}")
        return False
    
    with open(results_file) as f:
        reader = csv.DictReader(f)
        actual = {row['control_type']: row for row in reader}
    
    all_pass = True
    
    # Check Voynichese target
    if 'Voynichese' in actual:
        mi1 = float(actual['Voynichese']['MI1'])
        if abs(mi1 - VOYNICHESE_TARGET['MI1']) < 0.05:
            print(f"✓ Voynichese: MI₁={mi1:.2f}")
        else:
            print(f"✗ Voynichese: MI₁={mi1:.2f} (expected {VOYNICHESE_TARGET['MI1']})")
            all_pass = False
    
    # Check controls
    for control, expected in EXPECTED_CONTROLS.items():
        if control not in actual:
            print(f"✗ Missing control: {control}")
            all_pass = False
            continue
        
        mi1_actual = float(actual[control]['MI1'])
        morph_actual = float(actual[control]['morphological_coverage'])
        
        if abs(mi1_actual - expected['MI1']) < 0.05:
            print(f"✓ {control}: MI₁={mi1_actual:.2f}, morph={morph_actual}%")
        else:
            print(f"✗ {control}: MI₁={mi1_actual:.2f} (expected {expected['MI1']})")
            all_pass = False
    
    print("="*70 + "\n")
    if all_pass:
        print("✓✓✓ Table 5 VERIFIED")
    else:
        print("✗✗✗ Table 5 VERIFICATION FAILED")
    return all_pass

if __name__ == "__main__":
    sys.exit(0 if verify() else 1)
