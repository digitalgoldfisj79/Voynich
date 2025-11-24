#!/usr/bin/env python3
"""
Test 1: Frequency Distribution (Zipf's Law)

Hypothesis: If Voynichese is compressed Latin, frequency distributions should match.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).parent.parent
OUTPUT_TSV = BASE / "Integration_Analysis/test01_results.tsv"
OUTPUT_PNG = BASE / "Integration_Analysis/test01_zipf_comparison.png"

print("="*80)
print("TEST 1: FREQUENCY DISTRIBUTION COMPARISON")
print("="*80)

# Load frequencies
print("\nLoading data...")
voynich_freq = pd.read_csv(BASE / "metadata/t03_stem_frequencies.tsv", sep='\t')
latin_freq = pd.read_csv(BASE / "PhaseS/out/s6_latin_token_freq.tsv", sep='\t')
materia_freq = pd.read_csv(BASE / "PhaseS/out/s6_materia_token_freq.tsv", sep='\t')

# Rename columns for consistency
voynich_freq = voynich_freq.rename(columns={'stem_freq': 'count'})
latin_freq = latin_freq.rename(columns={'token': 'item', 'total_count': 'count'})
materia_freq = materia_freq.rename(columns={'token': 'item', 'total_count': 'count'})
voynich_freq = voynich_freq.rename(columns={'stem': 'item'})

# Calculate total tokens and frequencies
voynich_total = voynich_freq['count'].sum()
latin_total = latin_freq['count'].sum()
materia_total = materia_freq['count'].sum()

voynich_freq['frequency'] = voynich_freq['count'] / voynich_total
latin_freq['frequency'] = latin_freq['count'] / latin_total
materia_freq['frequency'] = materia_freq['count'] / materia_total

print(f"Voynichese: {len(voynich_freq)} stems, {voynich_total} total tokens")
print(f"Latin (all): {len(latin_freq)} types, {latin_total} total tokens")
print(f"De Materia: {len(materia_freq)} types, {materia_total} total tokens")

# Sort by frequency
voynich_freq = voynich_freq.sort_values('frequency', ascending=False).reset_index(drop=True)
latin_freq = latin_freq.sort_values('frequency', ascending=False).reset_index(drop=True)
materia_freq = materia_freq.sort_values('frequency', ascending=False).reset_index(drop=True)

# Add ranks
voynich_freq['rank'] = range(1, len(voynich_freq) + 1)
latin_freq['rank'] = range(1, len(latin_freq) + 1)
materia_freq['rank'] = range(1, len(materia_freq) + 1)

# Calculate Zipf slopes
def zipf_slope(df, n=100):
    subset = df.head(n)
    log_rank = np.log10(subset['rank'])
    log_freq = np.log10(subset['frequency'])
    slope = np.polyfit(log_rank, log_freq, 1)[0]
    return slope

voynich_slope = zipf_slope(voynich_freq)
latin_slope = zipf_slope(latin_freq)
materia_slope = zipf_slope(materia_freq)

print(f"\n{'='*80}")
print("ZIPF SLOPES (top 100 items)")
print("="*80)
print(f"Voynichese:  {voynich_slope:.3f}")
print(f"Latin (all): {latin_slope:.3f}")
print(f"De Materia:  {materia_slope:.3f}")
print(f"\nExpected Zipf slope: ~-1.0")

slope_diff_latin = abs(voynich_slope - latin_slope)
slope_diff_materia = abs(voynich_slope - materia_slope)

print(f"\nSlope differences:")
print(f"  Voynich vs Latin: {slope_diff_latin:.3f}")
print(f"  Voynich vs De Materia: {slope_diff_materia:.3f}")

test1_pass = slope_diff_materia < 0.3

# Top 10 comparison
print(f"\n{'='*80}")
print("TOP 10 FREQUENCY COMPARISON")
print("="*80)

print(f"\nVoynichese top 10:")
for i, row in voynich_freq.head(10).iterrows():
    print(f"  {row['rank']:2d}. {row['item']:10s}: {row['frequency']:.6f} ({int(row['count'])} tokens)")

print(f"\nDe Materia top 10:")
for i, row in materia_freq.head(10).iterrows():
    print(f"  {row['rank']:2d}. {row['item']:10s}: {row['frequency']:.6f} ({int(row['count'])} tokens)")

# Concentration
voynich_top10pct = voynich_freq.head(int(len(voynich_freq)*0.1))['frequency'].sum()
latin_top10pct = latin_freq.head(int(len(latin_freq)*0.1))['frequency'].sum()
materia_top10pct = materia_freq.head(int(len(materia_freq)*0.1))['frequency'].sum()

print(f"\n{'='*80}")
print("CONCENTRATION (top 10% of types)")
print("="*80)
print(f"Voynichese:  {voynich_top10pct*100:.1f}%")
print(f"Latin (all): {latin_top10pct*100:.1f}%")
print(f"De Materia:  {materia_top10pct*100:.1f}%")

concentration_diff = abs(voynich_top10pct - materia_top10pct)
test3_pass = concentration_diff < 0.15

# Plot
fig, ax = plt.subplots(figsize=(10, 6))

n_plot = min(500, len(voynich_freq), len(latin_freq), len(materia_freq))

ax.loglog(voynich_freq.head(n_plot)['rank'], 
          voynich_freq.head(n_plot)['frequency'], 
          'o-', label='Voynichese', markersize=3, alpha=0.7)
ax.loglog(materia_freq.head(n_plot)['rank'], 
          materia_freq.head(n_plot)['frequency'], 
          's-', label='De Materia', markersize=3, alpha=0.7)
ax.loglog(latin_freq.head(n_plot)['rank'], 
          latin_freq.head(n_plot)['frequency'], 
          '^-', label='Latin (general)', markersize=3, alpha=0.5)

x_ref = np.array([1, n_plot])
y_ref = voynich_freq.iloc[0]['frequency'] / x_ref
ax.loglog(x_ref, y_ref, 'k--', label="Zipf's Law (slope=-1)", alpha=0.5)

ax.set_xlabel('Rank', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Frequency Distribution Comparison', fontsize=14)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=150)
print(f"\n✓ Saved plot: {OUTPUT_PNG}")

# VERDICT
print(f"\n{'='*80}")
print("VERDICT: TEST 1 - FREQUENCY DISTRIBUTION")
print("="*80)

tests_passed = 0
tests_total = 3

print(f"\n1. Zipf slope similarity: ", end="")
if test1_pass:
    print(f"✓ PASS (diff={slope_diff_materia:.3f} < 0.3)")
    tests_passed += 1
else:
    print(f"✗ FAIL (diff={slope_diff_materia:.3f} >= 0.3)")

print(f"\n2. Slopes follow Zipf's law: ", end="")
voynich_zipf = abs(voynich_slope + 1.0) < 0.3
materia_zipf = abs(materia_slope + 1.0) < 0.3
if voynich_zipf and materia_zipf:
    print(f"✓ PASS (both ~-1.0)")
    tests_passed += 1
else:
    print(f"✗ FAIL (V:{voynich_slope:.2f}, M:{materia_slope:.2f})")

print(f"\n3. Concentration similarity: ", end="")
if test3_pass:
    print(f"✓ PASS (diff={concentration_diff*100:.1f}% < 15%)")
    tests_passed += 1
else:
    print(f"✗ FAIL (diff={concentration_diff*100:.1f}% >= 15%)")

print(f"\n{'-'*80}")
print(f"Tests passed: {tests_passed}/{tests_total}")

if tests_passed == 3:
    verdict = "PASS"
elif tests_passed >= 2:
    verdict = "WEAK PASS"
elif tests_passed >= 1:
    verdict = "INCONCLUSIVE"
else:
    verdict = "FAIL"

print(f"\nOVERALL VERDICT: {verdict}")

# Save
results = pd.DataFrame([{
    'test': 'frequency_distribution',
    'verdict': verdict,
    'voynich_slope': voynich_slope,
    'materia_slope': materia_slope,
    'slope_diff': slope_diff_materia,
    'concentration_diff': concentration_diff,
    'tests_passed': tests_passed
}])

OUTPUT_TSV.parent.mkdir(parents=True, exist_ok=True)
results.to_csv(OUTPUT_TSV, sep='\t', index=False)
print(f"\n✓ Saved: {OUTPUT_TSV}")
