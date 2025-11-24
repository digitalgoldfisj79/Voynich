#!/usr/bin/env python3
import sys
import csv
import math

def load_suffix_summary(path):
    """
    Load a suffix2 summary TSV with at least:
      - 'suffix2'
      - 'total_count'
    Returns: (counts_dict, total_tokens)
    """
    counts = {}
    total_tokens = 0
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if header is None:
            raise ValueError(f"{path}: empty file")

        try:
            idx_suffix = header.index("suffix2")
            idx_count = header.index("total_count")
        except ValueError as e:
            raise ValueError(f"{path}: expected columns 'suffix2' and 'total_count'") from e

        for row in reader:
            if not row or len(row) <= max(idx_suffix, idx_count):
                continue
            suffix = row[idx_suffix]
            try:
                count = int(row[idx_count])
            except ValueError:
                # skip header-like or malformed rows
                continue
            counts[suffix] = counts.get(suffix, 0) + count
            total_tokens += count

    return counts, total_tokens

def js_divergence(p_dist, q_dist):
    """
    Jensen–Shannon divergence between two discrete distributions.
    p_dist, q_dist: dict suffix -> probability
    """
    eps = 0.0  # assume distributions are already proper; no smoothing needed
    all_keys = set(p_dist.keys()) | set(q_dist.keys())
    # Ensure all keys are present with 0
    for k in all_keys:
        p_dist.setdefault(k, 0.0)
        q_dist.setdefault(k, 0.0)

    def kl(a, b):
        s = 0.0
        for k in all_keys:
            pa = a[k]
            pb = b[k]
            if pa > 0.0 and pb > 0.0:
                s += pa * math.log(pa / pb, 2.0)
        return s

    m = {k: 0.5 * (p_dist[k] + q_dist[k]) for k in all_keys}
    return 0.5 * kl(p_dist, m) + 0.5 * kl(q_dist, m)

def main():
    if len(sys.argv) != 4:
        sys.stderr.write(
            "Usage: s6_compare_dante_tac_suffix2.py "
            "<dante_suffix2_summary.tsv> <tac_suffix2_summary.tsv> <out_comparison.tsv>\n"
        )
        sys.exit(1)

    dante_path = sys.argv[1]
    tac_path = sys.argv[2]
    out_path = sys.argv[3]

    dante_counts, dante_total = load_suffix_summary(dante_path)
    tac_counts, tac_total = load_suffix_summary(tac_path)

    if dante_total == 0 or tac_total == 0:
        raise ValueError(f"Zero total tokens: dante_total={dante_total}, tac_total={tac_total}")

    # Build probability distributions
    dante_p = {k: v / dante_total for k, v in dante_counts.items()}
    tac_p = {k: v / tac_total for k, v in tac_counts.items()}

    js = js_divergence(dante_p, tac_p)

    sys.stderr.write(f"[S6-CT] Dante total tokens: {dante_total}\n")
    sys.stderr.write(f"[S6-CT] Tacuinum total tokens: {tac_total}\n")
    sys.stderr.write(f"[S6-CT] JS divergence (suffix2 distribution): {js:.6f}\n")

    # Write per-suffix comparison table
    all_suffixes = sorted(set(dante_counts.keys()) | set(tac_counts.keys()))

    with open(out_path, "w", encoding="utf-8", newline="") as out_f:
        w = csv.writer(out_f, delimiter="\t")
        w.writerow([
            "suffix2",
            "dante_total", "dante_frac",
            "tac_total", "tac_frac",
            "diff", "abs_diff"
        ])

        for sfx in all_suffixes:
            d_tot = dante_counts.get(sfx, 0)
            t_tot = tac_counts.get(sfx, 0)
            d_frac = d_tot / dante_total if dante_total > 0 else 0.0
            t_frac = t_tot / tac_total if tac_total > 0 else 0.0
            diff = t_frac - d_frac
            abs_diff = abs(diff)
            w.writerow([
                sfx,
                d_tot, f"{d_frac:.6f}",
                t_tot, f"{t_frac:.6f}",
                f"{diff:.6f}", f"{abs_diff:.6f}",
            ])

if __name__ == "__main__":
    main()
