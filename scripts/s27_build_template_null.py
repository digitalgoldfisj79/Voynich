#!/usr/bin/env python3
"""
S27: Null-model for recurrent templates (frame rung)

Input:
  - s23_frame_stats.tsv  (family-level frame stats)
Output:
  - s27_template_null.tsv (TSV with null expectations and z-scores)
  - s27_template_null.txt (human-readable summary)

This uses a simple balls-into-bins simulation per family:
  - n_patterns bins  (distinct_patterns)
  - total_instances balls (total_instances)
to estimate expected number of bins with count >= 2 and >= 5
under a random assignment.
"""

import sys
import csv
import math
import random
from collections import namedtuple

Stats = namedtuple(
    "Stats",
    [
        "family",
        "distinct_patterns",
        "total_instances",
        "real_ge2",
        "real_ge5",
        "entropy_bits",
        "top10_coverage",
        "top50_coverage",
    ],
)


def load_stats(path):
    stats = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if header is None or len(header) < 8:
            raise RuntimeError("[S27] s23 stats header malformed or missing")
        # Expect: family, distinct_patterns, total_instances, recurrent_ge2, recurrent_ge5, entropy_bits, top10_coverage, top50_coverage
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            family = row[0]
            distinct_patterns = int(row[1])
            total_instances = int(row[2])
            real_ge2 = int(row[3])
            real_ge5 = int(row[4])
            entropy_bits = float(row[5])
            top10 = float(row[6])
            top50 = float(row[7])
            stats.append(
                Stats(
                    family=family,
                    distinct_patterns=distinct_patterns,
                    total_instances=total_instances,
                    real_ge2=real_ge2,
                    real_ge5=real_ge5,
                    entropy_bits=entropy_bits,
                    top10_coverage=top10,
                    top50_coverage=top50,
                )
            )
    if not stats:
        raise RuntimeError("[S27] No rows read from s23 stats")
    return stats


def simulate_null(n_bins, n_balls, n_sims=2000):
    """
    Simple occupancy model:
      - n_bins: number of distinct patterns
      - n_balls: total frames
      - n_sims: number of Monte Carlo runs

    Returns:
      dict with mean/sd for counts >=2 and >=5.
    """
    # Fixed seed for reproducibility
    random.seed(27 + n_bins + n_balls)

    ge2_vals = []
    ge5_vals = []

    for _ in range(n_sims):
        counts = [0] * n_bins
        # assign each frame to a random pattern (uniform)
        for _ in range(n_balls):
            j = random.randrange(n_bins)
            counts[j] += 1
        ge2 = sum(1 for c in counts if c >= 2)
        ge5 = sum(1 for c in counts if c >= 5)
        ge2_vals.append(ge2)
        ge5_vals.append(ge5)

    def mean_sd(vals):
        n = len(vals)
        if n == 0:
            return 0.0, 0.0
        m = sum(vals) / n
        var = sum((v - m) ** 2 for v in vals) / n
        return m, math.sqrt(var)

    mean_ge2, sd_ge2 = mean_sd(ge2_vals)
    mean_ge5, sd_ge5 = mean_sd(ge5_vals)

    return {
        "n_sims": n_sims,
        "mean_ge2": mean_ge2,
        "sd_ge2": sd_ge2,
        "mean_ge5": mean_ge5,
        "sd_ge5": sd_ge5,
    }


def z_score(real, mean, sd):
    if sd <= 0:
        return None
    return (real - mean) / sd


def main():
    if len(sys.argv) != 4:
        sys.stderr.write(
            "[S27] Usage: s27_build_template_null.py "
            "<s23_frame_stats.tsv> <out_tsv> <out_txt>\n"
        )
        sys.exit(1)

    in_stats_path = sys.argv[1]
    out_tsv_path = sys.argv[2]
    out_txt_path = sys.argv[3]

    stats = load_stats(in_stats_path)

    # Run null-model per family
    results = []
    for st in stats:
        sys.stderr.write(
            f"[S27] Simulating null for {st.family} "
            f"(patterns={st.distinct_patterns}, frames={st.total_instances})\n"
        )
        nm = simulate_null(st.distinct_patterns, st.total_instances, n_sims=2000)
        z_ge2 = z_score(st.real_ge2, nm["mean_ge2"], nm["sd_ge2"])
        z_ge5 = z_score(st.real_ge5, nm["mean_ge5"], nm["sd_ge5"])
        results.append((st, nm, z_ge2, z_ge5))

    # Write TSV
    with open(out_tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "family",
                "distinct_patterns",
                "total_instances",
                "real_recurrent_ge2",
                "real_recurrent_ge5",
                "null_n_sims",
                "null_mean_ge2",
                "null_sd_ge2",
                "null_mean_ge5",
                "null_sd_ge5",
                "z_ge2",
                "z_ge5",
            ]
        )
        for st, nm, z_ge2, z_ge5 in results:
            writer.writerow(
                [
                    st.family,
                    st.distinct_patterns,
                    st.total_instances,
                    st.real_ge2,
                    st.real_ge5,
                    nm["n_sims"],
                    f"{nm['mean_ge2']:.6f}",
                    f"{nm['sd_ge2']:.6f}",
                    f"{nm['mean_ge5']:.6f}",
                    f"{nm['sd_ge5']:.6f}",
                    "" if z_ge2 is None else f"{z_ge2:.3f}",
                    "" if z_ge5 is None else f"{z_ge5:.3f}",
                ]
            )

    # Write TXT summary
    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write("S27 template null-model summary\n")
        f.write("========================================\n\n")
        for st, nm, z_ge2, z_ge5 in results:
            f.write(f"Family: {st.family}\n")
            f.write(f"  Distinct patterns (N)         : {st.distinct_patterns}\n")
            f.write(f"  Total frame instances (M)     : {st.total_instances}\n")
            f.write(f"  Real recurrent templates ≥2   : {st.real_ge2}\n")
            f.write(f"  Real recurrent templates ≥5   : {st.real_ge5}\n")
            f.write(
                f"  Null-model sims               : {nm['n_sims']}\n"
            )
            f.write(
                "  Null expectation (count ≥2)   : "
                f"{nm['mean_ge2']:.2f} ± {nm['sd_ge2']:.2f}\n"
            )
            f.write(
                "  Null expectation (count ≥5)   : "
                f"{nm['mean_ge5']:.2f} ± {nm['sd_ge5']:.2f}\n"
            )
            if z_ge2 is not None:
                f.write(f"  z-score (≥2)                  : {z_ge2:.2f}\n")
            if z_ge5 is not None:
                f.write(f"  z-score (≥5)                  : {z_ge5:.2f}\n")
            f.write("\n")

    sys.stderr.write(f"[S27] Wrote TSV to {out_tsv_path}\n")
    sys.stderr.write(f"[S27] Wrote TXT to {out_txt_path}\n")


if __name__ == "__main__":
    main()
