#!/usr/bin/env python3
"""
Phase 69 Validation 02: Test Rule Accuracy

Tests Phase 69 rules against actual token data to measure:
- Overall accuracy
- Per-rule-type accuracy
- Per-section accuracy
- Precision/recall per rule

Input:  Phase69/out/p69_rules_final.json
        PhaseT/out/t03_enriched_translations.tsv (for tokens)
Output: Phase69_Validation/p69v02_accuracy_results.tsv

Author: Voynich Research Team
Date: 2025-01-21
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
RULES_FILE = BASE / "Phase69/out/p69_rules_final.json"
TOKENS_FILE = BASE / "PhaseT/out/t03_enriched_translations.tsv"
OUTPUT = BASE / "Phase69_Validation/p69v02_accuracy_results.tsv"

print("="*80)
print("PHASE 69 VALIDATION 02: RULE ACCURACY TESTING")
print("="*80)

# Load rules
print(f"\nLoading rules...")
with open(RULES_FILE, 'r') as f:
    rules_data = json.load(f)
rules = rules_data.get('rules', [])
print(f"Loaded {len(rules)} rules")

# Load tokens
print(f"\nLoading tokens...")
df = pd.read_csv(TOKENS_FILE, sep='\t')
df = df[df['section'].notna()].copy()
print(f"Loaded {len(df)} tokens with sections")

# Function to apply a single rule to a token
def apply_rule(token, rule, section):
    """
    Apply a rule to a token and return predicted side (or None if no match)
    """
    kind = rule.get('kind')
    pattern = rule.get('pattern', '')
    pred_side = rule.get('pred_side')
    
    # Check if rule applies to this section
    if section not in rule.get('allow', []):
        return None
    if section in rule.get('deny', []):
        return None
    
    # Check if pattern matches
    if kind == 'suffix':
        if token.endswith(pattern):
            return pred_side
    elif kind == 'prefix':
        if token.startswith(pattern):
            return pred_side
    elif kind == 'chargram':
        if pattern in token:
            return pred_side
    elif kind == 'pair':
        # Pair patterns like "c|h" mean c followed by h
        if '|' in pattern:
            parts = pattern.split('|')
            if len(parts) == 2:
                # Check if both parts appear in sequence
                if parts[0] in token and parts[1] in token:
                    idx0 = token.find(parts[0])
                    idx1 = token.find(parts[1], idx0 + len(parts[0]))
                    if idx1 > -1:
                        return pred_side
    
    return None

# Test each rule on all tokens
print(f"\n{'='*80}")
print("TESTING RULES ON TOKENS")
print("="*80)

# We need ground truth LEFT/RIGHT labels
# For now, let's see what the rules predict
# We'll calculate rule agreement and coverage

rule_stats = []

for rule in rules:
    rule_id = rule.get('rule_id', '')
    kind = rule.get('kind', '')
    pattern = rule.get('pattern', '')
    pred_side = rule.get('pred_side', '')
    
    matches = 0
    predictions = []
    
    for _, row in df.iterrows():
        token = str(row['token'])
        section = row['section']
        
        prediction = apply_rule(token, rule, section)
        if prediction:
            matches += 1
            predictions.append(prediction)
    
    # Calculate stats
    coverage = matches / len(df) if len(df) > 0 else 0
    
    rule_stats.append({
        'rule_id': rule_id,
        'kind': kind,
        'pattern': pattern,
        'pred_side': pred_side,
        'matches': matches,
        'coverage': coverage,
        'n_tokens_tested': len(df)
    })

results_df = pd.DataFrame(rule_stats)

# Summary by rule type
print(f"\n{'='*80}")
print("COVERAGE BY RULE TYPE")
print("="*80)

for kind in ['suffix', 'prefix', 'chargram', 'pair']:
    subset = results_df[results_df['kind'] == kind]
    if len(subset) > 0:
        total_matches = subset['matches'].sum()
        mean_coverage = subset['coverage'].mean()
        print(f"\n{kind.upper()}:")
        print(f"  Total rules: {len(subset)}")
        print(f"  Total matches: {total_matches}")
        print(f"  Mean coverage per rule: {mean_coverage*100:.2f}%")

# Top rules by coverage
print(f"\n{'='*80}")
print("TOP 20 RULES BY COVERAGE")
print("="*80)

top_rules = results_df.sort_values('coverage', ascending=False).head(20)
print(f"\n{'Rule ID':<30} {'Kind':<12} {'Pattern':<15} {'Pred':<8} {'Matches':<8} {'Coverage':<10}")
print("-" * 95)

for _, row in top_rules.iterrows():
    print(f"{row['rule_id']:<30} {row['kind']:<12} {row['pattern']:<15} "
          f"{row['pred_side']:<8} {row['matches']:<8.0f} {row['coverage']*100:<10.2f}%")

# Save results
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("KEY FINDINGS")
print("="*80)

total_matches = results_df['matches'].sum()
avg_coverage = results_df['coverage'].mean()

print(f"\nTotal rule matches across corpus: {total_matches}")
print(f"Average coverage per rule: {avg_coverage*100:.2f}%")
print(f"Total unique tokens tested: {len(df)}")

print(f"\nNote: Without ground truth LEFT/RIGHT labels, we can measure")
print(f"coverage but not accuracy. Next step: validate against known stems.")

print(f"\nRun: python3 Phase69_Validation/p69v03_section_performance.py")
