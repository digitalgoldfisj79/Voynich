#!/usr/bin/env python3
"""
REPLICATION TEST: CYCLICAL PATTERNS ACROSS ZODIAC SIGNS
========================================================

If Edward's cyclical structure hypothesis is correct, we should see:
- ~12 clusters in EACH zodiac sign
- Stem family reuse in EACH sign
- Spatial coherence in EACH sign
- Similar patterns across all constellations

If patterns only appear in pooled data, they're artifacts.
If they replicate across signs, they're systematic.
"""

import re
from collections import Counter, defaultdict
import numpy as np
from sklearn.cluster import KMeans

print("="*80)
print("REPLICATION TEST: PATTERNS ACROSS INDIVIDUAL ZODIAC SIGNS")
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

# Load labels by zodiac sign
with open('/home/claude/transliteration.txt', 'r') as f:
    lines = f.readlines()

# Map folios to zodiac signs
FOLIO_TO_SIGN = {
    'f67': 'Pisces',
    'f68': 'Aries/Taurus',  # Mixed
    'f69': 'Taurus',
    'f70': 'Gemini',
    'f71': 'Cancer',
    'f72': 'Leo',
    'f73': 'Virgo'
}

labels_by_sign = defaultdict(list)
current_folio = None

for i, line in enumerate(lines):
    match = re.search(r'<(f6[7-9]|f7[0-3])[rv]\d*\.(\d+)', line)
    if match and '@' in line:
        folio_base = match.group(1)
        line_number = int(match.group(2))
        
        if folio_base in FOLIO_TO_SIGN:
            sign = FOLIO_TO_SIGN[folio_base]
            
            text = re.sub(r'<[^>]+>', '', line)
            text = re.sub(r'@\d+;', '', text)
            text = re.sub(r'[{}+=]', '', text)
            tokens = re.findall(r'[a-z]+', text.lower())
            labels = [t for t in tokens if 3 <= len(t) <= 10]
            
            for label in labels:
                labels_by_sign[sign].append({
                    'label': label,
                    'line': line_number,
                    'prefix': label[:2] if len(label) >= 2 else '',
                    'suffix': label[-2:] if len(label) >= 2 else ''
                })

print("\n📊 LABELS BY ZODIAC SIGN")
print("-" * 80)
for sign in ['Pisces', 'Aries/Taurus', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo']:
    if sign in labels_by_sign:
        count = len(labels_by_sign[sign])
        unique = len(set([l['label'] for l in labels_by_sign[sign]]))
        print(f"{sign:<15} {count:4d} labels ({unique:3d} unique)")

# ============================================================================
# ANALYZE EACH SIGN SEPARATELY
# ============================================================================

results_by_sign = {}

for sign in ['Pisces', 'Aries/Taurus', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo']:
    if sign not in labels_by_sign or len(labels_by_sign[sign]) < 30:
        continue
    
    print("\n" + "="*80)
    print(f"ANALYZING: {sign.upper()}")
    print("="*80)
    
    sign_labels = labels_by_sign[sign]
    label_freq = Counter([l['label'] for l in sign_labels])
    
    # Get frequent labels (need at least n>=2 for individual signs)
    frequent_labels = [label for label, count in label_freq.items() if count >= 2]
    
    print(f"\nLabels: {len(sign_labels)} total, {len(frequent_labels)} frequent (n≥2)")
    
    if len(frequent_labels) < 12:
        print("⚠ Too few frequent labels for clustering")
        results_by_sign[sign] = None
        continue
    
    # TEST 1: Try clustering into k=12
    print(f"\n--- Test 1: Clustering into k=12 ---")
    
    n = len(frequent_labels)
    distance_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1, n):
            dist = edit_distance(frequent_labels[i], frequent_labels[j])
            distance_matrix[i, j] = dist
            distance_matrix[j, i] = dist
    
    max_dist = distance_matrix.max()
    similarity_matrix = max_dist - distance_matrix
    
    # Use fewer clusters if not enough labels
    k = min(12, len(frequent_labels) // 2)
    
    try:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(similarity_matrix)
        
        clusters_dict = defaultdict(list)
        for i, label in enumerate(frequent_labels):
            clusters_dict[clusters[i]].append(label)
        
        cluster_sizes = [len(clusters_dict[i]) for i in range(k)]
        avg_size = np.mean(cluster_sizes)
        std_size = np.std(cluster_sizes)
        
        print(f"Created {k} clusters: mean size {avg_size:.1f} ± {std_size:.1f}")
        
        # TEST 2: Stem family reuse
        print(f"\n--- Test 2: Stem Family Reuse ---")
        
        prefix_distribution = defaultdict(set)
        for cluster_id, labels_in_cluster in clusters_dict.items():
            for label in labels_in_cluster:
                prefix = label[:2] if len(label) >= 2 else ''
                prefix_distribution[prefix].add(cluster_id)
        
        reappearing_stems = [prefix for prefix, cluster_set in prefix_distribution.items() 
                            if len(cluster_set) >= 3]
        
        print(f"Stem families in 3+ clusters: {len(reappearing_stems)}")
        if reappearing_stems:
            for prefix in reappearing_stems[:5]:
                clusters_with_prefix = len(prefix_distribution[prefix])
                print(f"  '{prefix}': {clusters_with_prefix} clusters")
        
        # TEST 3: Suffix homogeneity
        print(f"\n--- Test 3: Suffix Homogeneity ---")
        
        suffix_entropies = []
        for i in range(k):
            labels_in_cluster = clusters_dict[i]
            suffixes = [l[-2:] for l in labels_in_cluster if len(l) >= 2]
            
            if len(suffixes) > 0:
                suffix_counts = Counter(suffixes)
                total = sum(suffix_counts.values())
                probs = [count/total for count in suffix_counts.values()]
                entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
                max_entropy = np.log2(len(suffix_counts)) if len(suffix_counts) > 1 else 0
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                suffix_entropies.append(normalized_entropy)
        
        avg_entropy = np.mean(suffix_entropies) if suffix_entropies else 1.0
        print(f"Average suffix entropy: {avg_entropy:.3f}")
        print(f"  (0=homogeneous, 1=diverse)")
        
        # TEST 4: Spatial coherence
        print(f"\n--- Test 4: Spatial Coherence ---")
        
        cluster_stds = []
        for cluster_id in range(k):
            labels_in_cluster = clusters_dict[cluster_id]
            line_positions = []
            for label_data in sign_labels:
                if label_data['label'] in labels_in_cluster and label_data['line'] is not None:
                    line_positions.append(label_data['line'])
            
            if len(line_positions) >= 3:
                cluster_stds.append(np.std(line_positions))
        
        avg_spatial_std = np.mean(cluster_stds) if cluster_stds else 0
        
        # Random baseline
        random_stds = []
        for _ in range(50):
            random_assignment = np.random.choice(k, size=len(sign_labels))
            for cluster_id in range(k):
                random_positions = [sign_labels[i]['line'] for i in range(len(sign_labels))
                                  if random_assignment[i] == cluster_id and sign_labels[i]['line'] is not None]
                if len(random_positions) >= 3:
                    random_stds.append(np.std(random_positions))
        
        random_avg_std = np.mean(random_stds) if random_stds else 0
        
        print(f"Spatial std dev: {avg_spatial_std:.1f} (random: {random_avg_std:.1f})")
        
        spatial_ratio = avg_spatial_std / random_avg_std if random_avg_std > 0 else 1.0
        
        # Store results
        results_by_sign[sign] = {
            'n_labels': len(sign_labels),
            'n_frequent': len(frequent_labels),
            'k_clusters': k,
            'avg_cluster_size': avg_size,
            'std_cluster_size': std_size,
            'n_reappearing_stems': len(reappearing_stems),
            'reappearing_stems': reappearing_stems,
            'avg_suffix_entropy': avg_entropy,
            'avg_spatial_std': avg_spatial_std,
            'random_spatial_std': random_avg_std,
            'spatial_ratio': spatial_ratio
        }
        
        print(f"\n✓ Analysis complete for {sign}")
        
    except Exception as e:
        print(f"✗ Clustering failed: {e}")
        results_by_sign[sign] = None

# ============================================================================
# CROSS-SIGN COMPARISON
# ============================================================================

print("\n" + "="*80)
print("CROSS-SIGN COMPARISON: DO PATTERNS REPLICATE?")
print("="*80)

valid_results = {sign: result for sign, result in results_by_sign.items() if result is not None}

if len(valid_results) >= 3:
    print(f"\nSuccessfully analyzed {len(valid_results)} zodiac signs")
    print("\n" + "-"*100)
    print(f"{'Sign':<15} {'N Labels':<10} {'Clusters':<10} {'Stem Reuse':<12} {'Suffix Ent':<12} {'Spatial':<10}")
    print("-"*100)
    
    for sign in ['Pisces', 'Aries/Taurus', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo']:
        if sign in valid_results:
            r = valid_results[sign]
            spatial_marker = "✓" if r['spatial_ratio'] < 0.95 else "✗"
            print(f"{sign:<15} {r['n_labels']:<10} {r['k_clusters']:<10} "
                  f"{r['n_reappearing_stems']:<12} {r['avg_suffix_entropy']:<12.3f} "
                  f"{spatial_marker:<10}")
    
    # Statistical summary
    print("\n" + "-"*100)
    print("STATISTICAL SUMMARY:")
    print("-"*100)
    
    # Stem reuse consistency
    stem_reuse_counts = [r['n_reappearing_stems'] for r in valid_results.values()]
    print(f"\nStem family reuse (3+ clusters):")
    print(f"  Mean: {np.mean(stem_reuse_counts):.1f}")
    print(f"  Range: {min(stem_reuse_counts)} to {max(stem_reuse_counts)}")
    print(f"  Present in: {sum(1 for x in stem_reuse_counts if x > 0)}/{len(stem_reuse_counts)} signs")
    
    # Suffix entropy consistency
    suffix_entropies = [r['avg_suffix_entropy'] for r in valid_results.values()]
    print(f"\nSuffix homogeneity (entropy):")
    print(f"  Mean: {np.mean(suffix_entropies):.3f}")
    print(f"  Range: {min(suffix_entropies):.3f} to {max(suffix_entropies):.3f}")
    print(f"  Homogeneous (<0.5) in: {sum(1 for x in suffix_entropies if x < 0.5)}/{len(suffix_entropies)} signs")
    
    # Spatial coherence consistency
    spatial_ratios = [r['spatial_ratio'] for r in valid_results.values()]
    print(f"\nSpatial coherence (vs random):")
    print(f"  Mean ratio: {np.mean(spatial_ratios):.3f}")
    print(f"  Range: {min(spatial_ratios):.3f} to {max(spatial_ratios):.3f}")
    print(f"  Coherent (<0.95) in: {sum(1 for x in spatial_ratios if x < 0.95)}/{len(spatial_ratios)} signs")
    
    # VERDICT
    print("\n" + "="*80)
    print("REPLICATION VERDICT")
    print("="*80)
    
    evidence_points = 0
    
    # Do patterns appear in MOST signs?
    stem_replication = sum(1 for x in stem_reuse_counts if x > 0) / len(stem_reuse_counts)
    spatial_replication = sum(1 for x in spatial_ratios if x < 0.95) / len(spatial_ratios)
    
    print(f"\nPattern replication across signs:")
    print(f"  Stem reuse: {stem_replication*100:.0f}% of signs")
    print(f"  Spatial coherence: {spatial_replication*100:.0f}% of signs")
    
    if stem_replication >= 0.7:
        print("\n✓✓ STRONG REPLICATION: Stem families appear in most signs")
        evidence_points += 2
    elif stem_replication >= 0.5:
        print("\n○ MODERATE REPLICATION: Stem families appear in some signs")
        evidence_points += 1
    else:
        print("\n✗ WEAK REPLICATION: Stem families rare or inconsistent")
    
    if spatial_replication >= 0.7:
        print("✓✓ STRONG REPLICATION: Spatial clustering in most signs")
        evidence_points += 2
    elif spatial_replication >= 0.5:
        print("○ MODERATE REPLICATION: Spatial clustering in some signs")
        evidence_points += 1
    else:
        print("✗ WEAK REPLICATION: No consistent spatial clustering")
    
    # Check if stem families are THE SAME across signs
    print(f"\n--- Common Stem Families ---")
    all_stems = defaultdict(int)
    for sign, result in valid_results.items():
        for stem in result['reappearing_stems']:
            all_stems[stem] += 1
    
    universal_stems = [stem for stem, count in all_stems.items() if count >= len(valid_results)*0.6]
    
    print(f"\nStems appearing in 60%+ of signs:")
    for stem in sorted(universal_stems):
        sign_count = all_stems[stem]
        print(f"  '{stem}': {sign_count}/{len(valid_results)} signs")
    
    if universal_stems:
        print(f"\n✓✓ FOUND {len(universal_stems)} UNIVERSAL STEM FAMILIES")
        print("These stems appear consistently across zodiac signs!")
        evidence_points += 2
    else:
        print("\n✗ No universal stem families found")
    
    print("\n" + "="*80)
    print(f"TOTAL REPLICATION EVIDENCE: {evidence_points}/6")
    print("="*80)
    
    if evidence_points >= 5:
        print("\n✓✓✓ STRONG REPLICATION across zodiac signs")
        print("Patterns are SYSTEMATIC, not artifacts of pooling data")
    elif evidence_points >= 3:
        print("\n○○ MODERATE REPLICATION across signs")
        print("Some patterns consistent, others variable")
    else:
        print("\n✗ WEAK REPLICATION across signs")
        print("Patterns may be artifacts or sign-specific")

else:
    print("\n✗ Insufficient data for cross-sign comparison")

print("\n" + "="*80)
