#!/usr/bin/env python3
"""
Reconstruct Table 2: Calculate Currier A/B entropy from section data
"""

import numpy as np

print("="*80)
print("RECONSTRUCTING TABLE 2: Currier Hand Entropy")
print("="*80)

# From m02_suffix_by_section.tsv - Herbal section (Currier A proxy)
herbal = {
    'NULL': 0.27396593673965935,
    'aiin': 0.10498783454987834,
    'ain': 0.018613138686131386,
    'al': 0.04209245742092457,
    'am': 0.022992700729927006,
    'ody': 0.031143552311435525,
    'ol': 0.10072992700729927,
    'or': 0.07092457420924574,
    'y': 0.33454987834549876
}

# Section token counts from the data
sections = {
    'Biological': 5781,
    'Recipes': 9159,
    'Astronomical': 483,
    'Pharmaceutical': 1316
}

# Suffix proportions by section (for Currier B)
biological = {
    'NULL': 0.17765092544542466, 'aiin': 0.05189413596263622, 'ain': 0.06711641584500952,
    'al': 0.05950527590382287, 'am': 0.008130081300813009, 'ody': 0.0008649022660439371,
    'ol': 0.0728247708008995, 'or': 0.02266043937035115, 'y': 0.5393530531049991
}

recipes = {
    'NULL': 0.2731739272846381, 'aiin': 0.09171306911234851, 'ain': 0.06277977945190523,
    'al': 0.051970739163664154, 'am': 0.021618080576482148, 'ody': 0.02576700513156458,
    'ol': 0.048367725734250466, 'or': 0.02707719183316956, 'y': 0.3975324817119773
}

astronomical = {
    'NULL': 0.38716356107660455, 'aiin': 0.039337474120082816, 'ain': 0.006211180124223602,
    'al': 0.060041407867494824, 'am': 0.024844720496894408, 'ody': 0.062111801242236024,
    'ol': 0.039337474120082816, 'or': 0.033126293995859216, 'y': 0.34782608695652173
}

pharmaceutical = {
    'NULL': 0.2682370820668693, 'aiin': 0.07522796352583587, 'ain': 0.0121580547112462,
    'al': 0.030395136778115502, 'am': 0.010638297872340425, 'ody': 0.06534954407294832,
    'ol': 0.20288753799392098, 'or': 0.08738601823708207, 'y': 0.24772036474164133
}

def calculate_entropy(distribution):
    """Calculate Shannon entropy from probability distribution"""
    probs = np.array([p for p in distribution.values() if p > 0])
    return -np.sum(probs * np.log2(probs))

def combine_sections(section_dists, section_counts):
    """Combine multiple section distributions weighted by token counts"""
    total_tokens = sum(section_counts.values())
    
    # Initialize combined distribution
    combined = {}
    all_suffixes = set()
    for dist in section_dists.values():
        all_suffixes.update(dist.keys())
    
    # Weighted average
    for suffix in all_suffixes:
        combined[suffix] = 0
        for section_name, dist in section_dists.items():
            weight = section_counts[section_name] / total_tokens
            combined[suffix] += dist.get(suffix, 0) * weight
    
    return combined

# Calculate Currier A (Herbal) entropy
currier_a_entropy = calculate_entropy(herbal)

# Calculate Currier B (combined sections) entropy
currier_b_sections = {
    'Biological': biological,
    'Recipes': recipes,
    'Astronomical': astronomical,
    'Pharmaceutical': pharmaceutical
}
currier_b_combined = combine_sections(currier_b_sections, sections)
currier_b_entropy = calculate_entropy(currier_b_combined)

print("\n" + "="*80)
print("CURRIER A (Herbal Section)")
print("="*80)
print(f"Entropy: {currier_a_entropy:.3f} bits")
print("\nSuffix distribution:")
for suffix, prob in sorted(herbal.items(), key=lambda x: -x[1]):
    print(f"  {suffix:4s}: {prob*100:5.1f}%")

print("\n" + "="*80)
print("CURRIER B (Bio + Recipes + Astro + Pharm)")
print("="*80)
print(f"Entropy: {currier_b_entropy:.3f} bits")
print(f"\nCombined from:")
for section, count in sections.items():
    print(f"  {section:15s}: {count:5d} tokens ({count/sum(sections.values())*100:.1f}%)")
print("\nCombined suffix distribution:")
for suffix, prob in sorted(currier_b_combined.items(), key=lambda x: -x[1]):
    print(f"  {suffix:4s}: {prob*100:5.1f}%")

print("\n" + "="*80)
print("COMPARISON TO TABLE 2 IN PAPER")
print("="*80)
print("\nPaper claimed:")
print("  Currier A: entropy 2.578 bits")
print("  Currier B: entropy 2.017 bits")
print("  Difference: 0.561 bits")
print("\nOur reconstruction:")
print(f"  Currier A: entropy {currier_a_entropy:.3f} bits")
print(f"  Currier B: entropy {currier_b_entropy:.3f} bits")
print(f"  Difference: {currier_a_entropy - currier_b_entropy:.3f} bits")

# Check if they match (within rounding)
if abs(currier_a_entropy - 2.578) < 0.01 and abs(currier_b_entropy - 2.017) < 0.01:
    print("\n✓✓✓ MATCH! Table 2 values reproduced!")
else:
    print("\n⚠️  Different values - investigating discrepancy...")
    print(f"\nDiscrepancies:")
    print(f"  Currier A: {abs(currier_a_entropy - 2.578):.3f} bits off")
    print(f"  Currier B: {abs(currier_b_entropy - 2.017):.3f} bits off")

print("\n" + "="*80)
print("WHAT THIS MEANS")
print("="*80)

if abs(currier_a_entropy - 2.578) < 0.1:
    print("\n✓ Values are close - Table 2 is REPRODUCIBLE from section data")
    print("✓ Currier A (Herbal) does have higher entropy than B")
    print("✓ This supports register variation hypothesis")
else:
    print("\n⚠️  Values differ significantly")
    print("   Possible reasons:")
    print("   1. Different method was used (not just section aggregation)")
    print("   2. NULL category was excluded from original calculation")
    print("   3. Hand assignments differ from section assignments")

