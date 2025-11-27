#!/usr/bin/env python3
"""
SM2: SEMANTIC MAPPING USING VPCA STEM AXES
===========================================

Use Edward's stem_axis_features to:
1. Map zodiac stems to semantic space
2. Cluster stems by semantic similarity
3. Identify semantic fields
4. Assign meanings to morpheme clusters
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from sklearn.cluster import KMeans, DBSCAN
from scipy.spatial.distance import pdist, squareform, euclidean
import matplotlib.pyplot as plt
import re

print("="*80)
print("SM2: SEMANTIC MAPPING USING VPCA STEM AXES")
print("="*80)

# ============================================================================
# LOAD VPCA STEM AXES
# ============================================================================

stem_axes = pd.read_csv('/mnt/user-data/uploads/stem_axis_features.tsv', sep='\t')
print(f"\n📁 Loaded {len(stem_axes)} stem-section mappings")

# Filter to Astronomical
astro_stems = stem_axes[stem_axes['section'] == 'Astronomical'].copy()
print(f"📁 Found {len(astro_stems)} astronomical stem embeddings")

# Remove zero vectors (stems not in astronomical)
astro_stems = astro_stems[(astro_stems['axis1'] != 0) | (astro_stems['axis2'] != 0)]
print(f"📁 {len(astro_stems)} non-zero astronomical stems")

print(f"\nTop 20 stems by axis values:")
print(astro_stems.head(20)[['stem', 'axis1', 'axis2']])

# ============================================================================
# LOAD OUR ZODIAC DATA
# ============================================================================

print(f"\n" + "="*80)
print("LOADING ZODIAC DATA")
print("="*80)

with open('/home/claude/transliteration.txt', 'r') as f:
    lines = f.readlines()

zodiac_data = []

for line in lines:
    match = re.search(r'<(f6[7-9]|f7[0-5])[rv]\d*\.(\d+)', line)
    if match and '@' in line:
        folio = match.group(1)
        text = re.sub(r'<[^>]+>', '', line)
        text = re.sub(r'@\d+;', '', text)
        text = re.sub(r'[{}+=]', '', text)
        tokens = re.findall(r'[a-z]+', text.lower())
        labels = [t for t in tokens if 3 <= len(t) <= 10]
        zodiac_data.extend(labels)

print(f"Loaded {len(zodiac_data)} zodiac labels")

# ============================================================================
# MATCH ZODIAC LABELS TO STEM AXES
# ============================================================================

print(f"\n" + "="*80)
print("MATCHING ZODIAC LABELS TO VPCA STEMS")
print("="*80)

# Build stem lookup
stem_coords = {}
for _, row in astro_stems.iterrows():
    stem_coords[row['stem']] = (row['axis1'], row['axis2'])

# Check zodiac label coverage
label_freq = Counter(zodiac_data)
matched_labels = []
unmatched_labels = []

for label, count in label_freq.items():
    if label in stem_coords:
        matched_labels.append((label, count, stem_coords[label]))
    else:
        # Try substring matching
        found = False
        for stem in stem_coords:
            if stem in label or label in stem:
                matched_labels.append((label, count, stem_coords[stem]))
                found = True
                break
        if not found:
            unmatched_labels.append((label, count))

print(f"\nDirect matches: {len(matched_labels)}")
print(f"Unmatched: {len(unmatched_labels)}")

coverage = sum(c for l, c, coords in matched_labels) / len(zodiac_data) * 100
print(f"Coverage: {coverage:.1f}% of zodiac tokens")

# ============================================================================
# SEMANTIC SPACE VISUALIZATION
# ============================================================================

print(f"\n" + "="*80)
print("VISUALIZING SEMANTIC SPACE")
print("="*80)

# Get all astronomical stems for context
all_stems = astro_stems[['stem', 'axis1', 'axis2']].values

# Highlight zodiac stems
zodiac_stems_in_space = []
for label, count, (x, y) in matched_labels[:50]:  # Top 50
    zodiac_stems_in_space.append((label, x, y, count))

print(f"\nSemantic space statistics:")
print(f"  Axis1 range: [{astro_stems['axis1'].min():.3f}, {astro_stems['axis1'].max():.3f}]")
print(f"  Axis2 range: [{astro_stems['axis2'].min():.3f}, {astro_stems['axis2'].max():.3f}]")

# ============================================================================
# CLUSTER STEMS IN SEMANTIC SPACE
# ============================================================================

print(f"\n" + "="*80)
print("CLUSTERING STEMS BY SEMANTIC SIMILARITY")
print("="*80)

# Cluster astronomical stems
X = astro_stems[['axis1', 'axis2']].values

# Try k-means with different k
best_k = 8  # Start with 8 semantic fields

kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
astro_stems['cluster'] = kmeans.fit_predict(X)

print(f"\nClustered {len(astro_stems)} stems into {best_k} semantic fields")

# Analyze clusters
for cluster_id in range(best_k):
    cluster_stems = astro_stems[astro_stems['cluster'] == cluster_id]
    
    # Get cluster centroid
    centroid = kmeans.cluster_centers_[cluster_id]
    
    # Find zodiac labels in this cluster
    zodiac_in_cluster = []
    for label, count, (x, y) in matched_labels:
        # Find nearest cluster
        distances = [euclidean([x, y], c) for c in kmeans.cluster_centers_]
        nearest = np.argmin(distances)
        if nearest == cluster_id:
            zodiac_in_cluster.append((label, count))
    
    print(f"\n--- Cluster {cluster_id+1} (center: [{centroid[0]:.3f}, {centroid[1]:.3f}]) ---")
    print(f"  Size: {len(cluster_stems)} stems")
    print(f"  Zodiac labels: {len(zodiac_in_cluster)}")
    
    if cluster_stems.shape[0] > 0:
        # Show sample stems
        sample_stems = cluster_stems['stem'].head(10).tolist()
        print(f"  Sample stems: {', '.join(sample_stems)}")
    
    if zodiac_in_cluster:
        # Show top zodiac labels
        top_zodiac = sorted(zodiac_in_cluster, key=lambda x: x[1], reverse=True)[:5]
        print(f"  Top zodiac: {', '.join([f'{l}({c})' for l, c in top_zodiac])}")

# ============================================================================
# SEMANTIC FIELD CHARACTERIZATION
# ============================================================================

print(f"\n" + "="*80)
print("CHARACTERIZING SEMANTIC FIELDS")
print("="*80)

# Analyze cluster positions in semantic space
cluster_characteristics = []

for cluster_id in range(best_k):
    cluster_stems = astro_stems[astro_stems['cluster'] == cluster_id]
    
    centroid = kmeans.cluster_centers_[cluster_id]
    axis1_mean = centroid[0]
    axis2_mean = centroid[1]
    
    # Characterize by axis position
    axis1_char = "positive" if axis1_mean > 0 else "negative"
    axis2_char = "positive" if axis2_mean > 0 else "negative"
    
    # Distance from origin (semantic specificity)
    distance_from_origin = np.sqrt(axis1_mean**2 + axis2_mean**2)
    
    cluster_characteristics.append({
        'cluster': cluster_id,
        'centroid': centroid,
        'axis1': axis1_char,
        'axis2': axis2_char,
        'distance': distance_from_origin,
        'size': len(cluster_stems)
    })

print(f"\n{'Cluster':<10} {'Axis1':<12} {'Axis2':<12} {'Distance':<12} {'Size':<8} {'Semantic Field (hypothesis)'}")
print("-" * 90)

# Hypothesize semantic fields based on axes
semantic_hypotheses = {
    ('+', '+'): "Process/Active",
    ('+', '-'): "Quality/State",
    ('-', '+'): "Entity/Object",
    ('-', '-'): "Modifier/Relation"
}

for char in sorted(cluster_characteristics, key=lambda x: x['distance'], reverse=True):
    axis1_sign = '+' if char['axis1'] == 'positive' else '-'
    axis2_sign = '+' if char['axis2'] == 'positive' else '-'
    
    hypothesis = semantic_hypotheses.get((axis1_sign, axis2_sign), "Unknown")
    
    print(f"{char['cluster']+1:<10} {char['axis1']:<12} {char['axis2']:<12} "
          f"{char['distance']:<12.3f} {char['size']:<8} {hypothesis}")

# ============================================================================
# MAP ZODIAC ROOTS TO SEMANTIC FIELDS
# ============================================================================

print(f"\n" + "="*80)
print("MAPPING ZODIAC ROOTS TO SEMANTIC FIELDS")
print("="*80)

# Decompose zodiac labels and map roots
from collections import Counter

KNOWN_PREFIXES = ['ch', 'ot', 'ok', 'sh', 'qo', 'da', 'yk', 'ol', 'sa', 'op', 'do']
KNOWN_SUFFIXES = ['ot', 'ok', 'ch', 'ar', 'al', 'or', 'ol', 'ey', 'oy', 'ay', 
                  'ed', 'od', 'dy', 'ry', 'in', 'yn', 'an', 'es', 'os', 'ys']

def extract_root(label):
    """Extract root from label"""
    root = label
    
    # Remove prefix
    for prefix in KNOWN_PREFIXES:
        if label.startswith(prefix):
            root = label[len(prefix):]
            break
    
    # Remove suffix
    for suffix in KNOWN_SUFFIXES:
        if len(root) >= 3 and root.endswith(suffix):
            root = root[:-len(suffix)]
            break
    
    return root if root else None

# Extract roots and map to clusters
root_clusters = defaultdict(list)

for label, count, (x, y) in matched_labels:
    root = extract_root(label)
    if root and len(root) >= 1:
        # Find cluster
        distances = [euclidean([x, y], c) for c in kmeans.cluster_centers_]
        cluster_id = np.argmin(distances)
        root_clusters[root].append((cluster_id, count))

print(f"\nMapped {len(root_clusters)} unique roots to semantic fields")

print(f"\nTop 20 roots by frequency:")
root_total_freq = {root: sum(c for _, c in occurrences) 
                   for root, occurrences in root_clusters.items()}

for root, total_freq in sorted(root_total_freq.items(), key=lambda x: x[1], reverse=True)[:20]:
    # Find dominant cluster
    cluster_counts = Counter([c for c, count in root_clusters[root] for _ in range(count)])
    dominant_cluster = cluster_counts.most_common(1)[0][0]
    
    # Get semantic hypothesis
    char = cluster_characteristics[dominant_cluster]
    axis1_sign = '+' if char['axis1'] == 'positive' else '-'
    axis2_sign = '+' if char['axis2'] == 'positive' else '-'
    hypothesis = semantic_hypotheses.get((axis1_sign, axis2_sign), "Unknown")
    
    print(f"  '{root}' ({total_freq}×): Cluster {dominant_cluster+1} → {hypothesis}")

# ============================================================================
# VISUAL SUMMARY
# ============================================================================

print(f"\n" + "="*80)
print("GENERATING VISUAL SUMMARY")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Semantic space with clusters
ax1 = axes[0, 0]
colors = plt.cm.tab10(np.linspace(0, 1, best_k))

for cluster_id in range(best_k):
    cluster_stems = astro_stems[astro_stems['cluster'] == cluster_id]
    ax1.scatter(cluster_stems['axis1'], cluster_stems['axis2'], 
                c=[colors[cluster_id]], alpha=0.5, s=50, label=f'C{cluster_id+1}')

# Mark centroids
for i, centroid in enumerate(kmeans.cluster_centers_):
    ax1.scatter(centroid[0], centroid[1], c='red', marker='X', s=200, 
                edgecolors='black', linewidths=2)

ax1.set_xlabel('Axis 1')
ax1.set_ylabel('Axis 2')
ax1.set_title('Semantic Space: Astronomical Stems')
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax1.axhline(0, color='gray', linestyle='--', alpha=0.3)
ax1.axvline(0, color='gray', linestyle='--', alpha=0.3)
ax1.grid(True, alpha=0.3)

# Plot 2: Cluster sizes
ax2 = axes[0, 1]
cluster_sizes = [len(astro_stems[astro_stems['cluster'] == i]) for i in range(best_k)]
ax2.bar(range(1, best_k+1), cluster_sizes, color=colors, alpha=0.7)
ax2.set_xlabel('Cluster')
ax2.set_ylabel('Number of Stems')
ax2.set_title('Semantic Field Sizes')

# Plot 3: Zodiac coverage by cluster
ax3 = axes[1, 0]
zodiac_by_cluster = [0] * best_k

for label, count, (x, y) in matched_labels:
    distances = [euclidean([x, y], c) for c in kmeans.cluster_centers_]
    cluster_id = np.argmin(distances)
    zodiac_by_cluster[cluster_id] += count

ax3.bar(range(1, best_k+1), zodiac_by_cluster, color=colors, alpha=0.7)
ax3.set_xlabel('Cluster')
ax3.set_ylabel('Zodiac Token Count')
ax3.set_title('Zodiac Distribution by Semantic Field')

# Plot 4: Semantic field quadrants
ax4 = axes[1, 1]
for cluster_id in range(best_k):
    centroid = kmeans.cluster_centers_[cluster_id]
    size = cluster_sizes[cluster_id]
    ax4.scatter(centroid[0], centroid[1], s=size*20, c=[colors[cluster_id]], 
                alpha=0.6, edgecolors='black', linewidths=1)
    ax4.text(centroid[0], centroid[1], f'C{cluster_id+1}', 
            ha='center', va='center', fontweight='bold', fontsize=8)

ax4.axhline(0, color='black', linestyle='-', alpha=0.5)
ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
ax4.set_xlabel('Axis 1 (Process ← → Quality)')
ax4.set_ylabel('Axis 2 (Entity ← → Modifier)')
ax4.set_title('Semantic Field Quadrants')
ax4.text(0.8, 0.8, 'Process/Active', transform=ax4.transAxes, ha='center')
ax4.text(0.8, 0.2, 'Quality/State', transform=ax4.transAxes, ha='center')
ax4.text(0.2, 0.8, 'Entity/Object', transform=ax4.transAxes, ha='center')
ax4.text(0.2, 0.2, 'Modifier/Relation', transform=ax4.transAxes, ha='center')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sm2_semantic_space.png', dpi=300, bbox_inches='tight')
print("Visual saved!")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"\n" + "="*80)
print("SM2 SEMANTIC MAPPING COMPLETE")
print("="*80)

print(f"\n📊 Coverage:")
print(f"  • VPCA stems mapped: {len(astro_stems)}")
print(f"  • Zodiac labels matched: {len(matched_labels)}")
print(f"  • Coverage: {coverage:.1f}%")

print(f"\n🎯 Semantic Fields Identified:")
print(f"  • Total clusters: {best_k}")
print(f"  • Roots mapped: {len(root_clusters)}")

print(f"\n💡 Semantic Hypotheses:")
for quadrant, meaning in semantic_hypotheses.items():
    print(f"  • {quadrant}: {meaning}")

print(f"\n✓ SM2 framework built on VPCA stem axes")
print(f"\n" + "="*80)
