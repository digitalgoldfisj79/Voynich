#!/usr/bin/env python3
"""
RIGOROUS STATISTICAL CONTROLS
==============================

Before claiming any patterns are real, we need to test against:
1. Baseline Voynichese bigram frequencies (are zodiac labels special?)
2. Morphological relatedness (edit distance clustering)
3. Suffix family analysis (are "clusters" just morphological variants?)
4. Randomization/permutation controls (could we get this by chance?)
5. Frequency controls (do common labels just appear everywhere?)

This is the CRITICAL methodological step we skipped.
"""

import re
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import chi2_contingency, entropy
import random
from itertools import combinations

print("="*80)
print("CRITICAL STATISTICAL CONTROLS")
print("="*80)

# Load full transliteration
with open('/home/claude/transliteration.txt', 'r') as f:
    lines = f.readlines()

# ============================================================================
# STEP 1: BASELINE VOYNICHESE BIGRAM FREQUENCIES
# ============================================================================
print("\n" + "="*80)
print("STEP 1: BASELINE VOYNICHESE BIGRAM FREQUENCIES")
print("="*80)

# Extract ALL Voynichese text (not just zodiac)
all_voynichese_text = []
zodiac_labels = []

zodiac_folios = set([f'f{i}{r}{n}' for i in range(67, 74) 
                     for r in ['r', 'v'] 
                     for n in ['', '1', '2', '3']])

current_folio = None
for line in lines:
    match = re.match(r'<(f\d+[rv]\d*)', line)
    if match:
        current_folio = match.group(1)
    
    # Extract clean text
    if '@' not in line and '<' in line:  # Regular text line
        text = re.sub(r'<[^>]+>', '', line)
        text = re.sub(r'[^a-z]', '', text.lower())
        
        if current_folio and current_folio in zodiac_folios:
            zodiac_labels.append(text)
        else:
            all_voynichese_text.append(text)

# Compute bigram frequencies for baseline
baseline_bigrams = Counter()
for text in all_voynichese_text:
    for i in range(len(text)-1):
        bigram = text[i:i+2]
        baseline_bigrams[bigram] += 1

total_baseline_bigrams = sum(baseline_bigrams.values())

# Compute bigram frequencies for zodiac labels
zodiac_bigrams = Counter()
zodiac_text = ''.join(zodiac_labels)
for i in range(len(zodiac_text)-1):
    bigram = zodiac_text[i:i+2]
    zodiac_bigrams[bigram] += 1

total_zodiac_bigrams = sum(zodiac_bigrams.values())

print(f"\nBaseline Voynichese: {total_baseline_bigrams:,} bigrams")
print(f"Zodiac section: {total_zodiac_bigrams:,} bigrams")

# Compare top bigrams
print("\nTop 20 bigrams - Baseline vs Zodiac:")
print(f"{'Bigram':<8} {'Baseline %':<12} {'Zodiac %':<12} {'Ratio':<8} {'Significant?'}")
print("-" * 65)

top_baseline = set([bg for bg, _ in baseline_bigrams.most_common(50)])
top_zodiac = set([bg for bg, _ in zodiac_bigrams.most_common(50)])
top_combined = top_baseline | top_zodiac

enrichment_scores = []
for bigram in sorted(top_combined, key=lambda x: zodiac_bigrams[x], reverse=True)[:20]:
    baseline_pct = (baseline_bigrams[bigram] / total_baseline_bigrams * 100) if total_baseline_bigrams else 0
    zodiac_pct = (zodiac_bigrams[bigram] / total_zodiac_bigrams * 100) if total_zodiac_bigrams else 0
    ratio = zodiac_pct / baseline_pct if baseline_pct > 0 else float('inf')
    
    # Simple significance test
    significant = "***" if ratio > 1.5 or ratio < 0.67 else ""
    
    enrichment_scores.append((bigram, ratio))
    print(f"'{bigram}'      {baseline_pct:6.2f}%      {zodiac_pct:6.2f}%      {ratio:6.2f}x  {significant}")

print("\n🔍 KEY FINDING:")
ot_baseline = baseline_bigrams['ot'] / total_baseline_bigrams * 100
ot_zodiac = zodiac_bigrams['ot'] / total_zodiac_bigrams * 100
ot_ratio = ot_zodiac / ot_baseline if ot_baseline > 0 else 0

print(f"'ot' bigram: {ot_baseline:.2f}% baseline → {ot_zodiac:.2f}% zodiac = {ot_ratio:.2f}x")
if ot_ratio > 1.2:
    print("✓ 'ot' IS enriched in zodiac section")
else:
    print("✗ 'ot' is NOT particularly enriched (baseline effect!)")

# ============================================================================
# STEP 2: EDIT DISTANCE CLUSTERING
# ============================================================================
print("\n" + "="*80)
print("STEP 2: MORPHOLOGICAL RELATEDNESS (Edit Distance)")
print("="*80)

def edit_distance(s1, s2):
    """Compute Levenshtein distance"""
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# Get repeated zodiac labels from our analysis
from collections import Counter
zodiac_labels_list = []
current_folio = None
for line in lines:
    match = re.match(r'<(f\d+[rv]\d*)', line)
    if match:
        current_folio = match.group(1)
    
    if current_folio and current_folio in zodiac_folios:
        if any(marker in line for marker in ['@Ri', '@Ls', '@Ro', '@Cc', '@Pb']):
            text = re.sub(r'<[^>]+>', '', line)
            text = re.sub(r'@\d+;', '', text)
            tokens = re.findall(r'[a-z]+', text.lower())
            labels = [t for t in tokens if 3 <= len(t) <= 10]
            zodiac_labels_list.extend(labels)

label_freq = Counter(zodiac_labels_list)
frequent_labels = [label for label, count in label_freq.items() if count >= 5]

print(f"\nAnalyzing {len(frequent_labels)} frequent labels (n≥5)")

# Find morphologically related clusters
clusters = []
used = set()

for label1 in frequent_labels:
    if label1 in used:
        continue
    
    cluster = [label1]
    for label2 in frequent_labels:
        if label2 != label1 and label2 not in used:
            dist = edit_distance(label1, label2)
            if dist <= 2:  # Very similar
                cluster.append(label2)
                used.add(label2)
    
    if len(cluster) > 1:
        clusters.append(cluster)
        used.add(label1)

print(f"\nFound {len(clusters)} morphological clusters (edit distance ≤ 2):")
for i, cluster in enumerate(clusters[:10], 1):
    freqs = [label_freq[l] for l in cluster]
    print(f"  {i}. {cluster} (frequencies: {freqs})")

print("\n🔍 KEY QUESTION:")
print("Are our 'position-consistent' labels morphologically related?")

# Check if 'oteey', 'otey', 'oteos', 'noteody' are related
ot_family = [l for l in frequent_labels if l.startswith('ot')]
print(f"\n'ot-' family: {len(ot_family)} labels")
print(f"Top 'ot-' labels: {sorted(ot_family, key=lambda x: label_freq[x], reverse=True)[:10]}")

# Are they just morphological variants?
ot_distances = []
for l1, l2 in combinations(ot_family[:10], 2):
    dist = edit_distance(l1, l2)
    if dist <= 3:
        ot_distances.append((l1, l2, dist))

if ot_distances:
    print(f"\nClose 'ot-' variants (edit distance ≤ 3):")
    for l1, l2, dist in ot_distances[:10]:
        print(f"  '{l1}' ↔ '{l2}': distance {dist}")

# ============================================================================
# STEP 3: SUFFIX FAMILY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("STEP 3: SUFFIX FAMILY CLUSTERING")
print("="*80)

# Group labels by suffix
suffix_families = defaultdict(list)
for label in frequent_labels:
    if len(label) >= 4:
        suffix = label[-2:]  # Last 2 characters
        suffix_families[suffix].append(label)

large_families = {suffix: labels for suffix, labels in suffix_families.items() if len(labels) >= 3}

print(f"\nFound {len(large_families)} suffix families (n≥3):")
for suffix, labels in sorted(large_families.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    print(f"  '-{suffix}': {labels[:8]}")

print("\n🔍 KEY QUESTION:")
print("Do suffix families appear in similar positions?")
print("(If yes, 'position clustering' might be morphological artifact)")

# ============================================================================
# STEP 4: PERMUTATION TEST
# ============================================================================
print("\n" + "="*80)
print("STEP 4: RANDOMIZATION CONTROL")
print("="*80)

# Get labels with positions
labels_with_position = []
current_folio = None
for line in lines:
    match = re.match(r'<(f\d+[rv]\d*)', line)
    if match:
        current_folio = match.group(1)
    
    if current_folio and current_folio in zodiac_folios:
        if '@Cc' in line:
            position = 'center'
        elif '@Ri' in line:
            position = 'inner'
        elif '@Ro' in line:
            position = 'outer'
        else:
            position = None
        
        if position:
            text = re.sub(r'<[^>]+>', '', line)
            text = re.sub(r'@\d+;', '', text)
            tokens = re.findall(r'[a-z]+', text.lower())
            labels = [t for t in tokens if 3 <= len(t) <= 10]
            for label in labels:
                labels_with_position.append((label, position))

print(f"\nLabels with position markers: {len(labels_with_position)}")

# Calculate observed position consistency for top labels
def position_consistency(label, label_position_list):
    """Calculate % of time a label appears in its most common position"""
    label_positions = [pos for lbl, pos in label_position_list if lbl == label]
    if not label_positions:
        return 0
    
    position_counts = Counter(label_positions)
    most_common_count = position_counts.most_common(1)[0][1]
    return most_common_count / len(label_positions)

top_labels = ['oteey', 'aiin', 'otey', 'chey', 'daiin']
observed_consistencies = {}

for label in top_labels:
    consistency = position_consistency(label, labels_with_position)
    observed_consistencies[label] = consistency

print("\nObserved position consistency:")
for label, cons in observed_consistencies.items():
    print(f"  '{label}': {cons*100:.1f}%")

# PERMUTATION TEST: Shuffle labels randomly
print("\nRunning permutation test (1000 iterations)...")

n_permutations = 1000
random_consistencies = {label: [] for label in top_labels}

for iteration in range(n_permutations):
    # Shuffle labels while keeping positions fixed
    shuffled_labels = [label for label, _ in labels_with_position]
    random.shuffle(shuffled_labels)
    shuffled_data = [(shuffled_labels[i], labels_with_position[i][1]) 
                     for i in range(len(labels_with_position))]
    
    for label in top_labels:
        consistency = position_consistency(label, shuffled_data)
        random_consistencies[label].append(consistency)

print("\nPermutation test results:")
print(f"{'Label':<12} {'Observed':<12} {'Random Mean':<15} {'P-value':<10} {'Significant?'}")
print("-" * 70)

for label in top_labels:
    observed = observed_consistencies[label]
    random_mean = np.mean(random_consistencies[label])
    random_std = np.std(random_consistencies[label])
    
    # Calculate p-value (how many random >= observed?)
    p_value = sum(1 for r in random_consistencies[label] if r >= observed) / n_permutations
    
    significant = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""
    
    print(f"'{label}'      {observed*100:5.1f}%       {random_mean*100:5.1f}% ± {random_std*100:4.1f}%    {p_value:.4f}     {significant}")

# ============================================================================
# STEP 5: FREQUENCY CONTROL
# ============================================================================
print("\n" + "="*80)
print("STEP 5: FREQUENCY CONTROL")
print("="*80)

print("\nDo high-frequency labels just appear everywhere?")

# Compare top frequent labels vs rare labels
label_frequencies = Counter(zodiac_labels_list)
high_freq_labels = [label for label, count in label_frequencies.most_common(20)]
low_freq_labels = [label for label, count in label_frequencies.items() if 5 <= count <= 10]

print(f"\nHigh frequency (top 20): {high_freq_labels[:10]}")
print(f"Medium frequency (5-10): {low_freq_labels[:10]}")

# Count how many different positions each appears in
def position_diversity(label, label_position_list):
    """Count how many different position types a label appears in"""
    positions = set(pos for lbl, pos in label_position_list if lbl == label)
    return len(positions)

print("\nPosition diversity:")
print(f"{'Category':<20} {'Avg # Positions':<20} {'Avg Consistency'}")
print("-" * 60)

high_freq_diversity = [position_diversity(l, labels_with_position) for l in high_freq_labels]
high_freq_consistency = [position_consistency(l, labels_with_position) for l in high_freq_labels]

low_freq_diversity = [position_diversity(l, labels_with_position) for l in low_freq_labels[:20]]
low_freq_consistency = [position_consistency(l, labels_with_position) for l in low_freq_labels[:20]]

print(f"High frequency       {np.mean(high_freq_diversity):.2f}               {np.mean(high_freq_consistency)*100:.1f}%")
print(f"Medium frequency     {np.mean(low_freq_diversity):.2f}               {np.mean(low_freq_consistency)*100:.1f}%")

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*80)
print("FINAL VERDICT: ARE OUR PATTERNS REAL?")
print("="*80)

evidence = []

# Check baseline bigrams
if ot_ratio < 1.2:
    evidence.append("✗ 'ot-' enrichment is BASELINE EFFECT (not special to zodiac)")
else:
    evidence.append("✓ 'ot-' IS genuinely enriched in zodiac section")

# Check morphological clustering
if len(clusters) > 20:
    evidence.append("⚠ Many morphological clusters (patterns may be morphological)")
else:
    evidence.append("✓ Limited morphological clustering")

# Check permutation tests
significant_count = sum(1 for label in top_labels 
                       if sum(1 for r in random_consistencies[label] 
                             if r >= observed_consistencies[label]) < 50)
if significant_count >= 3:
    evidence.append("✓ Position consistency survives permutation test")
else:
    evidence.append("✗ Position consistency could be random")

# Check frequency control
if np.mean(high_freq_consistency) > np.mean(low_freq_consistency) + 0.2:
    evidence.append("⚠ High-frequency labels more consistent (frequency artifact?)")
else:
    evidence.append("✓ Consistency not driven by frequency alone")

print("\n" + "\n".join(evidence))

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("\nWe need these controls to distinguish:")
print("  REAL PATTERN vs ARTIFACT OF:")
print("    - Voynichese baseline phonotactics")
print("    - Morphological relatedness")
print("    - Random chance")
print("    - Frequency effects")
print("\nOnly patterns that survive ALL controls are meaningful.")
print("="*80)
