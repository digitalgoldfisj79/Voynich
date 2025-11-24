#!/usr/bin/env python3
"""
M10: Stem Stability Analysis

Analyzes which stems appear consistently across sections vs. which vary.
Stable stems with consistent behavior are better translation targets.

Input:  PhaseT/out/t03_enriched_translations.tsv
        PhaseM/out/m09_structural_content_classification.tsv
Output: PhaseM/out/m10_stem_stability.tsv

Methodology:
1. Calculate consistency metrics for each stem
2. Identify stable stems (appear in multiple sections consistently)
3. Measure morphological stability (same suffixes across sections?)
4. Rank stems by translation target suitability

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT_TOKENS = BASE / "PhaseT/out/t03_enriched_translations.tsv"
INPUT_CLASS = BASE / "PhaseM/out/m09_structural_content_classification.tsv"
OUTPUT = BASE / "PhaseM/out/m10_stem_stability.tsv"

print("="*80)
print("M10: STEM STABILITY ANALYSIS")
print("="*80)

# Load data
print(f"\nLoading data...")
df = pd.read_csv(INPUT_TOKENS, sep='\t')
df_class = pd.read_csv(INPUT_CLASS, sep='\t')

# Filter to tokens with section labels
df = df[df['section'].notna()].copy()

print(f"Analyzing {len(df)} tokens with section labels")

# For each stem, calculate stability metrics
print("\nCalculating stability metrics...")

stem_stability = {}

for stem in df['stem'].unique():
    if pd.isna(stem) or stem == 'nan':
        continue
    
    stem_data = df[df['stem'] == stem]
    
    # Basic stats
    total_count = len(stem_data)
    n_sections = stem_data['section'].nunique()
    
    # Section distribution variance (low = stable)
    section_counts = stem_data['section'].value_counts()
    if len(section_counts) > 1:
        section_variance = np.var(section_counts.values)
        section_std = np.std(section_counts.values)
    else:
        section_variance = 0
        section_std = 0
    
    # Morphological stability: do suffixes stay consistent?
    suffix_stability = 0
    if total_count > 5:  # Only for stems with enough data
        # Get suffix distributions per section
        section_suffix_dists = {}
        for section in stem_data['section'].unique():
            section_tokens = stem_data[stem_data['section'] == section]
            suffixes = []
            for _, row in section_tokens.iterrows():
                token = str(row['token'])
                if token.startswith(stem):
                    suffix = token[len(stem):]
                    if suffix == '':
                        suffix = 'NULL'
                    suffixes.append(suffix)
            
            if suffixes:
                from collections import Counter
                suffix_dist = Counter(suffixes)
                most_common = suffix_dist.most_common(1)[0][0]
                section_suffix_dists[section] = most_common
        
        # Are the most common suffixes the same across sections?
        if len(section_suffix_dists) > 1:
            suffix_values = list(section_suffix_dists.values())
            # Count how many sections share the most common suffix
            from collections import Counter
            suffix_counts = Counter(suffix_values)
            max_agreement = max(suffix_counts.values())
            suffix_stability = max_agreement / len(suffix_values)
    
    # Coefficient of variation (normalized measure)
    mean_per_section = total_count / n_sections if n_sections > 0 else 0
    cv = section_std / mean_per_section if mean_per_section > 0 else 0
    
    # Presence consistency: what fraction of sections contain this stem?
    max_sections = df['section'].nunique()
    presence_consistency = n_sections / max_sections
    
    stem_stability[stem] = {
        'total_count': total_count,
        'n_sections': n_sections,
        'presence_consistency': presence_consistency,
        'section_variance': section_variance,
        'coefficient_of_variation': cv,
        'morphological_stability': suffix_stability
    }

# Create results dataframe
results = []

for stem, metrics in stem_stability.items():
    # Get classification
    class_row = df_class[df_class['stem'] == stem]
    classification = class_row['classification'].values[0] if len(class_row) > 0 else 'UNKNOWN'
    
    # Calculate overall stability score
    # Higher is more stable
    stability_score = 0
    
    # Present in many sections
    if metrics['presence_consistency'] > 0.66:
        stability_score += 2
    elif metrics['presence_consistency'] > 0.33:
        stability_score += 1
    
    # Low coefficient of variation (consistent counts)
    if metrics['coefficient_of_variation'] < 0.5:
        stability_score += 2
    elif metrics['coefficient_of_variation'] < 1.0:
        stability_score += 1
    
    # Morphologically stable
    if metrics['morphological_stability'] > 0.7:
        stability_score += 2
    elif metrics['morphological_stability'] > 0.5:
        stability_score += 1
    
    # Sufficient frequency
    if metrics['total_count'] > 50:
        stability_score += 1
    
    results.append({
        'stem': stem,
        'total_count': metrics['total_count'],
        'n_sections': metrics['n_sections'],
        'presence_consistency': metrics['presence_consistency'],
        'coefficient_of_variation': metrics['coefficient_of_variation'],
        'morphological_stability': metrics['morphological_stability'],
        'stability_score': stability_score,
        'classification': classification
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('stability_score', ascending=False)

# Summary
print(f"\n{'='*80}")
print("STABILITY SUMMARY")
print("="*80)

print("\nStability score distribution:")
for score in sorted(results_df['stability_score'].unique(), reverse=True):
    count = len(results_df[results_df['stability_score'] == score])
    print(f"  Score {score}: {count} stems")

# Most stable stems
print(f"\n{'='*80}")
print("TOP 30 MOST STABLE STEMS")
print("="*80)
print("\nThese are the best candidates for semantic analysis:")
print("  - Appear consistently across sections")
print("  - Have stable morphology")
print("  - Sufficient frequency\n")

print(f"{'Stem':<10} {'Count':<8} {'Sections':<10} {'Presence%':<12} {'CV':<8} {'MorphStab':<12} {'Score':<8} {'Class':<12}")
print("-" * 95)

for _, row in results_df.head(30).iterrows():
    print(f"{row['stem']:<10} {row['total_count']:<8.0f} {row['n_sections']:<10.0f} "
          f"{row['presence_consistency']*100:<12.1f} {row['coefficient_of_variation']:<8.2f} "
          f"{row['morphological_stability']:<12.2f} {row['stability_score']:<8.0f} "
          f"{row['classification']:<12}")

# Best content word targets
print(f"\n{'='*80}")
print("BEST CONTENT WORD TARGETS (stable + content)")
print("="*80)

content_stable = results_df[
    (results_df['classification'] == 'CONTENT') & 
    (results_df['stability_score'] >= 3) &
    (results_df['total_count'] >= 10)
].head(20)

if len(content_stable) > 0:
    print(f"\n{'Stem':<10} {'Count':<8} {'Sections':<10} {'Score':<8}")
    print("-" * 40)
    for _, row in content_stable.iterrows():
        print(f"{row['stem']:<10} {row['total_count']:<8.0f} {row['n_sections']:<10.0f} {row['stability_score']:<8.0f}")
else:
    print("\n  No stable content words found with these criteria")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("PHASE 1B COMPLETE")
print("="*80)
print("\nStem analysis complete. You now have:")
print("  1. Complete stem inventory (4,021 stems)")
print("  2. Section-specific vocabularies")
print("  3. Stem-suffix combination rules")
print("  4. Structural vs. content classification")
print("  5. Stability analysis for translation targets")
