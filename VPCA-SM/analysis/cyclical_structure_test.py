#!/usr/bin/env python3
"""
CYCLICAL STRUCTURE TEST
========================

Edward's hypothesis: If f68r3 is a 12-phase cycle (medieval model),
we should see:

1. Clusters of ~12-15 items that behave like micro-cycles
2. Suffix homogeneity within clusters (morphological coherence)
3. Stem families reappearing across cycles
4. Internal adjacency structure (spatial clustering)
5. Cyclic edit-distance similarity (same phases are similar)

This distinguishes RANDOM NOISE from SYSTEMATIC CYCLICAL ENCODING.
"""

import re
from collections import Counter, defaultdict
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt

print("="*80)
print("12-FOLD CYCLICAL STRUCTURE TEST")
print("="*80)

def edit_distance(s1, s2):
    """Levenshtein distance"""
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

# Load ALL zodiac labels with folio and line positions
with open('/home/claude/transliteration.txt', 'r') as f:
    lines = f.readlines()

f68r3_labels = []  # Keep variable name for compatibility but use all zodiac
current_folio = None

# Zodiac folios: f67-f73
for i, line in enumerate(lines):
    # Check if this is a zodiac folio line
    match = re.search(r'<(f6[7-9]|f7[0-3])[rv]\d*\.(\d+)', line)
    if match and '@' in line:
        current_folio = match.group(1)
        line_number = int(match.group(2))
        
        # Extract labels with line position
        text = re.sub(r'<[^>]+>', '', line)
        text = re.sub(r'@\d+;', '', text)
        text = re.sub(r'[{}]', '', text)  # Remove curly braces
        text = re.sub(r'[+=]', '', text)  # Remove special markers
        tokens = re.findall(r'[a-z]+', text.lower())
        labels = [t for t in tokens if 3 <= len(t) <= 10]
        
        for label in labels:
            f68r3_labels.append({
                'label': label,
                'folio': current_folio,
                'line': line_number,
                'prefix': label[:2] if len(label) >= 2 else '',
                'suffix': label[-2:] if len(label) >= 2 else '',
                'length': len(label)
            })

print(f"\n📊 ZODIAC FOLIOS DATA")
print("-" * 80)
print(f"Total labels in zodiac folios: {len(f68r3_labels)}")
print(f"Labels with position info: {len([l for l in f68r3_labels if l['line'] is not None])}")

# Count by folio
folio_counts = {}
for item in f68r3_labels:
    folio = item.get('folio', 'unknown')
    folio_counts[folio] = folio_counts.get(folio, 0) + 1

print(f"\nLabels by folio:")
for folio in sorted(folio_counts.keys()):
    print(f"  {folio}: {folio_counts[folio]}")

# ============================================================================
# TEST 1: CLUSTER INTO ~12 GROUPS
# ============================================================================
print("\n" + "="*80)
print("TEST 1: CLUSTERING INTO ~12 MICRO-CYCLES")
print("="*80)

# Create edit distance matrix for frequent labels
label_freq = Counter([l['label'] for l in f68r3_labels])
frequent_labels = [label for label, count in label_freq.items() if count >= 3]

print(f"\nUsing {len(frequent_labels)} frequent labels (n≥3) for clustering")

# Compute pairwise edit distances
n = len(frequent_labels)
distance_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(i+1, n):
        dist = edit_distance(frequent_labels[i], frequent_labels[j])
        distance_matrix[i, j] = dist
        distance_matrix[j, i] = dist

# Try clustering into k=12 groups
print("\nClustering into k=12 groups (KMeans on edit distance)...")

# Convert distance to similarity for KMeans
max_dist = distance_matrix.max()
similarity_matrix = max_dist - distance_matrix

kmeans = KMeans(n_clusters=12, random_state=42, n_init=10)
clusters = kmeans.fit_predict(similarity_matrix)

# Organize by cluster
clusters_dict = defaultdict(list)
for i, label in enumerate(frequent_labels):
    clusters_dict[clusters[i]].append(label)

print(f"\nCluster sizes:")
cluster_sizes = [len(clusters_dict[i]) for i in range(12)]
print(f"  Mean: {np.mean(cluster_sizes):.1f} ± {np.std(cluster_sizes):.1f}")
print(f"  Range: {min(cluster_sizes)} to {max(cluster_sizes)}")

# Show clusters
print(f"\nCluster composition (showing first 8 labels each):")
for i in range(12):
    labels_in_cluster = clusters_dict[i]
    print(f"  Cluster {i+1:2d} ({len(labels_in_cluster):2d} labels): {labels_in_cluster[:8]}")

# ============================================================================
# TEST 2: SUFFIX HOMOGENEITY WITHIN CLUSTERS
# ============================================================================
print("\n" + "="*80)
print("TEST 2: SUFFIX HOMOGENEITY WITHIN CLUSTERS")
print("="*80)

print("\nMeasuring suffix diversity within each cluster...")

suffix_homogeneity = []
for i in range(12):
    labels_in_cluster = clusters_dict[i]
    suffixes = [l[-2:] for l in labels_in_cluster if len(l) >= 2]
    
    if len(suffixes) > 0:
        suffix_counts = Counter(suffixes)
        # Calculate entropy (low = homogeneous)
        total = sum(suffix_counts.values())
        probs = [count/total for count in suffix_counts.values()]
        entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
        
        # Normalized entropy (0 = all same, 1 = all different)
        max_entropy = np.log2(len(suffix_counts)) if len(suffix_counts) > 1 else 0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        most_common_suffix, most_common_count = suffix_counts.most_common(1)[0]
        suffix_pct = most_common_count / len(suffixes) * 100
        
        suffix_homogeneity.append({
            'cluster': i,
            'entropy': normalized_entropy,
            'dominant_suffix': most_common_suffix,
            'dominant_pct': suffix_pct,
            'unique_suffixes': len(suffix_counts)
        })

print(f"\n{'Cluster':<10} {'Dominant Suffix':<18} {'% Dominant':<12} {'Entropy':<10} {'# Unique'}")
print("-" * 75)

for item in suffix_homogeneity:
    print(f"{item['cluster']+1:2d}         '-{item['dominant_suffix']}'             "
          f"{item['dominant_pct']:5.1f}%        {item['entropy']:5.2f}      {item['unique_suffixes']:2d}")

avg_entropy = np.mean([item['entropy'] for item in suffix_homogeneity])
print(f"\nAverage normalized entropy: {avg_entropy:.3f}")
print(f"(0 = perfect homogeneity, 1 = maximum diversity)")

if avg_entropy < 0.5:
    print("✓ Clusters show STRONG suffix homogeneity")
elif avg_entropy < 0.7:
    print("○ Clusters show MODERATE suffix homogeneity")
else:
    print("✗ Clusters show WEAK suffix homogeneity")

# ============================================================================
# TEST 3: STEM FAMILIES REAPPEARING
# ============================================================================
print("\n" + "="*80)
print("TEST 3: STEM FAMILIES REAPPEARING ACROSS CLUSTERS")
print("="*80)

# Count how many clusters each prefix appears in
prefix_distribution = defaultdict(set)

for cluster_id, labels_in_cluster in clusters_dict.items():
    for label in labels_in_cluster:
        prefix = label[:2] if len(label) >= 2 else ''
        prefix_distribution[prefix].add(cluster_id)

# Find "stem families" that appear in multiple clusters
print("\nPrefixes appearing in multiple clusters:")
print(f"{'Prefix':<10} {'# Clusters':<15} {'Clusters'}")
print("-" * 60)

reappearing_stems = []
for prefix, cluster_set in sorted(prefix_distribution.items(), 
                                 key=lambda x: len(x[1]), reverse=True):
    if len(cluster_set) >= 3:
        reappearing_stems.append(prefix)
        print(f"'{prefix}'      {len(cluster_set):2d}             {sorted(cluster_set)}")

print(f"\nFound {len(reappearing_stems)} stem families appearing in 3+ clusters")

if len(reappearing_stems) >= 5:
    print("✓ STRONG evidence of stem reuse across cycles")
elif len(reappearing_stems) >= 3:
    print("○ MODERATE evidence of stem reuse")
else:
    print("✗ WEAK evidence of stem reuse")

# ============================================================================
# TEST 4: SPATIAL ADJACENCY
# ============================================================================
print("\n" + "="*80)
print("TEST 4: SPATIAL ADJACENCY WITHIN CLUSTERS")
print("="*80)

print("\nTesting if labels in same cluster appear near each other...")

# For each cluster, calculate spatial coherence
cluster_coherence = []

for cluster_id in range(12):
    labels_in_cluster = clusters_dict[cluster_id]
    
    # Get line positions for these labels
    line_positions = []
    for label_data in f68r3_labels:
        if label_data['label'] in labels_in_cluster and label_data['line'] is not None:
            line_positions.append(label_data['line'])
    
    if len(line_positions) >= 3:
        # Calculate spatial spread
        positions_array = np.array(line_positions)
        spatial_range = positions_array.max() - positions_array.min()
        spatial_std = positions_array.std()
        
        cluster_coherence.append({
            'cluster': cluster_id,
            'n_labels': len(line_positions),
            'range': spatial_range,
            'std': spatial_std,
            'positions': line_positions[:10]
        })

print(f"\n{'Cluster':<10} {'N Labels':<12} {'Line Range':<15} {'Std Dev'}")
print("-" * 60)

for item in cluster_coherence:
    print(f"{item['cluster']+1:2d}         {item['n_labels']:3d}         "
          f"{item['range']:6.1f}          {item['std']:6.1f}")

avg_std = np.mean([item['std'] for item in cluster_coherence])
print(f"\nAverage spatial std dev: {avg_std:.1f} lines")

# Compare to random assignment
print("\nComparing to random assignment...")
random_stds = []
for _ in range(100):
    random_assignment = np.random.choice(12, size=len(f68r3_labels))
    for cluster_id in range(12):
        random_positions = [f68r3_labels[i]['line'] for i in range(len(f68r3_labels)) 
                          if random_assignment[i] == cluster_id and f68r3_labels[i]['line'] is not None]
        if len(random_positions) >= 3:
            random_stds.append(np.std(random_positions))

random_avg_std = np.mean(random_stds)
print(f"Random average std dev: {random_avg_std:.1f} lines")

if avg_std < random_avg_std * 0.8:
    print("✓ Clusters show STRONG spatial coherence")
elif avg_std < random_avg_std * 0.95:
    print("○ Clusters show MODERATE spatial coherence")
else:
    print("✗ Clusters do NOT show spatial coherence")

# ============================================================================
# TEST 5: CYCLIC EDIT-DISTANCE SIMILARITY
# ============================================================================
print("\n" + "="*80)
print("TEST 5: CYCLIC EDIT-DISTANCE SIMILARITY")
print("="*80)

print("\nTesting if similar phases across cycles are morphologically similar...")

# For each cluster, get representative labels
cluster_representatives = {}
for cluster_id in range(12):
    labels_in_cluster = clusters_dict[cluster_id]
    # Use most frequent as representative
    cluster_label_counts = Counter([l['label'] for l in f68r3_labels 
                                   if l['label'] in labels_in_cluster])
    if cluster_label_counts:
        representative = cluster_label_counts.most_common(1)[0][0]
        cluster_representatives[cluster_id] = representative

print(f"\nCluster representatives:")
for i in range(12):
    if i in cluster_representatives:
        print(f"  Phase {i+1:2d}: '{cluster_representatives[i]}'")

# Calculate inter-cluster distances
print(f"\nInter-cluster edit distances (showing phases 1-6):")
print("    ", end="")
for j in range(1, 7):
    print(f"{j:4d}", end="")
print()

inter_cluster_distances = []
for i in range(6):
    print(f"  {i+1:2d}", end="")
    for j in range(6):
        if i in cluster_representatives and j in cluster_representatives:
            dist = edit_distance(cluster_representatives[i], cluster_representatives[j])
            inter_cluster_distances.append(dist)
            print(f"{dist:4d}", end="")
        else:
            print(f"   -", end="")
    print()

avg_inter_cluster_dist = np.mean(inter_cluster_distances)
print(f"\nAverage inter-cluster distance: {avg_inter_cluster_dist:.2f}")

# Compare opposite phases (should they be similar in a cycle?)
print(f"\nOpposite phase similarity (if 12-fold cycle, opposite = 6 apart):")
opposite_pairs = [(i, (i+6)%12) for i in range(6)]
opposite_distances = []

for i, j in opposite_pairs:
    if i in cluster_representatives and j in cluster_representatives:
        dist = edit_distance(cluster_representatives[i], cluster_representatives[j])
        opposite_distances.append(dist)
        print(f"  Phase {i+1:2d} ↔ Phase {j+1:2d}: distance {dist}")

if opposite_distances:
    avg_opposite_dist = np.mean(opposite_distances)
    print(f"\nAverage opposite-phase distance: {avg_opposite_dist:.2f}")
    
    if avg_opposite_dist < avg_inter_cluster_dist * 0.9:
        print("○ Opposite phases show some similarity (weak cyclic pattern)")
    else:
        print("✗ No special opposite-phase similarity")

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*80)
print("FINAL VERDICT: IS THERE A 12-FOLD CYCLICAL STRUCTURE?")
print("="*80)

evidence_score = 0
max_score = 5

# Test 1: Cluster sizes reasonable
if 8 <= np.mean(cluster_sizes) <= 16:
    print("✓ Cluster sizes consistent with 12-fold division")
    evidence_score += 1
else:
    print("✗ Cluster sizes inconsistent")

# Test 2: Suffix homogeneity
if avg_entropy < 0.5:
    print("✓ Strong suffix homogeneity within clusters")
    evidence_score += 1
elif avg_entropy < 0.7:
    print("○ Moderate suffix homogeneity")
    evidence_score += 0.5
else:
    print("✗ Weak suffix homogeneity")

# Test 3: Stem reuse
if len(reappearing_stems) >= 5:
    print("✓ Strong stem family reuse across clusters")
    evidence_score += 1
elif len(reappearing_stems) >= 3:
    print("○ Moderate stem reuse")
    evidence_score += 0.5
else:
    print("✗ Weak stem reuse")

# Test 4: Spatial coherence
if avg_std < random_avg_std * 0.8:
    print("✓ Strong spatial clustering")
    evidence_score += 1
elif avg_std < random_avg_std * 0.95:
    print("○ Moderate spatial clustering")
    evidence_score += 0.5
else:
    print("✗ No spatial clustering")

# Test 5: Cyclic similarity
if opposite_distances and avg_opposite_dist < avg_inter_cluster_dist * 0.9:
    print("○ Weak cyclic edit-distance pattern")
    evidence_score += 0.5
else:
    print("✗ No cyclic similarity pattern")

print(f"\n" + "="*80)
print(f"TOTAL EVIDENCE SCORE: {evidence_score:.1f} / {max_score}")
print("="*80)

if evidence_score >= 4:
    print("\n✓✓✓ STRONG EVIDENCE for 12-fold cyclical structure")
    print("The data support Edward's hypothesis of medieval-style")
    print("nested cyclical encoding with morphological coherence.")
elif evidence_score >= 2.5:
    print("\n○ MODERATE EVIDENCE for cyclical structure")
    print("Some patterns present but not all tests positive.")
    print("May be partial cyclical encoding or different organization.")
else:
    print("\n✗ WEAK EVIDENCE for 12-fold cyclical structure")
    print("Clustering appears more random than systematic.")

print("\n" + "="*80)
