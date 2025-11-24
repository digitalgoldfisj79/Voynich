#!/usr/bin/env python3
import sys
import math
from collections import Counter

def entropy(chars: str) -> float:
    c = Counter(chars)
    n = sum(c.values())
    if n == 0:
        return 0.0
    return -sum((v / n) * math.log2(v / n) for v in c.values() if v)

def mi1(chars: str) -> float:
    # Mutual information between adjacent characters
    if len(chars) < 2:
        return 0.0

    pair_counts = Counter(zip(chars, chars[1:]))
    n_pairs = sum(pair_counts.values())
    if n_pairs == 0:
        return 0.0

    x_counts = Counter()
    y_counts = Counter()
    for (a, b), v in pair_counts.items():
        x_counts[a] += v
        y_counts[b] += v

    mi = 0.0
    for (a, b), v in pair_counts.items():
        p_xy = v / n_pairs
        p_x = x_counts[a] / n_pairs
        p_y = y_counts[b] / n_pairs
        # avoid any numerical weirdness
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))

    return mi

def main():
    if len(sys.argv) != 2:
        print("Usage: p6_compute_entropy_mi.py <tokens.txt>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            tokens = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[ERR] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    chars = "".join(tokens)
    H1 = entropy(chars)
    MI = mi1(chars)

    print(f"# {path}")
    print(f"H1_bits_per_char\t{H1:.6f}")
    print(f"MI1_bits\t{MI:.6f}")

if __name__ == "__main__":
    main()
