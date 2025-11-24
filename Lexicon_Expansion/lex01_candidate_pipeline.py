#!/usr/bin/env python3
"""
Lexicon Expansion Pipeline

Uses VALIDATED methodology to systematically expand T3 lexicon.

Strategy:
1. Start with high-frequency stems (not yet in T3)
2. Find Latin matches using SAME criteria that worked
3. Validate against domain-section patterns
4. Iteratively expand lexicon

Goal: 332 → 500 → 1000 validated mappings
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
OUTPUT_DIR = BASE / "Lexicon_Expansion"

print("="*80)
print("LEXICON EXPANSION PIPELINE")
print("="*80)

# Load existing validated data
t3_validated = pd.read_csv(BASE / "metadata/t3_candidates_domains_filtered.tsv", sep='\t')
voynich_stems = pd.read_csv(BASE / "metadata/t03_stem_frequencies.tsv", sep='\t')
latin_corpus = pd.read_csv(BASE / "PhaseS/out/s6_materia_token_freq.tsv", sep='\t')
section_dist = pd.read_csv(BASE / "PhaseS/out/s4_stem_section_distribution.tsv", sep='\t')

print(f"\nCurrent state:")
print(f"  Validated T3: {len(t3_validated)} stems")
print(f"  Total Voynich stems: {len(voynich_stems)}")
print(f"  Latin corpus: {len(latin_corpus)} tokens")

# Identify unexplored stems
section_dist = section_dist.rename(columns={'token': 'stem'})
explored_stems = set(t3_validated['stem'].values)
all_stems = set(voynich_stems['stem'].values)
unexplored = all_stems - explored_stems

print(f"  Unexplored stems: {len(unexplored)}")

# Merge frequency data for unexplored stems
unexplored_df = voynich_stems[voynich_stems['stem'].isin(unexplored)].copy()
unexplored_df = unexplored_df.merge(section_dist, on='stem', how='left')

# Calculate priority score
def priority_score(row):
    """
    Priority = frequency * section_clarity
    High frequency + appears predominantly in one section = high priority
    """
    freq = row['stem_freq']
    
    # Section clarity: how concentrated is it?
    section_cols = [c for c in row.index if c.startswith('count_')]
    section_counts = [row[c] for c in section_cols if pd.notna(row[c])]
    
    if len(section_counts) == 0 or sum(section_counts) == 0:
        clarity = 0
    else:
        max_section = max(section_counts)
        total = sum(section_counts)
        clarity = max_section / total  # Concentration ratio
    
    return freq * clarity

unexplored_df['priority'] = unexplored_df.apply(priority_score, axis=1)
unexplored_df = unexplored_df.sort_values('priority', ascending=False)

print(f"\n{'='*80}")
print("TOP 50 EXPANSION CANDIDATES")
print("="*80)

print(f"\n{'Stem':<12} {'Freq':<6} {'Priority':<10} {'Dominant Section':<20}")
print("-" * 60)

top_candidates = []

for _, row in unexplored_df.head(50).iterrows():
    stem = row['stem']
    freq = row['stem_freq']
    priority = row['priority']
    
    # Find dominant section
    section_cols = [c for c in row.index if c.startswith('count_')]
    sections = {c.replace('count_', ''): row[c] for c in section_cols if pd.notna(row[c])}
    
    if sections:
        dominant = max(sections.items(), key=lambda x: x[1])
        dom_section = dominant[0]
        dom_count = dominant[1]
    else:
        dom_section = "Unknown"
        dom_count = 0
    
    print(f"{stem:<12} {freq:<6} {priority:<10.2f} {dom_section:<20}")
    
    top_candidates.append({
        'stem': stem,
        'frequency': freq,
        'priority': priority,
        'dominant_section': dom_section,
        'dominant_count': dom_count
    })

# Save candidates
candidates_df = pd.DataFrame(top_candidates)
candidates_file = OUTPUT_DIR / "lex01_expansion_candidates.tsv"
candidates_df.to_csv(candidates_file, sep='\t', index=False)

print(f"\n✓ Saved top 50 candidates: {candidates_file}")

# Strategy by section
print(f"\n{'='*80}")
print("EXPANSION STRATEGY BY SECTION")
print("="*80)

print("\nBased on validated patterns:")
print("  • Herbal stems → Look for botanical Latin (BOT_*)")
print("  • Recipes stems → Look for processing Latin (PROC_*)")
print("  • Biological stems → Look for body/fluid Latin (BIO_*)")

for section in ['Herbal', 'Recipes', 'Biological', 'Pharmaceutical']:
    section_candidates = [c for c in top_candidates if c['dominant_section'] == section]
    print(f"\n{section}: {len(section_candidates)} high-priority candidates")
    
    if len(section_candidates) > 0:
        print(f"  Top 3: {', '.join([c['stem'] for c in section_candidates[:3]])}")

print(f"\n{'='*80}")
print("NEXT STEPS")
print("="*80)

print("""
1. For each candidate stem, run matching algorithm:
   - Find Latin lemmas with similar form
   - Check Latin corpus frequency
   - Assign domain based on Latin semantics
   
2. Validate new assignments:
   - Does domain match section? (should follow existing pattern)
   - Does it increase or decrease χ²?
   - Is assignment consistent with neighboring stems?

3. Iterative expansion:
   - Add 50 candidates
   - Re-run validation tests
   - If χ² stays high, continue
   - If χ² drops, re-examine assignments

4. Target milestones:
   - 500 stems (50% more)
   - 750 stems (125% more)
   - 1000 stems (200% more)
""")

print("\nReady to start expansion!")
print("\nRun: python3 Lexicon_Expansion/lex02_batch_matcher.py")
