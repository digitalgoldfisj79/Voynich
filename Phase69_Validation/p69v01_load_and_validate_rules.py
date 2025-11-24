#!/usr/bin/env python3
"""
Phase 69 Validation 01: Load and Validate Rule System

Loads the Phase 69 rulebook and performs basic validation on the 109-rule system.

Input:  Phase69/out/p69_rules_final.json
Output: Phase69_Validation/p69v01_rule_inventory.tsv
        Phase69_Validation/p69v01_rule_summary.txt

Author: Voynich Research Team
Date: 2025-01-21
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent

# Correct path to Phase69 output
RULES_FILE = BASE / "Phase69/out/p69_rules_final.json"
OUTPUT_INV = BASE / "Phase69_Validation/p69v01_rule_inventory.tsv"
OUTPUT_SUMMARY = BASE / "Phase69_Validation/p69v01_rule_summary.txt"

print("="*80)
print("PHASE 69 VALIDATION 01: RULE SYSTEM INVENTORY")
print("="*80)

# Load rules
print(f"\nLoading rules from: {RULES_FILE}")
with open(RULES_FILE, 'r') as f:
    data = json.load(f)

rules = data.get('rules', [])
print(f"Loaded {len(rules)} rules")

# Analyze rule structure
rule_types = Counter([r.get('kind', 'unknown') for r in rules])

print(f"\n{'='*80}")
print("RULE TYPE DISTRIBUTION")
print("="*80)

for rule_type, count in rule_types.most_common():
    print(f"{rule_type:15s}: {count:3d} rules ({count/len(rules)*100:5.2f}%)")

# Analyze by prediction side
print(f"\n{'='*80}")
print("PREDICTION DIRECTION")
print("="*80)

pred_sides = Counter([r.get('pred_side', 'unknown') for r in rules])
for side, count in pred_sides.most_common():
    print(f"{side:15s}: {count:3d} rules ({count/len(rules)*100:5.2f}%)")

# Analyze patterns
print(f"\n{'='*80}")
print("RULE PATTERNS BY TYPE")
print("="*80)

for rule_type in sorted(rule_types.keys()):
    type_rules = [r for r in rules if r.get('kind') == rule_type]
    patterns = [r.get('pattern', '') for r in type_rules]
    unique_patterns = len(set(patterns))
    
    print(f"\n{rule_type.upper()}:")
    print(f"  Total rules: {len(type_rules)}")
    print(f"  Unique patterns: {unique_patterns}")
    print(f"  Example patterns: {', '.join(sorted(set(patterns))[:10])}")

# Analyze base weights
print(f"\n{'='*80}")
print("BASE WEIGHT DISTRIBUTION")
print("="*80)

weights = [r.get('base_weight', 0) for r in rules]
print(f"Mean weight: {sum(weights)/len(weights):.2f}")
print(f"Min weight: {min(weights):.2f}")
print(f"Max weight: {max(weights):.2f}")
print(f"Median weight: {sorted(weights)[len(weights)//2]:.2f}")

# Analyze section allowances
print(f"\n{'='*80}")
print("SECTION COVERAGE")
print("="*80)

all_sections = set()
for r in rules:
    all_sections.update(r.get('allow', []))

print(f"Sections covered: {', '.join(sorted(all_sections))}")

for section in sorted(all_sections):
    rules_for_section = [r for r in rules if section in r.get('allow', [])]
    print(f"{section:20s}: {len(rules_for_section):3d} rules ({len(rules_for_section)/len(rules)*100:5.2f}%)")

# Create detailed inventory
inventory = []
for r in rules:
    inventory.append({
        'rule_id': r.get('rule_id', ''),
        'kind': r.get('kind', ''),
        'pattern': r.get('pattern', ''),
        'pred_side': r.get('pred_side', ''),
        'base_weight': r.get('base_weight', 0),
        'n_allow': len(r.get('allow', [])),
        'n_deny': len(r.get('deny', [])),
        'sections': ','.join(r.get('allow', []))
    })

inventory_df = pd.DataFrame(inventory)

# Save inventory
OUTPUT_INV.parent.mkdir(parents=True, exist_ok=True)
inventory_df.to_csv(OUTPUT_INV, sep='\t', index=False)
print(f"\n✓ Saved rule inventory: {OUTPUT_INV}")

# Create summary report
with open(OUTPUT_SUMMARY, 'w') as f:
    f.write("="*80 + "\n")
    f.write("PHASE 69 MORPHOLOGICAL RULE SYSTEM\n")
    f.write("Validation Report 01: Rule Inventory\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"Total Rules: {len(rules)}\n\n")
    
    f.write("Rule Types:\n")
    for rule_type, count in rule_types.most_common():
        f.write(f"  {rule_type:15s}: {count:3d} rules\n")
    
    f.write("\nPrediction Directions:\n")
    for side, count in pred_sides.most_common():
        f.write(f"  {side:15s}: {count:3d} rules\n")
    
    f.write("\nSection Coverage:\n")
    for section in sorted(all_sections):
        rules_for_section = [r for r in rules if section in r.get('allow', [])]
        f.write(f"  {section:20s}: {len(rules_for_section):3d} rules\n")

print(f"✓ Saved summary: {OUTPUT_SUMMARY}")

print(f"\n{'='*80}")
print("NEXT STEPS")
print("="*80)
print("\n1. Validate rule predictions against actual tokens")
print("2. Test LEFT/RIGHT axis accuracy")
print("3. Section-specific performance analysis")
print("4. Statistical significance testing")

print(f"\nRun: python3 Phase69_Validation/p69v02_test_predictions.py")
