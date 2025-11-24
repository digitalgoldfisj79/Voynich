#!/usr/bin/env python3
"""
Which section or combination matches Currier B entropy of 2.017?
"""

import numpy as np

sections_data = {
    'Biological': {
        'NULL': 0.17765092544542466, 'aiin': 0.05189413596263622, 'ain': 0.06711641584500952,
        'al': 0.05950527590382287, 'am': 0.008130081300813009, 'ody': 0.0008649022660439371,
        'ol': 0.0728247708008995, 'or': 0.02266043937035115, 'y': 0.5393530531049991
    },
    'Recipes': {
        'NULL': 0.2731739272846381, 'aiin': 0.09171306911234851, 'ain': 0.06277977945190523,
        'al': 0.051970739163664154, 'am': 0.021618080576482148, 'ody': 0.02576700513156458,
        'ol': 0.048367725734250466, 'or': 0.02707719183316956, 'y': 0.3975324817119773
    },
    'Astronomical': {
        'NULL': 0.38716356107660455, 'aiin': 0.039337474120082816, 'ain': 0.006211180124223602,
        'al': 0.060041407867494824, 'am': 0.024844720496894408, 'ody': 0.062111801242236024,
        'ol': 0.039337474120082816, 'or': 0.033126293995859216, 'y': 0.34782608695652173
    },
    'Pharmaceutical': {
        'NULL': 0.2682370820668693, 'aiin': 0.07522796352583587, 'ain': 0.0121580547112462,
        'al': 0.030395136778115502, 'am': 0.010638297872340425, 'ody': 0.06534954407294832,
        'ol': 0.20288753799392098, 'or': 0.08738601823708207, 'y': 0.24772036474164133
    },
    'Herbal': {
        'NULL': 0.27396593673965935, 'aiin': 0.10498783454987834, 'ain': 0.018613138686131386,
        'al': 0.04209245742092457, 'am': 0.022992700729927006, 'ody': 0.031143552311435525,
        'ol': 0.10072992700729927, 'or': 0.07092457420924574, 'y': 0.33454987834549876
    }
}

def calculate_entropy(distribution):
    """Calculate Shannon entropy from probability distribution"""
    probs = np.array([p for p in distribution.values() if p > 0])
    return -np.sum(probs * np.log2(probs))

print("="*80)
print("TESTING WHICH SECTION(S) MATCH CURRIER B = 2.017")
print("="*80)

print("\nIndividual section entropies:")
for section, dist in sections_data.items():
    entropy = calculate_entropy(dist)
    diff = abs(entropy - 2.017)
    match = "✓✓✓ MATCH!" if diff < 0.01 else ""
    print(f"  {section:15s}: {entropy:.3f} bits (diff: {diff:.3f}) {match}")

# Try excluding NULL category
print("\n" + "="*80)
print("WITHOUT NULL CATEGORY (maybe NULL was excluded?)")
print("="*80)

for section, dist in sections_data.items():
    # Remove NULL and renormalize
    dist_no_null = {k: v for k, v in dist.items() if k != 'NULL'}
    total = sum(dist_no_null.values())
    dist_normalized = {k: v/total for k, v in dist_no_null.items()}
    
    entropy = calculate_entropy(dist_normalized)
    diff = abs(entropy - 2.017)
    match = "✓✓✓ MATCH!" if diff < 0.01 else ""
    print(f"  {section:15s}: {entropy:.3f} bits (diff: {diff:.3f}) {match}")

# Try Recipes + Pharmaceutical only
print("\n" + "="*80)
print("TESTING DIFFERENT COMBINATIONS")
print("="*80)

combos = [
    ("Recipes only", ['Recipes']),
    ("Recipes + Pharm", ['Recipes', 'Pharmaceutical']),
    ("Bio + Recipes", ['Biological', 'Recipes']),
    ("All except Herbal", ['Biological', 'Recipes', 'Astronomical', 'Pharmaceutical'])
]

section_counts = {
    'Biological': 5781,
    'Recipes': 9159,
    'Astronomical': 483,
    'Pharmaceutical': 1316
}

def combine_sections(section_names, section_dists, section_counts):
    """Combine multiple sections weighted by token counts"""
    total_tokens = sum(section_counts[s] for s in section_names)
    
    combined = {}
    all_suffixes = set()
    for s in section_names:
        all_suffixes.update(section_dists[s].keys())
    
    for suffix in all_suffixes:
        combined[suffix] = 0
        for section_name in section_names:
            weight = section_counts[section_name] / total_tokens
            combined[suffix] += section_dists[section_name].get(suffix, 0) * weight
    
    return combined

for name, section_list in combos:
    if all(s in section_counts for s in section_list):
        combined = combine_sections(section_list, sections_data, section_counts)
        entropy = calculate_entropy(combined)
        diff = abs(entropy - 2.017)
        match = "✓✓✓ MATCH!" if diff < 0.02 else ""
        print(f"  {name:25s}: {entropy:.3f} bits (diff: {diff:.3f}) {match}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("\nThe claimed 2.017 bits doesn't match any obvious combination.")
print("Possibilities:")
print("1. Used different hand assignments (not just sections)")
print("2. Excluded NULL category")
print("3. Calculated from actual token counts by hand (not section aggregation)")
print("4. There's an error in the paper's reported value")

