#!/usr/bin/env python3
import sys, math, itertools

def read_bins(path):
    H = []
    with open(path) as f:
        for ln in f:
            if ln.startswith("bin") or not ln.strip():
                continue
            parts = ln.strip().split("\t")
            # expected: bin, frac, H1_bits
            if len(parts) < 3:
                continue
            try:
                h = float(parts[2])
            except ValueError:
                continue
            H.append(h)
    if len(H) < 3:
        raise ValueError(f"Not enough bins in {path}")
    return H

def linreg_slope(xs, ys):
    n = len(xs)
    mx = sum(xs)/n
    my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den = sum((x-mx)**2 for x in xs)
    if den == 0:
        return 0.0
    return num/den

def compute_metrics(H):
    n = len(H)
    # relative positions 0..1
    xs = [i/(n-1) for i in range(n)]
    slope = linreg_slope(xs, H)

    left = H[0]
    mid = H[n//2]
    right = H[-1]
    delta_edges = ((left + right)/2.0) - mid

    rsym = 0.0
    if (left + right) != 0:
        rsym = (left - right) / (left + right)

    return slope, delta_edges, rsym

def permutation_pvalue(H, observed_slope):
    # exact test over all permutations of H
    vals = list(H)
    perms = set(itertools.permutations(vals))
    total = 0
    extreme = 0
    n = len(vals)
    xs = [i/(n-1) for i in range(n)]
    for perm in perms:
        total += 1
        s = linreg_slope(xs, perm)
        if abs(s) >= abs(observed_slope) - 1e-12:
            extreme += 1
    p = extreme / total if total > 0 else 1.0
    return p, total

def main(path):
    H = read_bins(path)
    slope, dE, rsym = compute_metrics(H)
    p, nperm = permutation_pvalue(H, slope)

    print(f"{path}")
    print(f"  H_bins       = {[round(h,3) for h in H]}")
    print(f"  slope        = {slope:+.4f}   (H1 vs relative position)")
    print(f"  Δedges       = {dE:+.4f}   ( (L+R)/2 - mid )")
    print(f"  R_sym        = {rsym:+.4f}   (left vs right symmetry)")
    print(f"  perm_test    = two-sided, |slope| vs all {nperm} permutations of same H set")
    print(f"  p_value      = {p:.4f}")
    print("")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: p8_stats_edgegrad.py out/paper8/<corpus>_bins.tsv")
        sys.exit(1)
    main(sys.argv[1])
