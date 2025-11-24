#!/usr/bin/env python3
import sys
import csv
import math

def read_tsv(path):
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.reader(f, delimiter='\t'))

def euclid(a, b):
    return math.sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

def main():
    if len(sys.argv) != 4:
        print("Usage: s3_build_section_stability.py <folio_vectors> <section_summary> <out_path>")
        sys.exit(1)

    folio_path = sys.argv[1]
    summary_path = sys.argv[2]
    out_path = sys.argv[3]

    # Load folio vectors
    folio_rows = read_tsv(folio_path)
    f_header = folio_rows[0]

    # We use only behavioural features, aligned by column index:
    # avg_left_frac, avg_right_frac, avg_unknown_frac,
    # avg_left_score, avg_right_score, avg_rule_hits, avg_axis_diff
    # In s1_folio_structural_vectors.tsv these are cols 4..10.
    folio_feat_idx = list(range(4, 11))

    folios = []
    for r in folio_rows[1:]:
        folio_id = r[0]
        section = r[1]
        try:
            vec = [float(r[i]) for i in folio_feat_idx]
        except (ValueError, IndexError):
            continue
        folios.append((folio_id, section, vec))

    # Load section centroids
    summary_rows = read_tsv(summary_path)
    s_header = summary_rows[0]

    # Corresponding centroid features are:
    # mean_avg_left_frac, mean_avg_right_frac, mean_avg_unknown_frac,
    # mean_avg_left_score, mean_avg_right_score, mean_avg_rule_hits, mean_avg_axis_diff
    # In s2_section_structural_summary.tsv these are also cols 4..10.
    centroid_feat_idx = list(range(4, 11))

    centroids = {}  # section → vector
    for r in summary_rows[1:]:
        sec = r[0]
        try:
            vec = [float(r[i]) for i in centroid_feat_idx]
        except (ValueError, IndexError):
            continue
        centroids[sec] = vec

    out = []
    out.append(["folio", "true_section", "dist_true", "nearest_other_section", "dist_other", "margin"])

    for folio_id, true_sec, vec in folios:
        if true_sec not in centroids:
            continue

        true_vec = centroids[true_sec]
        if len(vec) != len(true_vec):
            # safety guard: skip if any mismatch survives
            continue

        true_d = euclid(vec, true_vec)

        nearest = None
        nearest_d = 1e9
        for sec, cvec in centroids.items():
            if sec == true_sec:
                continue
            if len(cvec) != len(vec):
                continue
            d = euclid(vec, cvec)
            if d < nearest_d:
                nearest_d = d
                nearest = sec

        margin = nearest_d - true_d
        out.append([folio_id, true_sec, f"{true_d:.6f}", nearest, f"{nearest_d:.6f}", f"{margin:.6f}"])

    with open(out_path, 'w', encoding='utf-8') as f:
        for row in out:
            f.write("\t".join(str(x) for x in row) + "\n")

    print(f"[OK] Wrote section stability → {out_path}")

if __name__ == "__main__":
    main()
