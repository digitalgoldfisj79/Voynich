#!/usr/bin/env python3
import os
import sys
import math
import itertools
from collections import Counter

# ---------- CONFIG: which corpora to include ----------

# Adjust paths if needed; script will skip missing files gracefully.
CORPORA = [
    ("voynich",               "p6_voynich_tokens.txt"),
    ("latin_abbrev_comp",     "corpora/latin_abbrev_compressed.txt"),
    ("latin_abbrev_exp",      "corpora/latin_abbrev_expanded.txt"),
    ("latin_dante_monarchia", "corpora/latin_tokens.txt"),
    ("guide_hebrew",          "corpora/tokens_hebrew.txt"),
    ("guide_arabic",          "corpora/tokens_arabic.txt"),
]

OUTDIR = "Phase901/out"
OUTFILE = os.path.join(OUTDIR, "p9_feature_table.tsv")

MIN_TOKENS_WARN = 500  # below this, we warn but still print


# ---------- basic helpers ----------

def load_tokens(path):
    tokens = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            t = line.strip()
            if t:
                tokens.append(t)
    return tokens

def shannon_entropy_from_counts(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        p = c / total
        h -= p * math.log2(p)
    return h

def compute_H1_MI1(tokens):
    """Character-level H1 and MI1 over concatenated tokens with spaces."""
    # build stream including spaces as delimiters
    stream = []
    for t in tokens:
        if t:
            stream.extend(t)
            stream.append(" ")  # simple boundary marker
    if stream:
        stream.pop()  # remove last boundary

    # H1
    c_counts = Counter(stream)
    H1 = shannon_entropy_from_counts(c_counts)

    # MI1
    if len(stream) < 2:
        return H1, 0.0
    bigram_counts = Counter()
    for a, b in zip(stream[:-1], stream[1:]):
        bigram_counts[(a, b)] += 1

    total_bigram = sum(bigram_counts.values())
    if total_bigram == 0:
        return H1, 0.0

    # p(a), p(b)
    # reuse c_counts / total_chars
    total_chars = sum(c_counts.values())
    pa = {ch: c_counts[ch] / total_chars for ch in c_counts}
    pb = pa  # same marginals over same alphabet

    mi = 0.0
    for (a, b), c in bigram_counts.items():
        p_ab = c / total_bigram
        p_a = pa.get(a, 0.0)
        p_b = pb.get(b, 0.0)
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))

    return H1, mi


def compute_positional_bins(tokens):
    """
    Assign characters to 5 relative bins based on index/len:
    b = min(4, floor(5 * i / L)).
    Returns list of 5 entropies [H0..H4].
    """
    bins = [Counter() for _ in range(5)]
    for t in tokens:
        L = len(t)
        if L <= 0:
            continue
        for i, ch in enumerate(t):
            # skip spaces or weird stuff if any
            if ch.isspace():
                continue
            b = int(5 * i / L)
            if b > 4:
                b = 4
            bins[b][ch] += 1

    H_bins = [shannon_entropy_from_counts(c) for c in bins]
    return H_bins


def compute_slope_and_permutation_p(H_bins):
    """
    Given 5-bin entropies, compute:
    - slope: OLS of H vs [0,0.25,0.5,0.75,1.0]
    - p_perm: exact two-sided permutation p-value based on |slope|
    """
    if len(H_bins) != 5:
        return 0.0, 1.0

    xs = [0.0, 0.25, 0.5, 0.75, 1.0]
    ys = H_bins

    mean_x = sum(xs) / 5.0
    mean_y = sum(ys) / 5.0

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    slope = num / den if den > 0 else 0.0

    # permutation test over all 5! = 120 permutations
    perms = list(itertools.permutations(ys))
    more_extreme = 0
    for p in perms:
        m_y = sum(p) / 5.0
        num_p = sum((x - mean_x) * (y - m_y) for x, y in zip(xs, p))
        slope_p = num_p / den if den > 0 else 0.0
        if abs(slope_p) >= abs(slope):
            more_extreme += 1
    p_perm = more_extreme / len(perms) if perms else 1.0

    return slope, p_perm


def compute_delta_edges_and_sym(H_bins):
    if len(H_bins) != 5:
        return 0.0, 0.0
    H0, H1b, H2b, H3b, H4 = H_bins
    delta_edges = ((H0 + H4) / 2.0) - H2b
    r_sym = H0 - H4
    return delta_edges, r_sym


# ---------- main ----------

def main():
    os.makedirs(OUTDIR, exist_ok=True)

    header = [
        "label",
        "n_tokens",
        "H1",
        "MI1",
        "H0",
        "H1_bin",
        "H2_bin",
        "H3_bin",
        "H4_bin",
        "slope",
        "p_perm",
        "Delta_edges",
        "R_sym",
    ]

    with open(OUTFILE, "w", encoding="utf-8") as f_out:
        f_out.write("\t".join(header) + "\n")

        for label, path in CORPORA:
            full_path = os.path.join(path) if not os.path.isabs(path) else path

            if not os.path.isfile(full_path):
                print(f"[WARN] {label}: file not found: {full_path}, skipping.")
                continue

            tokens = load_tokens(full_path)
            n = len(tokens)

            if n == 0:
                print(f"[WARN] {label}: 0 tokens, skipping.")
                continue

            if n < MIN_TOKENS_WARN:
                print(f"[WARN] {label}: only {n} tokens (<{MIN_TOKENS_WARN}), interpret with caution.")

            H1, MI1 = compute_H1_MI1(tokens)
            H_bins = compute_positional_bins(tokens)
            slope, p_perm = compute_slope_and_permutation_p(H_bins)
            d_edges, r_sym = compute_delta_edges_and_sym(H_bins)

            H0, H1b, H2b, H3b, H4 = H_bins

            print(
                f"[INFO] {label:20s} n={n:6d} "
                f"H1={H1:.6f} MI1={MI1:.6f} "
                f"Hbins={[f'{h:.3f}' for h in H_bins]} "
                f"slope={slope:.3f} p={p_perm:.3f}"
            )

            row = [
                label,
                str(n),
                f"{H1:.6f}",
                f"{MI1:.6f}",
                f"{H0:.6f}",
                f"{H1b:.6f}",
                f"{H2b:.6f}",
                f"{H3b:.6f}",
                f"{H4:.6f}",
                f"{slope:.6f}",
                f"{p_perm:.6f}",
                f"{d_edges:.6f}",
                f"{r_sym:.6f}",
            ]
            f_out.write("\t".join(row) + "\n")

    print(f"[OK] Wrote feature table → {OUTFILE}")


if __name__ == "__main__":
    main()
