#!/usr/bin/env python3
"""
Analyze Cappelli abbreviation patterns
"""

from pathlib import Path
from collections import Counter
import random

BASE = Path(__file__).parent

print("="*80)
print("CAPPELLI ABBREVIATION ANALYSIS")
print("="*80)

# Load parallel texts
expanded = BASE / "latin_abbrev_expanded.txt"
compressed = BASE / "latin_abbrev_compressed.txt"

exp_tokens = expanded.read_text().lower().split()
comp_tokens = compressed.read_text().lower().split()

print(f"\nExpanded tokens: {len(exp_tokens):,}")
print(f"Compressed tokens: {len(comp_tokens):,}")

min_len = min(len(exp_tokens), len(comp_tokens))
if len(exp_tokens) != len(comp_tokens):
    print(f"⚠️ Using first {min_len:,} pairs")

# Analyze compression
total_exp_chars = sum(len(t) for t in exp_tokens[:min_len])
total_comp_chars = sum(len(t) for t in comp_tokens[:min_len])

compression_ratio = total_comp_chars / total_exp_chars

print(f"\nTotal characters:")
print(f"  Expanded: {total_exp_chars:,}")
print(f"  Compressed: {total_comp_chars:,}")
print(f"  Ratio: {compression_ratio:.3f}")
print(f"  Reduction: {(1-compression_ratio)*100:.1f}%")

# Mean lengths
mean_exp = total_exp_chars / min_len
mean_comp = total_comp_chars / min_len

print(f"\nMean token length:")
print(f"  Expanded: {mean_exp:.2f} chars/token")
print(f"  Compressed: {mean_comp:.2f} chars/token")

# Compare to Voynich
voynich_mean = 5.09
print(f"\n  Voynich: {voynich_mean:.2f} chars/token")
print(f"  Voynich position: {(voynich_mean - mean_comp)/(mean_exp - mean_comp)*100:.1f}% between compressed and expanded")

# Compression patterns
print("\n" + "="*80)
print("COMPRESSION PATTERNS")
print("="*80)

patterns = Counter()
endings_removed = Counter()

for exp, comp in zip(exp_tokens[:min_len], comp_tokens[:min_len]):
    if len(exp) > len(comp):
        diff = len(exp) - len(comp)
        patterns[f"{diff}_chars_removed"] += 1
        
        # Check if ending removed
        if len(comp) > 0 and exp.startswith(comp):
            ending = exp[len(comp):]
            endings_removed[ending] += 1

print("\nCharacter deletion:")
for pattern, count in sorted(patterns.items()):
    pct = count / min_len * 100
    print(f"  {pattern:20s}: {count:6,} ({pct:5.1f}%)")

print("\nTop 20 removed endings:")
for ending, count in endings_removed.most_common(20):
    pct = count / min_len * 100
    print(f"  -{ending:15s}: {count:5,} ({pct:4.1f}%)")

# Sample pairs
print("\n" + "="*80)
print("SAMPLE ABBREVIATIONS")
print("="*80)

random.seed(1420)
sample_indices = random.sample(range(min_len), min(30, min_len))

for i in sample_indices[:20]:
    exp = exp_tokens[i]
    comp = comp_tokens[i]
    if len(exp) > 0:
        ratio = len(comp) / len(exp)
        reduction = (1 - ratio) * 100
        print(f"  {exp:20s} → {comp:12s} ({reduction:4.0f}% reduction)")

# Suffix analysis
print("\n" + "="*80)
print("SUFFIX PRESERVATION")
print("="*80)

# Check what suffixes remain after compression
from collections import defaultdict

suffix_map = defaultdict(Counter)

for exp, comp in zip(exp_tokens[:min_len], comp_tokens[:min_len]):
    if len(exp) > 2 and len(comp) > 1:
        # Get last 2 chars of each
        exp_end = exp[-2:]
        comp_end = comp[-2:] if len(comp) >= 2 else comp[-1:]
        suffix_map[exp_end][comp_end] += 1

print("\nHow expanded endings map to compressed:")
for exp_end in sorted(suffix_map.keys())[:15]:
    comp_dist = suffix_map[exp_end]
    total = sum(comp_dist.values())
    print(f"\n  -{exp_end} ({total:,} occurrences):")
    for comp_end, count in comp_dist.most_common(5):
        pct = count / total * 100
        print(f"    → {comp_end:8s} {count:5,} ({pct:5.1f}%)")

print("\n" + "="*80)
print("COMPARISON TO VOYNICH")
print("="*80)

print(f"\nCappelli Latin abbreviation:")
print(f"  Mean length: {mean_comp:.2f} chars")
print(f"  Compression: {(1-compression_ratio)*100:.0f}% reduction")

print(f"\nVoynichese:")
print(f"  Mean length: 5.09 chars")
print(f"  Inferred compression: ~34% reduction (from 7.76)")

print(f"\nInterpretation:")
if abs(mean_comp - 5.09) < 1.0:
    print(f"  ✓ Voynich length ({5.09:.2f}) matches Cappelli compressed ({mean_comp:.2f})")
else:
    print(f"  Voynich ({5.09:.2f}) is intermediate between")
    print(f"  Cappelli compressed ({mean_comp:.2f}) and expanded ({mean_exp:.2f})")

