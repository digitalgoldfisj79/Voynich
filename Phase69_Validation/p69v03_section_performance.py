#!/usr/bin/env python3
"""
Phase 69 Validation 03: Section-Specific Performance

Tests how Phase 69 rules perform in different manuscript sections.

Input:  Phase69/out/p69_rules_final.json
        PhaseT/out/t03_enriched_translations.tsv
Output: Phase69_Validation/p69v03_section_performance.tsv

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
OUTPUT = BASE / "Phase69_Validation/p69v03_section_performance.tsv"

print("="*80)
print("PHASE 69 VALIDATION 03: SECTION-SPECIFIC PERFORMANCE")
print("="*80)

# Load rules
with open(RULES_FILE, 'r') as f:
    rules = json.load(f)['rules']

# Load tokens
df = pd.read_csv(TOKENS_FILE, sep='\t')
df = df[df['section'].notna()].copy()

print(f"Loaded {len(rules)} rules")
print(f"Loaded {len(df)} tokens")

# Apply rules by section
def apply_rule(token, rule, section):
    """Apply rule to token if section is allowed"""
    if section not in rule.get('allow', []):
        return None
    if section in rule.get('deny', []):
        return None
    
    kind = rule.get('kind')
    pattern = rule.get('pattern', '')
    pred_side = rule.get('pred_side')
    
    if kind == 'suffix' and token.endswith(pattern):
        return pred_side
    elif kind == 'prefix' and token.startswith(pattern):
        return pred_side
    elif kind == 'chargram' and pattern in token:
        return pred_side
    elif kind == 'pair' and '|' in pattern:
        parts = pattern.split('|')
        if len(parts) == 2:
            if parts[0] in token and parts[1] in token:
                idx0 = token.find(parts[0])
                idx1 = token.find(parts[1], idx0 + len(parts[0]))
                if idx1 > -1:
                    return pred_side
    
    return None

# Analyze by section
section_stats = defaultdict(lambda: {
    'total_tokens': 0,
    'tokens_with_matches': 0,
    'total_matches': 0,
    'left_predictions': 0,
    'right_predictions': 0,
    'rules_fired': set()
})

print("\nApplying rules by section...")

for section in df['section'].unique():
    section_tokens = df[df['section'] == section]
    section_stats[section]['total_tokens'] = len(section_tokens)
    
    for _, row in section_tokens.iterrows():
        token = str(row['token'])
        token_matches = 0
        
        for rule in rules:
            pred = apply_rule(token, rule, section)
            if pred:
                token_matches += 1
                section_stats[section]['total_matches'] += 1
                section_stats[section]['rules_fired'].add(rule.get('rule_id'))
                
                if pred == 'left':
                    section_stats[section]['left_predictions'] += 1
                elif pred == 'right':
                    section_stats[section]['right_predictions'] += 1
        
        if token_matches > 0:
            section_stats[section]['tokens_with_matches'] += 1

# Create results
results = []
for section, stats in section_stats.items():
    total = stats['total_tokens']
    coverage = stats['tokens_with_matches'] / total if total > 0 else 0
    avg_matches = stats['total_matches'] / total if total > 0 else 0
    
    left_pct = stats['left_predictions'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
    right_pct = stats['right_predictions'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
    
    results.append({
        'section': section,
        'total_tokens': total,
        'tokens_covered': stats['tokens_with_matches'],
        'coverage_pct': coverage * 100,
        'total_matches': stats['total_matches'],
        'avg_matches_per_token': avg_matches,
        'left_predictions': stats['left_predictions'],
        'right_predictions': stats['right_predictions'],
        'left_pct': left_pct * 100,
        'right_pct': right_pct * 100,
        'unique_rules_fired': len(stats['rules_fired'])
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('total_tokens', ascending=False)

# Display
print(f"\n{'='*80}")
print("SECTION PERFORMANCE")
print("="*80)

print(f"\n{'Section':<20} {'Tokens':<8} {'Coverage':<10} {'Avg Match':<10} {'Left%':<8} {'Right%':<8} {'Rules':<8}")
print("-" * 90)

for _, row in results_df.iterrows():
    print(f"{row['section']:<20} {row['total_tokens']:<8.0f} {row['coverage_pct']:<10.1f} "
          f"{row['avg_matches_per_token']:<10.2f} {row['left_pct']:<8.1f} {row['right_pct']:<8.1f} "
          f"{row['unique_rules_fired']:<8.0f}")

# Save
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

# Overall statistics
print(f"\n{'='*80}")
print("OVERALL STATISTICS")
print("="*80)

total_tokens = results_df['total_tokens'].sum()
total_covered = results_df['tokens_covered'].sum()
total_matches = results_df['total_matches'].sum()
total_left = results_df['left_predictions'].sum()
total_right = results_df['right_predictions'].sum()

print(f"\nTotal tokens: {total_tokens}")
print(f"Tokens covered: {total_covered} ({total_covered/total_tokens*100:.1f}%)")
print(f"Total rule matches: {total_matches}")
print(f"Average matches per token: {total_matches/total_tokens:.2f}")
print(f"\nPrediction distribution:")
print(f"  LEFT:  {total_left} ({total_left/total_matches*100:.1f}%)")
print(f"  RIGHT: {total_right} ({total_right/total_matches*100:.1f}%)")

print(f"\n{'='*80}")
print("KEY OBSERVATIONS")
print("="*80)

# Find sections with most skew
most_left = results_df.nlargest(1, 'left_pct').iloc[0]
most_right = results_df.nlargest(1, 'right_pct').iloc[0]

print(f"\nMost LEFT-skewed:  {most_left['section']} ({most_left['left_pct']:.1f}% left)")
print(f"Most RIGHT-skewed: {most_right['section']} ({most_right['right_pct']:.1f}% right)")

print(f"\nNext: Compare to baseline/random predictions")
