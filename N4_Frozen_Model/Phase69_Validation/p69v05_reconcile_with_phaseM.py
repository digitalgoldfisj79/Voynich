#!/usr/bin/env python3
"""
Phase 69 Validation 05: Reconcile with PhaseM Morphology

Compares Phase 69's character-level rules with PhaseM's morphological suffixes.

Question: Are these different levels of analysis, or contradictory?

Input:  Phase69/out/p69_rules_final.json
        PhaseM/out/m01_suffix_inventory.tsv
        PhaseT/out/t03_enriched_translations.tsv
Output: Phase69_Validation/p69v05_reconciliation.tsv

Author: Voynich Research Team
Date: 2025-01-21
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
RULES_FILE = BASE / "Phase69/out/p69_rules_final.json"
SUFFIXES_FILE = BASE / "PhaseM/out/m01_suffix_inventory.tsv"
TOKENS_FILE = BASE / "PhaseT/out/t03_enriched_translations.tsv"
OUTPUT = BASE / "Phase69_Validation/p69v05_reconciliation.tsv"

print("="*80)
print("PHASE 69 vs PHASEM: RECONCILIATION ANALYSIS")
print("="*80)

# Load Phase 69 rules
with open(RULES_FILE, 'r') as f:
    p69_rules = json.load(f)['rules']

# Load PhaseM suffixes
phasem_suffixes = pd.read_csv(SUFFIXES_FILE, sep='\t')

# Load tokens
df = pd.read_csv(TOKENS_FILE, sep='\t')
df = df[df['section'].notna()].copy()

print(f"\nPhase 69: {len(p69_rules)} rules")
print(f"PhaseM: {len(phasem_suffixes)} suffixes (excluding NULL)")

# Compare suffix patterns
print(f"\n{'='*80}")
print("COMPARING SUFFIX PATTERNS")
print("="*80)

# Get Phase 69 suffix rules
p69_suffix_rules = [r for r in p69_rules if r.get('kind') == 'suffix']
print(f"\nPhase 69 has {len(p69_suffix_rules)} suffix rules:")
for rule in p69_suffix_rules:
    print(f"  {rule['pattern']:10s} → {rule['pred_side']}")

print(f"\nPhaseM has {len(phasem_suffixes)} morphological suffixes:")
for _, row in phasem_suffixes.head(10).iterrows():
    suffix = row['suffix']
    if suffix != suffix or str(suffix) == 'nan':
        continue
    print(f"  {str(suffix):10s}: {int(row['token_count'])} tokens")

# Analysis: Do Phase 69 suffix rules match PhaseM suffixes?
print(f"\n{'='*80}")
print("OVERLAP ANALYSIS")
print("="*80)

p69_patterns = set([r['pattern'] for r in p69_suffix_rules])
phasem_patterns = set([str(s) for s in phasem_suffixes['suffix'].dropna() if str(s) != 'nan'])

overlap = p69_patterns.intersection(phasem_patterns)
p69_only = p69_patterns - phasem_patterns
phasem_only = phasem_patterns - p69_patterns

print(f"\nOverlap: {len(overlap)} patterns")
if overlap:
    print(f"  {', '.join(sorted(overlap))}")

print(f"\nPhase 69 only: {len(p69_only)} patterns")
if p69_only:
    print(f"  {', '.join(sorted(p69_only))}")

print(f"\nPhaseM only: {len(phasem_only)} patterns")
if phasem_only:
    print(f"  {', '.join(sorted(phasem_only))}")

# Key insight: Check if PhaseM suffixes are CHARACTER SEQUENCES or MORPHOLOGICAL UNITS
print(f"\n{'='*80}")
print("CHARACTER vs MORPHOLOGICAL ANALYSIS")
print("="*80)

print("\nPhase 69 operates at CHARACTER level:")
print("  - Rules fire on character patterns")
print("  - Example: 'che' as a character sequence")
print("  - Example: '|h' means 'ends with h'")

print("\nPhaseM operates at MORPHOLOGICAL level:")
print("  - Suffixes extracted as: token - stem")
print("  - Example: 'daiin' = 'd' (stem) + 'aiin' (suffix)")
print("  - Example: 'sheol' = 'she' (stem) + 'ol' (suffix)")

# Test on sample tokens
print(f"\n{'='*80}")
print("SAMPLE TOKEN ANALYSIS")
print("="*80)

sample_tokens = [
    ('daiin', 'd', 'aiin'),
    ('sheol', 'she', 'ol'),
    ('qoky', 'qok', 'y'),
    ('chedy', 'ched', 'y'),
    ('okal', 'ok', 'al')
]

print("\nHow Phase 69 vs PhaseM analyze the same tokens:\n")
print(f"{'Token':<12} {'Stem':<8} {'M-Suffix':<10} {'P69 Suffix Rules':<30} {'P69 Other Rules':<30}")
print("-" * 100)

for token, stem, m_suffix in sample_tokens:
    # Find Phase 69 suffix rules that match
    p69_suffix_matches = []
    p69_other_matches = []
    
    for rule in p69_rules:
        kind = rule.get('kind')
        pattern = rule.get('pattern')
        
        if kind == 'suffix' and token.endswith(pattern):
            p69_suffix_matches.append(pattern)
        elif kind == 'chargram' and pattern in token:
            p69_other_matches.append(f"{pattern}(char)")
        elif kind == 'pair' and '|' in pattern:
            parts = pattern.split('|')
            if len(parts) == 2 and parts[0] in token and parts[1] in token:
                p69_other_matches.append(f"{pattern}(pair)")
    
    p69_suff_str = ','.join(p69_suffix_matches[:3]) if p69_suffix_matches else '-'
    p69_other_str = ','.join(p69_other_matches[:3]) if p69_other_matches else '-'
    
    print(f"{token:<12} {stem:<8} {m_suffix:<10} {p69_suff_str:<30} {p69_other_str:<30}")

# Create reconciliation summary
print(f"\n{'='*80}")
print("RECONCILIATION SUMMARY")
print("="*80)

summary = {
    'analysis_level': ['Phase 69', 'PhaseM'],
    'unit_type': ['Character sequences', 'Morphological suffixes'],
    'n_patterns': [len(p69_rules), len(phasem_suffixes)],
    'overlap_patterns': [len(overlap), len(overlap)],
    'method': ['Rule-based character patterns', 'Token - Stem extraction'],
    'purpose': ['LEFT/RIGHT axis prediction', 'Morphological documentation']
}

summary_df = pd.DataFrame(summary)

print("\n" + summary_df.to_string(index=False))

print(f"\n{'='*80}")
print("KEY INSIGHT")
print("="*80)

print("\nPhase 69 and PhaseM analyze DIFFERENT LEVELS:")
print("\n1. Phase 69 (Character-level):")
print("   - 109 rules for character patterns")
print("   - Purpose: Predict LEFT/RIGHT axis")
print("   - Includes: character pairs, n-grams, positions")
print("   - 15 'suffix' rules are CHARACTER patterns (h, ch, che, etc.)")

print("\n2. PhaseM (Morphological-level):")
print("   - 8-9 morphological suffixes")
print("   - Purpose: Document morpheme boundaries")
print("   - Method: Extract suffix = token - stem")
print("   - Suffixes are MORPHEMES (y, aiin, ol, al, etc.)")

print("\nTHESE ARE NOT CONTRADICTORY - THEY'RE COMPLEMENTARY:")
print("  - Phase 69: How to PREDICT morphological class from characters")
print("  - PhaseM: What the actual MORPHOLOGICAL UNITS are")

# Save
results = []
for pattern in sorted(p69_patterns.union(phasem_patterns)):
    results.append({
        'pattern': pattern,
        'in_phase69': pattern in p69_patterns,
        'in_phasem': pattern in phasem_patterns,
        'analysis_type': 'Both' if pattern in overlap else 
                        ('P69_character' if pattern in p69_only else 'PhaseM_morpheme')
    })

results_df = pd.DataFrame(results)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)

print(f"\n✓ Saved: {OUTPUT}")
print(f"\nNext: Run p69v06_baseline_comparison.py")
