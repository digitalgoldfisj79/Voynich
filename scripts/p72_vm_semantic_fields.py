#!/usr/bin/env python3
"""
p72_vm_semantic_fields.py

Cluster Voynich stems into K data-driven "fields" based on structural vectors
from:
  Phase71/out/p71_vm_structural_vectors.tsv

This is a *purely structural clustering* using features:
  left_frac, right_frac, mean_axis_diff, mean_rule_hits, log_count

Inputs:
  - Phase71/out/p71_vm_structural_vectors.tsv

Outputs:
  - Phase72/out/p72_vm_semantic_fields.tsv
      token, count, cluster_id, left_frac, right_frac, unknown_frac,
      mean_axis_diff, mean_rule_hits, log_count, dist_to_center

  - Phase72/out/p72_vm_semantic_field_summary.tsv
      cluster_id, n_stems, total_count, mean_left_frac, mean_right_frac,
      mean_unknown_frac, mean_axis_diff, mean_rule_hits, mean_log_count
"""

import os
import sys
import csv
import math
from collections import defaultdict

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")

P71_PATH      = os.path.join(BASE, "Phase71", "out", "p71_vm_structural_vectors.tsv")
OUT_DIR       = os.path.join(BASE, "Phase72", "out")
FIELDS_PATH   = os.path.join(OUT_DIR, "p72_vm_semantic_fields.tsv")
SUMMARY_PATH  = os.path.join(OUT_DIR, "p72_vm_semantic_field_summary.tsv")

# Hyperparameters (can tweak here)
MIN_COUNT = 20   # minimum token frequency to include in clustering
K_CLUSTERS = 5   # number of clusters
MAX_ITERS  = 50  # max k-means iterations


def load_structural_vectors(path):
    if not os.path.exists(path):
        print(f"[ERROR] Structural vector file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            print(f"[ERROR] Empty file: {path}", file=sys.stderr)
            sys.exit(1)

        col_idx = {name: i for i, name in enumerate(header)}
        required = [
            "token", "count",
            "left_frac", "right_frac", "unknown_frac",
            "mean_rule_hits", "mean_axis_diff",
        ]
        for col in required:
            if col not in col_idx:
                print(f"[ERROR] Missing column '{col}' in {path}", file=sys.stderr)
                print(f"        Header was: {header}", file=sys.stderr)
                sys.exit(1)

        rows = []
        total = 0
        included = 0
        for row in reader:
            if not row:
                continue
            total += 1
            token = row[col_idx["token"]]
            try:
                count = int(row[col_idx["count"]])
            except ValueError:
                continue

            if count < MIN_COUNT:
                continue  # skip low-frequency stems

            try:
                left_frac    = float(row[col_idx["left_frac"]])
                right_frac   = float(row[col_idx["right_frac"]])
                unknown_frac = float(row[col_idx["unknown_frac"]])
                mean_rule    = float(row[col_idx["mean_rule_hits"]])
                mean_axis    = float(row[col_idx["mean_axis_diff"]])
            except ValueError:
                continue

            log_count = math.log1p(count)

            rows.append({
                "token": token,
                "count": count,
                "left_frac": left_frac,
                "right_frac": right_frac,
                "unknown_frac": unknown_frac,
                "mean_rule_hits": mean_rule,
                "mean_axis_diff": mean_axis,
                "log_count": log_count,
            })
            included += 1

    print(f"[INFO] Loaded {total} rows from {path}", file=sys.stderr)
    print(f"[INFO] Included {included} stems with count >= {MIN_COUNT}", file=sys.stderr)
    return rows


def zscore_features(rows, feature_names):
    """
    Compute z-score normalization for each feature.
    Returns:
      - new_rows: list of dicts with 'z_*' keys added
      - stats: dict feature -> (mean, std)
    """
    sums = {feat: 0.0 for feat in feature_names}
    sums_sq = {feat: 0.0 for feat in feature_names}
    n = len(rows)
    if n == 0:
        print("[ERROR] No rows to cluster after filtering.", file=sys.stderr)
        sys.exit(1)

    # First pass: mean and std
    for r in rows:
        for feat in feature_names:
            v = r[feat]
            sums[feat] += v
            sums_sq[feat] += v * v

    stats = {}
    for feat in feature_names:
        mean = sums[feat] / n
        var = (sums_sq[feat] / n) - (mean * mean)
        std = math.sqrt(var) if var > 0 else 1.0
        stats[feat] = (mean, std)

    # Second pass: add z-scores
    for r in rows:
        for feat in feature_names:
            mean, std = stats[feat]
            z = (r[feat] - mean) / std
            r["z_" + feat] = z

    print("[INFO] Feature z-score stats:", file=sys.stderr)
    for feat in feature_names:
        mean, std = stats[feat]
        print(f"  {feat}: mean={mean:.3f}, std={std:.3f}", file=sys.stderr)

    return rows, stats


def kmeans(rows, feature_names, k, max_iters):
    """
    Simple deterministic k-means on z-scored features.
    - rows: list of dicts, each with 'z_*' features
    - feature_names: original names; we use 'z_'+name
    Initial centers: first k rows (sorted by descending count, then token).
    Returns:
      - assignments: list of cluster_id per row index [0..k-1]
      - centers: list of dicts with center coordinates in z-space
    """
    n = len(rows)
    if n < k:
        print(f"[WARN] n={n} < k={k}, reducing k to {n}", file=sys.stderr)
        k = n

    # Sort rows deterministically by count desc, then token
    rows_sorted_idx = sorted(range(n), key=lambda i: (-rows[i]["count"], rows[i]["token"]))
    # Initial centers: first k rows
    centers = []
    for ci in range(k):
        idx = rows_sorted_idx[ci]
        c = {}
        for feat in feature_names:
            zname = "z_" + feat
            c[zname] = rows[idx][zname]
        centers.append(c)

    assignments = [0] * n

    def dist2(row, center):
        d = 0.0
        for feat in feature_names:
            zname = "z_" + feat
            dv = row[zname] - center[zname]
            d += dv * dv
        return d

    for it in range(max_iters):
        changed = False

        # Assignment step
        for i, r in enumerate(rows):
            best_c = None
            best_d = None
            for ci, center in enumerate(centers):
                d = dist2(r, center)
                if best_d is None or d < best_d:
                    best_d = d
                    best_c = ci
            if assignments[i] != best_c:
                assignments[i] = best_c
                changed = True

        # Recompute centers
        cluster_sums = [defaultdict(float) for _ in range(k)]
        cluster_counts = [0] * k
        for i, r in enumerate(rows):
            ci = assignments[i]
            cluster_counts[ci] += 1
            for feat in feature_names:
                zname = "z_" + feat
                cluster_sums[ci][zname] += r[zname]

        for ci in range(k):
            if cluster_counts[ci] == 0:
                # Keep old center if empty
                continue
            for feat in feature_names:
                zname = "z_" + feat
                centers[ci][zname] = cluster_sums[ci][zname] / cluster_counts[ci]

        print(f"[INFO] k-means iter {it+1}, changed={changed}", file=sys.stderr)
        if not changed:
            print("[INFO] k-means converged.", file=sys.stderr)
            break

    return assignments, centers


def write_fields(rows, assignments, centers, feature_names, out_path):
    tmp_path = out_path + ".tmp"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fieldnames = [
        "token", "count", "cluster_id",
        "left_frac", "right_frac", "unknown_frac",
        "mean_axis_diff", "mean_rule_hits", "log_count",
        "dist_to_center",
    ]

    # Precompute distances
    def dist(row, center):
        d2 = 0.0
        for feat in feature_names:
            zname = "z_" + feat
            dv = row[zname] - center[zname]
            d2 += dv * dv
        return math.sqrt(d2)

    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(fieldnames)

        # deterministic order: by cluster, then count desc, then token
        order = sorted(
            range(len(rows)),
            key=lambda i: (assignments[i], -rows[i]["count"], rows[i]["token"])
        )

        for i in order:
            r = rows[i]
            ci = assignments[i]
            cluster_id = ci + 1  # 1-based
            d = dist(r, centers[ci])

            writer.writerow([
                r["token"],
                r["count"],
                cluster_id,
                f"{r['left_frac']:.3f}",
                f"{r['right_frac']:.3f}",
                f"{r['unknown_frac']:.3f}",
                f"{r['mean_axis_diff']:.3f}",
                f"{r['mean_rule_hits']:.3f}",
                f"{r['log_count']:.3f}",
                f"{d:.3f}",
            ])

    os.replace(tmp_path, out_path)
    print(f"[OK] Wrote VM semantic field assignments → {out_path}", file=sys.stderr)


def write_summary(rows, assignments, feature_names, summary_path):
    tmp_path = summary_path + ".tmp"
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)

    k = max(assignments) + 1 if assignments else 0

    # aggregate per cluster
    agg = []
    for ci in range(k):
        agg.append({
            "n_stems": 0,
            "total_count": 0,
            "sum_left_frac": 0.0,
            "sum_right_frac": 0.0,
            "sum_unknown_frac": 0.0,
            "sum_axis_diff": 0.0,
            "sum_rule_hits": 0.0,
            "sum_log_count": 0.0,
        })

    for i, r in enumerate(rows):
        ci = assignments[i]
        a = agg[ci]
        a["n_stems"] += 1
        a["total_count"] += r["count"]
        a["sum_left_frac"]    += r["left_frac"]
        a["sum_right_frac"]   += r["right_frac"]
        a["sum_unknown_frac"] += r["unknown_frac"]
        a["sum_axis_diff"]    += r["mean_axis_diff"]
        a["sum_rule_hits"]    += r["mean_rule_hits"]
        a["sum_log_count"]    += r["log_count"]

    fieldnames = [
        "cluster_id",
        "n_stems",
        "total_count",
        "mean_left_frac",
        "mean_right_frac",
        "mean_unknown_frac",
        "mean_axis_diff",
        "mean_rule_hits",
        "mean_log_count",
    ]

    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(fieldnames)
        for ci in range(k):
            a = agg[ci]
            n = a["n_stems"] if a["n_stems"] > 0 else 1
            writer.writerow([
                ci + 1,
                a["n_stems"],
                a["total_count"],
                f"{a['sum_left_frac'] / n:.3f}",
                f"{a['sum_right_frac'] / n:.3f}",
                f"{a['sum_unknown_frac'] / n:.3f}",
                f"{a['sum_axis_diff'] / n:.3f}",
                f"{a['sum_rule_hits'] / n:.3f}",
                f"{a['sum_log_count'] / n:.3f}",
            ])

    os.replace(tmp_path, summary_path)
    print(f"[OK] Wrote VM semantic field summary → {summary_path}", file=sys.stderr)


def main():
    feature_names = [
        "left_frac",
        "right_frac",
        "mean_axis_diff",
        "mean_rule_hits",
        "log_count",
    ]

    rows = load_structural_vectors(P71_PATH)
    rows, stats = zscore_features(rows, feature_names)

    assignments, centers = kmeans(rows, feature_names, K_CLUSTERS, MAX_ITERS)

    os.makedirs(OUT_DIR, exist_ok=True)
    write_fields(rows, assignments, centers, feature_names, FIELDS_PATH)
    write_summary(rows, assignments, feature_names, SUMMARY_PATH)


if __name__ == "__main__":
    main()
