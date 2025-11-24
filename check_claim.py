#!/usr/bin/env python3
"""
Critical check: Are we overstating the match?
"""

print("="*80)
print("CRITICAL EVALUATION")
print("="*80)

voynich = {
    'y': 38.4, 'NULL': 21.8, 'aiin': 9.8, 'ol': 9.1, 
    'al': 5.8, 'or': 5.4, 'ain': 4.5, 'ody': 3.0, 'am': 2.2
}

merged_latin = {
    'y': 18.4, 'NULL': 17.1, 'aiin': 8.9, 'ol': 8.3,
    'al': 9.0, 'or': 1.6, 'ain': 11.1, 'ody': 11.6, 'am': 13.9
}

print("\nDISTRIBUTION COMPARISON (percentage points):")
print(f"{'Suffix':6s} {'Voynich':>8s} {'Merged':>8s} {'Diff':>8s} {'Match?':>8s}")
print("-" * 42)

for suffix in ['y', 'NULL', 'aiin', 'ol', 'al', 'or', 'ain', 'ody', 'am']:
    v = voynich[suffix]
    m = merged_latin[suffix]
    diff = abs(v - m)
    
    if diff < 2:
        match = "✓✓✓"
    elif diff < 5:
        match = "✓"
    elif diff < 10:
        match = "~"
    else:
        match = "✗"
    
    print(f"{suffix:6s} {v:7.1f}% {m:7.1f}% {diff:7.1f}pp {match:>8s}")

print("\n" + "="*80)
print("HONEST ASSESSMENT")
print("="*80)

major_diff = sum(1 for s in voynich if abs(voynich[s] - merged_latin[s]) > 5)
close = sum(1 for s in voynich if abs(voynich[s] - merged_latin[s]) < 2)

print(f"\nSuffixes with <2pp difference: {close}/9")
print(f"Suffixes with >5pp difference: {major_diff}/9")

print("\n✓ WHAT WORKS:")
print("  - Same 9 suffix types ✓")
print("  - Same token length ✓")
print("  - All suffixes present ✓")

print("\n⚠️ WHAT DOESN'T WORK:")
print("  - y-suffix: 20pp off (38% vs 18%)")
print("  - am-suffix: 11pp off (2% vs 14%)")
print("  - Entropy: 16% higher (3.01 vs 2.59)")
print("  - Correlation: only 0.645 (moderate)")

print("\n" + "="*80)
print("VERDICT")
print("="*80)

print("\nHonest conclusion:")
print("  ✓ Compression + merging produces RIGHT STRUCTURE")
print("  ✗ But WRONG PROPORTIONS")
print("")
print("  This means:")
print("  - The MECHANISM works (can get 9 types)")
print("  - The DETAILS differ (proportions way off)")
print("")
print("  Interpretation:")
print("  - If Voynichese = compressed Latin, MORE is needed")
print("  - OR Voynichese isn't just compressed Latin")
print("  - OR our merger rules are wrong")

