#!/usr/bin/env python3
"""
TESTING EDWARD'S FUNCTIONAL HYPOTHESIS
=======================================

Edward's hypothesis:
- 'ot-' = beginning/entry of a phase (initiating marker)
- 'ok-' = unit/point/entity within the cycle (constituent marker)  
- 'ch-' = modified/intensified phase state (qualitative modifier)

Testable predictions:
1. 'ot-' should appear at BEGINNINGS (early in sequences)
2. 'ok-' should be DISTRIBUTED (appear throughout)
3. 'ch-' should show MODIFICATION (combine with other markers, intensity)

Medieval parallels:
- Incipit (beginning) / In medio (middle) / Terminus (end)
- Astrological ingress markers
- Alchemical phase notation
"""

import re
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt

print("="*80)
print("TESTING FUNCTIONAL HYPOTHESIS: ot/ok/ch STEM SEMANTICS")
print("="*80)

# Load zodiac labels with sequential position
with open('/home/claude/transliteration.txt', 'r') as f:
    lines = f.readlines()

zodiac_labels = []
current_folio = None
folio_position = 0

for i, line in enumerate(lines):
    match = re.search(r'<(f6[7-9]|f7[0-3])[rv]\d*\.(\d+)', line)
    if match and '@' in line:
        folio_base = match.group(1)
        line_number = int(match.group(2))
        
        text = re.sub(r'<[^>]+>', '', line)
        text = re.sub(r'@\d+;', '', text)
        text = re.sub(r'[{}+=]', '', text)
        tokens = re.findall(r'[a-z]+', text.lower())
        labels = [t for t in tokens if 3 <= len(t) <= 10]
        
        for label in labels:
            zodiac_labels.append({
                'label': label,
                'folio': folio_base,
                'line': line_number,
                'position': folio_position,
                'prefix': label[:2] if len(label) >= 2 else '',
                'suffix': label[-2:] if len(label) >= 2 else ''
            })
            folio_position += 1

print(f"\nTotal labels: {len(zodiac_labels)}")

# Filter to our three universal stems
ot_labels = [l for l in zodiac_labels if l['prefix'] == 'ot']
ok_labels = [l for l in zodiac_labels if l['prefix'] == 'ok']
ch_labels = [l for l in zodiac_labels if l['prefix'] == 'ch']

print(f"\n'ot-' labels: {len(ot_labels)}")
print(f"'ok-' labels: {len(ok_labels)}")
print(f"'ch-' labels: {len(ch_labels)}")

# ============================================================================
# TEST 1: SEQUENTIAL POSITIONING - Are 'ot-' labels at beginnings?
# ============================================================================
print("\n" + "="*80)
print("TEST 1: SEQUENTIAL POSITIONING")
print("="*80)

print("\n--- Prediction 1: 'ot-' should appear early (beginning markers) ---")

# Group by folio and measure position percentiles
def position_percentile(labels_subset, all_labels):
    """What percentile of the sequence do these labels appear at?"""
    percentiles = []
    
    # Group by folio
    folio_groups = defaultdict(list)
    for label in all_labels:
        folio_groups[label['folio']].append(label)
    
    for label in labels_subset:
        folio = label['folio']
        folio_labels = folio_groups[folio]
        
        # What position is this label in its folio?
        positions = [l['line'] for l in folio_labels]
        label_position = label['line']
        
        # Calculate percentile
        percentile = (sum(1 for p in positions if p < label_position) / len(positions)) * 100
        percentiles.append(percentile)
    
    return percentiles

ot_percentiles = position_percentile(ot_labels, zodiac_labels)
ok_percentiles = position_percentile(ok_labels, zodiac_labels)
ch_percentiles = position_percentile(ch_labels, zodiac_labels)

print(f"\nPosition in sequence (percentile):")
print(f"  'ot-': Mean {np.mean(ot_percentiles):.1f}% (median {np.median(ot_percentiles):.1f}%)")
print(f"  'ok-': Mean {np.mean(ok_percentiles):.1f}% (median {np.median(ok_percentiles):.1f}%)")
print(f"  'ch-': Mean {np.mean(ch_percentiles):.1f}% (median {np.median(ch_percentiles):.1f}%)")

# Statistical test
print(f"\nAre 'ot-' labels significantly earlier?")
if np.mean(ot_percentiles) < 40:
    print(f"  ✓ YES: 'ot-' appears in first 40% (mean {np.mean(ot_percentiles):.1f}%)")
elif np.mean(ot_percentiles) < 50:
    print(f"  ○ WEAK: 'ot-' slightly early (mean {np.mean(ot_percentiles):.1f}%)")
else:
    print(f"  ✗ NO: 'ot-' not particularly early (mean {np.mean(ot_percentiles):.1f}%)")

# ============================================================================
# TEST 2: DISTRIBUTION PATTERN - Is 'ok-' evenly distributed?
# ============================================================================
print("\n" + "="*80)
print("TEST 2: DISTRIBUTION PATTERN")
print("="*80)

print("\n--- Prediction 2: 'ok-' should be evenly distributed (constituent units) ---")

# Calculate distribution variance
def distribution_variance(percentiles):
    """How evenly distributed are the positions?"""
    # Bin into 10 deciles
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    counts = np.histogram(percentiles, bins=bins)[0]
    
    # Perfect distribution = 10% in each bin
    expected = len(percentiles) / 10
    chi_square = sum((count - expected)**2 / expected for count in counts if expected > 0)
    
    return chi_square, counts

ot_chi, ot_bins = distribution_variance(ot_percentiles)
ok_chi, ok_bins = distribution_variance(ok_percentiles)
ch_chi, ch_bins = distribution_variance(ch_percentiles)

print(f"\nDistribution uniformity (lower = more even):")
print(f"  'ot-': χ² = {ot_chi:.2f}")
print(f"  'ok-': χ² = {ok_chi:.2f}")
print(f"  'ch-': χ² = {ch_chi:.2f}")

if ok_chi < min(ot_chi, ch_chi):
    print(f"\n✓ YES: 'ok-' is most evenly distributed")
elif ok_chi < ot_chi:
    print(f"\n○ PARTIAL: 'ok-' more even than 'ot-'")
else:
    print(f"\n✗ NO: 'ok-' not particularly even")

# ============================================================================
# TEST 3: MODIFICATION PATTERNS - Does 'ch-' show intensity/modification?
# ============================================================================
print("\n" + "="*80)
print("TEST 3: MODIFICATION PATTERNS")
print("="*80)

print("\n--- Prediction 3: 'ch-' should modify/intensify (qualitative marker) ---")

# Test A: Does 'ch-' combine with other stems?
print("\nTest A: Compound forms (does 'ch-' modify other stems?)")

# Look for labels that contain both 'ch' and other stems
compound_patterns = defaultdict(int)

for label in zodiac_labels:
    full_label = label['label']
    # Check if label contains multiple stem patterns
    if 'ch' in full_label:
        if 'ot' in full_label and full_label.index('ot') != full_label.index('ch'):
            compound_patterns['ch+ot'] += 1
        if 'ok' in full_label and full_label.index('ok') != full_label.index('ch'):
            compound_patterns['ch+ok'] += 1
        if 'sh' in full_label:
            compound_patterns['ch+sh'] += 1

print(f"Compound forms found:")
for pattern, count in sorted(compound_patterns.items(), key=lambda x: x[1], reverse=True):
    print(f"  {pattern}: {count} occurrences")

if compound_patterns:
    print(f"\n✓ YES: 'ch-' appears in compound forms (modification)")
else:
    print(f"\n✗ NO: No clear compound patterns")

# Test B: Length distribution (modifiers might be longer?)
print("\nTest B: Label length (are 'ch-' labels longer/modified?)")

ot_lengths = [len(l['label']) for l in ot_labels]
ok_lengths = [len(l['label']) for l in ok_labels]
ch_lengths = [len(l['label']) for l in ch_labels]

print(f"  'ot-': Mean length {np.mean(ot_lengths):.2f}")
print(f"  'ok-': Mean length {np.mean(ok_lengths):.2f}")
print(f"  'ch-': Mean length {np.mean(ch_lengths):.2f}")

if np.mean(ch_lengths) > max(np.mean(ot_lengths), np.mean(ok_lengths)):
    print(f"\n✓ YES: 'ch-' labels are longer (potential modification)")
else:
    print(f"\n✗ NO: 'ch-' not significantly longer")

# Test C: Suffix diversity (modification = more variation?)
print("\nTest C: Suffix diversity (modifiers = more variable?)")

ot_suffixes = [l['suffix'] for l in ot_labels if l['suffix']]
ok_suffixes = [l['suffix'] for l in ok_labels if l['suffix']]
ch_suffixes = [l['suffix'] for l in ch_labels if l['suffix']]

ot_unique = len(set(ot_suffixes))
ok_unique = len(set(ok_suffixes))
ch_unique = len(set(ch_suffixes))

ot_diversity = ot_unique / len(ot_suffixes) if ot_suffixes else 0
ok_diversity = ok_unique / len(ok_suffixes) if ok_suffixes else 0
ch_diversity = ch_unique / len(ch_suffixes) if ch_suffixes else 0

print(f"  'ot-': {ot_unique} unique suffixes / {len(ot_suffixes)} = {ot_diversity:.3f}")
print(f"  'ok-': {ok_unique} unique suffixes / {len(ok_suffixes)} = {ok_diversity:.3f}")
print(f"  'ch-': {ch_unique} unique suffixes / {len(ch_suffixes)} = {ch_diversity:.3f}")

if ch_diversity > max(ot_diversity, ok_diversity):
    print(f"\n✓ YES: 'ch-' has highest suffix diversity (modification)")
else:
    print(f"\n✗ NO: 'ch-' not particularly diverse")

# ============================================================================
# TEST 4: CO-OCCURRENCE PATTERNS
# ============================================================================
print("\n" + "="*80)
print("TEST 4: CO-OCCURRENCE PATTERNS")
print("="*80)

print("\n--- What comes AFTER 'ot-' (beginning)? ---")

# Find what follows 'ot-' labels
following_ot = []
for i, label in enumerate(zodiac_labels[:-1]):
    if label['prefix'] == 'ot':
        next_label = zodiac_labels[i+1]
        if next_label['folio'] == label['folio']:  # Same folio
            following_ot.append(next_label['prefix'])

following_ot_counts = Counter(following_ot)
print(f"\nPrefixes following 'ot-' (top 5):")
for prefix, count in following_ot_counts.most_common(5):
    pct = count / len(following_ot) * 100 if following_ot else 0
    print(f"  '{prefix}': {count} ({pct:.1f}%)")

# Find what follows 'ok-' labels
following_ok = []
for i, label in enumerate(zodiac_labels[:-1]):
    if label['prefix'] == 'ok':
        next_label = zodiac_labels[i+1]
        if next_label['folio'] == label['folio']:
            following_ok.append(next_label['prefix'])

following_ok_counts = Counter(following_ok)
print(f"\nPrefixes following 'ok-' (top 5):")
for prefix, count in following_ok_counts.most_common(5):
    pct = count / len(following_ok) * 100 if following_ok else 0
    print(f"  '{prefix}': {count} ({pct:.1f}%)")

# ============================================================================
# VISUAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("CREATING VISUAL SUMMARY")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Position distributions
ax1 = axes[0, 0]
ax1.hist(ot_percentiles, bins=20, alpha=0.5, label="'ot-'", color='blue')
ax1.hist(ok_percentiles, bins=20, alpha=0.5, label="'ok-'", color='green')
ax1.hist(ch_percentiles, bins=20, alpha=0.5, label="'ch-'", color='red')
ax1.set_xlabel('Position Percentile')
ax1.set_ylabel('Frequency')
ax1.set_title('Sequential Position Distribution')
ax1.legend()
ax1.axvline(50, color='black', linestyle='--', alpha=0.3)

# Plot 2: Distribution by decile
ax2 = axes[0, 1]
deciles = np.arange(10)
width = 0.25
ax2.bar(deciles - width, [c/sum(ot_bins)*100 for c in ot_bins], width, label="'ot-'", alpha=0.7)
ax2.bar(deciles, [c/sum(ok_bins)*100 for c in ok_bins], width, label="'ok-'", alpha=0.7)
ax2.bar(deciles + width, [c/sum(ch_bins)*100 for c in ch_bins], width, label="'ch-'", alpha=0.7)
ax2.axhline(10, color='black', linestyle='--', alpha=0.3, label='Even distribution')
ax2.set_xlabel('Decile (0-10%, 10-20%, ...)')
ax2.set_ylabel('Percentage of labels')
ax2.set_title('Distribution Uniformity')
ax2.legend()
ax2.set_xticks(deciles)

# Plot 3: Length distributions
ax3 = axes[1, 0]
ax3.boxplot([ot_lengths, ok_lengths, ch_lengths], labels=["'ot-'", "'ok-'", "'ch-'"])
ax3.set_ylabel('Label Length (characters)')
ax3.set_title('Label Length by Stem')

# Plot 4: Following patterns
ax4 = axes[1, 1]
following_prefixes = ['ot', 'ok', 'ch', 'da', 'sh']
ot_following = [following_ot_counts.get(p, 0) for p in following_prefixes]
ok_following = [following_ok_counts.get(p, 0) for p in following_prefixes]
x = np.arange(len(following_prefixes))
ax4.bar(x - 0.2, ot_following, 0.4, label="After 'ot-'", alpha=0.7)
ax4.bar(x + 0.2, ok_following, 0.4, label="After 'ok-'", alpha=0.7)
ax4.set_xlabel('Following Prefix')
ax4.set_ylabel('Count')
ax4.set_title('Co-occurrence Patterns')
ax4.set_xticks(x)
ax4.set_xticklabels(following_prefixes)
ax4.legend()

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/functional_hypothesis_test.png', dpi=300, bbox_inches='tight')
print("Visual saved!")

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*80)
print("FINAL VERDICT: EDWARD'S FUNCTIONAL HYPOTHESIS")
print("="*80)

evidence_score = 0
max_score = 5

print("\nTesting Edward's predictions:")
print("-" * 60)

# Test 1: 'ot-' at beginnings
if np.mean(ot_percentiles) < 40:
    print("✓ 'ot-' appears early (beginning marker)")
    evidence_score += 1
elif np.mean(ot_percentiles) < 50:
    print("○ 'ot-' slightly early")
    evidence_score += 0.5
else:
    print("✗ 'ot-' not particularly early")

# Test 2: 'ok-' distributed
if ok_chi < min(ot_chi, ch_chi):
    print("✓ 'ok-' is most evenly distributed (constituent marker)")
    evidence_score += 1
elif ok_chi < ot_chi:
    print("○ 'ok-' more even than 'ot-'")
    evidence_score += 0.5
else:
    print("✗ 'ok-' not particularly even")

# Test 3a: 'ch-' compounds
if compound_patterns:
    print("✓ 'ch-' appears in compound forms (modification)")
    evidence_score += 1
else:
    print("✗ No clear compound patterns")

# Test 3b: 'ch-' length
if np.mean(ch_lengths) > max(np.mean(ot_lengths), np.mean(ok_lengths)):
    print("✓ 'ch-' labels are longer (modification/intensification)")
    evidence_score += 1
else:
    print("✗ 'ch-' not significantly longer")

# Test 3c: 'ch-' diversity
if ch_diversity > max(ot_diversity, ok_diversity):
    print("✓ 'ch-' has highest suffix diversity (variable modification)")
    evidence_score += 1
else:
    print("✗ 'ch-' not particularly diverse")

print(f"\n" + "="*80)
print(f"EVIDENCE SCORE: {evidence_score:.1f} / {max_score}")
print("="*80)

if evidence_score >= 4:
    print("\n✓✓✓ STRONG SUPPORT for functional hypothesis")
    print("'ot-', 'ok-', 'ch-' appear to have distinct semantic functions")
elif evidence_score >= 2.5:
    print("\n○○ MODERATE SUPPORT for functional hypothesis")
    print("Some patterns consistent with predictions")
else:
    print("\n✗ WEAK SUPPORT for functional hypothesis")
    print("Patterns don't clearly match predictions")

print("\n" + "="*80)
