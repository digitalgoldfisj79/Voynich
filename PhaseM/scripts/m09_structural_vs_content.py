#!/usr/bin/env python3
"""
M09: Structural vs. Content Word Classification

Classifies stems as likely structural (function words) vs. content words
based on frequency, distribution, and morphological behavior.

Input:  PhaseT/out/t03_enriched_translations.tsv
        PhaseM/out/m06_stem_inventory.tsv
        PhaseM/out/m07_stem_by_section.tsv
Output: PhaseM/out/m09_structural_content_classification.tsv

Methodology:
1. High frequency + even distribution → structural
2. Lower frequency + section-specific → content
3. Morphological flexibility → consider behavior
4. Statistical classification using multiple features

Author: Voynich Research Team
Date: 2025-01-21
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE = Path(__file__).parent.parent.parent
INPUT_TOKENS = BASE / "PhaseT/out/t03_enriched_translations.tsv"
INPUT_INVENTORY = BASE / "PhaseM/out/m06_stem_inventory.tsv"
INPUT_SECTIONS = BASE / "PhaseM/out/m07_stem_by_section.tsv"
OUTPUT = BASE / "PhaseM/out/m09_structural_content_classification.tsv"

print("="*80)
print("M09: STRUCTURAL VS. CONTENT WORD CLASSIFICATION")
print("="*80)

# Load data
print(f"\nLoading data...")
df_tokens = pd.read_csv(INPUT_TOKENS, sep='\t')
df_inventory = pd.read_csv(INPUT_INVENTORY, sep='\t')
df_sections = pd.read_csv(INPUT_SECTIONS, sep='\t')

# Filter tokens with section labels
df_with_section = df_tokens[df_tokens['section'].notna()].copy()

# Calculate distribution metrics for each stem
print("\nCalculating distribution metrics...")

stem_metrics = {}

for stem in df_inventory['stem']:
    # Get all occurrences
    stem_tokens = df_with_section[df_with_section['stem'] == stem]
    
    if len(stem_tokens) == 0:
        continue
    
    # Frequency
    frequency = len(stem_tokens)
    
    # Section distribution
    section_counts = stem_tokens['section'].value_counts()
    n_sections = len(section_counts)
    
    # Calculate entropy (measure of even distribution)
    if n_sections > 0:
        proportions = section_counts / section_counts.sum()
        entropy = -np.sum(proportions * np.log2(proportions + 1e-10))
        max_entropy = np.log2(n_sections) if n_sections > 1 else 0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    else:
        normalized_entropy = 0
    
    # Max section proportion (how concentrated?)
    max_section_prop = section_counts.max() / section_counts.sum() if len(section_counts) > 0 else 0
    
    stem_metrics[stem] = {
        'frequency': frequency,
        'n_sections': n_sections,
        'normalized_entropy': normalized_entropy,
        'max_section_proportion': max_section_prop
    }

# Classification heuristics
print("\nClassifying stems...")

results = []

for stem, metrics in stem_metrics.items():
    freq = metrics['frequency']
    entropy = metrics['normalized_entropy']
    max_prop = metrics['max_section_proportion']
    n_sec = metrics['n_sections']
    
    # Classification logic
    score = 0
    reasons = []
    
    # High frequency suggests structural
    if freq > 100:
        score += 2
        reasons.append('high_freq')
    elif freq > 50:
        score += 1
        reasons.append('med_freq')
    
    # Even distribution suggests structural
    if entropy > 0.8 and n_sec >= 4:
        score += 2
        reasons.append('even_distribution')
    elif entropy > 0.6 and n_sec >= 3:
        score += 1
        reasons.append('moderate_distribution')
    
    # Low concentration suggests structural
    if max_prop < 0.4:
        score += 1
        reasons.append('low_concentration')
    
    # Section-specific suggests content
    if max_prop > 0.7:
        score -= 2
        reasons.append('section_specific')
    
    # Low frequency suggests content
    if freq < 10:
        score -= 2
        reasons.append('low_freq')
    elif freq < 30:
        score -= 1
        reasons.append('lowmed_freq')
    
    # Classify
    if score >= 3:
        classification = 'STRUCTURAL'
    elif score <= -2:
        classification = 'CONTENT'
    else:
        classification = 'AMBIGUOUS'
    
    results.append({
        'stem': stem,
        'frequency': freq,
        'n_sections': n_sec,
        'normalized_entropy': entropy,
        'max_section_proportion': max_prop,
        'classification_score': score,
        'classification': classification,
        'reasons': '; '.join(reasons)
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('frequency', ascending=False)

# Summary statistics
print(f"\n{'='*80}")
print("CLASSIFICATION SUMMARY")
print("="*80)

for classification in ['STRUCTURAL', 'AMBIGUOUS', 'CONTENT']:
    subset = results_df[results_df['classification'] == classification]
    total_tokens = subset['frequency'].sum()
    
    print(f"\n{classification}:")
    print(f"  Stem count: {len(subset)}")
    print(f"  Token count: {total_tokens}")
    print(f"  Mean frequency: {subset['frequency'].mean():.1f}")
    print(f"  Mean entropy: {subset['normalized_entropy'].mean():.3f}")

# Show top structural stems
print(f"\n{'='*80}")
print("TOP 30 STRUCTURAL STEMS")
print("="*80)

structural = results_df[results_df['classification'] == 'STRUCTURAL'].head(30)
print(f"\n{'Stem':<10} {'Freq':<8} {'Sections':<10} {'Entropy':<10} {'Max%':<8}")
print("-" * 60)

for _, row in structural.iterrows():
    print(f"{row['stem']:<10} {row['frequency']:<8.0f} {row['n_sections']:<10.0f} "
          f"{row['normalized_entropy']:<10.3f} {row['max_section_proportion']*100:<8.1f}")

# Show some content words
print(f"\n{'='*80}")
print("SAMPLE CONTENT STEMS (section-specific, lower frequency)")
print("="*80)

content = results_df[results_df['classification'] == 'CONTENT']
content_sample = content[content['frequency'] > 5].head(30)

print(f"\n{'Stem':<10} {'Freq':<8} {'Sections':<10} {'Entropy':<10} {'Max%':<8}")
print("-" * 60)

for _, row in content_sample.iterrows():
    print(f"{row['stem']:<10} {row['frequency']:<8.0f} {row['n_sections']:<10.0f} "
          f"{row['normalized_entropy']:<10.3f} {row['max_section_proportion']*100:<8.1f}")

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT}")

print(f"\n{'='*80}")
print("KEY INSIGHT")
print("="*80)
print("\nFor semantic analysis, focus on:")
print("  1. CONTENT stems (section-specific, meaningful)")
print("  2. High-frequency STRUCTURAL stems may be function words")
print("  3. AMBIGUOUS stems need case-by-case evaluation")

print(f"\nNext step: Run m10_stem_stability.py")
