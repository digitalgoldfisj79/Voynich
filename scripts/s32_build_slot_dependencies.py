#!/usr/bin/env python3
"""
S32: Cross-position dependencies P(R | L, C) from frame triples.

Input:
  - s21_family_frames.tsv
    columns: family, role_group, pattern, count

Output:
  - s32_slot_dependencies.tsv
    family, role_group, left_token, centre_token, right_token,
    triple_count, pair_total_count, prob_r_given_lc,
    entropy_r_given_lc, entropy_ratio, family_total_instances,
    prob_lc_given_family

  - s32_slot_dependencies.txt
    Human-readable summary per family.
"""

import argparse
import csv
import math
from collections import defaultdict

def shannon_entropy(counts):
    total = float(sum(counts))
    if total <= 0.0 or len(counts) <= 1:
        return 0.0
    h = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        h -= p * math.log(p, 2.0)
    return h

def load_frames(path):
    triple_counts = defaultdict(int)
    pair_totals = defaultdict(int)
    family_totals = defaultdict(int)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            family = row.get("family", "").strip()
            role = row.get("role_group", "").strip()
            pattern = row.get("pattern", "").strip()
            count = int(row.get("count", "0") or "0")

            if not family or not pattern:
                continue

            parts = pattern.split("|")
            if len(parts) != 3:
                # Ignore malformed frames
                continue

            left, centre, right = [p.strip() for p in parts]

            key_triple = (family, role, left, centre, right)
            key_pair = (family, role, left, centre)
            key_family = (family, role)

            triple_counts[key_triple] += count
            pair_totals[key_pair] += count
            family_totals[key_family] += count

    return triple_counts, pair_totals, family_totals

def compute_entropies(triple_counts):
    pair_R_counts = defaultdict(list)
    for (family, role, left, centre, right), cnt in triple_counts.items():
        pair_key = (family, role, left, centre)
        pair_R_counts[pair_key].append(cnt)

    pair_entropy = {}
    pair_entropy_ratio = {}
    for pair_key, counts in pair_R_counts.items():
        h = shannon_entropy(counts)
        k = len(counts)
        if k <= 1:
            hmax = 0.0
            ratio = 0.0
        else:
            hmax = math.log(k, 2.0)
            ratio = h / hmax if hmax > 0.0 else 0.0
        pair_entropy[pair_key] = h
        pair_entropy_ratio[pair_key] = ratio

    return pair_entropy, pair_entropy_ratio

def write_tsv(out_path, triple_counts, pair_totals, family_totals,
              pair_entropy, pair_entropy_ratio):
    fieldnames = [
        "family",
        "role_group",
        "left_token",
        "centre_token",
        "right_token",
        "triple_count",
        "pair_total_count",
        "prob_r_given_lc",
        "entropy_r_given_lc",
        "entropy_ratio",
        "family_total_instances",
        "prob_lc_given_family",
    ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for (family, role, left, centre, right), triple_count in sorted(
            triple_counts.items()
        ):
            pair_key = (family, role, left, centre)
            fam_key = (family, role)
            pair_total = pair_totals.get(pair_key, 0)
            fam_total = family_totals.get(fam_key, 0)

            if pair_total > 0:
                p_r_lc = triple_count / float(pair_total)
            else:
                p_r_lc = 0.0

            if fam_total > 0:
                p_lc_fam = pair_total / float(fam_total)
            else:
                p_lc_fam = 0.0

            h_pair = pair_entropy.get(pair_key, 0.0)
            ratio = pair_entropy_ratio.get(pair_key, 0.0)

            writer.writerow(
                {
                    "family": family,
                    "role_group": role,
                    "left_token": left,
                    "centre_token": centre,
                    "right_token": right,
                    "triple_count": triple_count,
                    "pair_total_count": pair_total,
                    "prob_r_given_lc": f"{p_r_lc:.6f}",
                    "entropy_r_given_lc": f"{h_pair:.6f}",
                    "entropy_ratio": f"{ratio:.6f}",
                    "family_total_instances": fam_total,
                    "prob_lc_given_family": f"{p_lc_fam:.6f}",
                }
            )

def write_txt(out_path, triple_counts, pair_totals, family_totals,
              pair_entropy):
    # Summaries per family
    pairs_by_family = defaultdict(list)
    for (family, role, left, centre, right), triple_count in triple_counts.items():
        pair_key = (family, role, left, centre)
        pairs_by_family[(family, role)].append(pair_key)

    # Count distinct pairs per family and classify deterministic vs branching
    pair_variants = defaultdict(lambda: defaultdict(int))
    for (family, role, left, centre, right), triple_count in triple_counts.items():
        pair_variants[(family, role, left, centre)][right] += triple_count

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("S32 cross-position dependency summary\n")
        f.write("=====================================\n\n")

        families = sorted({(fam, role) for (fam, role, _, _, _) in triple_counts.keys()})
        for (family, role) in families:
            fam_key = (family, role)
            fam_total = family_totals.get(fam_key, 0)
            pair_keys = [pk for pk in pair_variants.keys() if pk[0] == family and pk[1] == role]
            n_pairs = len(pair_keys)

            n_det = 0
            n_branch = 0
            # Track some examples of highest-entropy pairs
            entropy_examples = []

            for pk in pair_keys:
                _, _, left, centre = pk
                r_counts = pair_variants[pk]
                k = len(r_counts)
                if k == 1:
                    n_det += 1
                else:
                    n_branch += 1
                counts = list(r_counts.values())
                h = shannon_entropy(counts)
                entropy_examples.append((h, left, centre, r_counts, sum(counts)))

            entropy_examples.sort(reverse=True)
            top_examples = entropy_examples[:5]

            f.write(f"Family: {family} ({role})\n")
            f.write(f"  Total frame instances: {fam_total}\n")
            f.write(f"  Distinct (L,C) pairs: {n_pairs}\n")
            f.write(f"  Deterministic pairs (single R): {n_det}\n")
            f.write(f"  Branching pairs (multiple R):   {n_branch}\n")
            f.write(f"  Example high-entropy pairs (top 5):\n")
            for h, left, centre, r_counts, total in top_examples:
                f.write(
                    f"    - ({left}, {centre}) -> "
                    f"{len(r_counts)} R-options, H(R|L,C)={h:.3f}, total={total}\n"
                )
            f.write("\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True, help="s21_family_frames.tsv")
    ap.add_argument("--out-tsv", required=True, help="Output TSV path")
    ap.add_argument("--out-txt", required=True, help="Output TXT summary")
    args = ap.parse_args()

    triple_counts, pair_totals, family_totals = load_frames(args.frames)
    pair_entropy, pair_entropy_ratio = compute_entropies(triple_counts)

    write_tsv(
        args.out_tsv,
        triple_counts,
        pair_totals,
        family_totals,
        pair_entropy,
        pair_entropy_ratio,
    )
    write_txt(
        args.out_txt,
        triple_counts,
        pair_totals,
        family_totals,
        pair_entropy,
    )

if __name__ == "__main__":
    main()
