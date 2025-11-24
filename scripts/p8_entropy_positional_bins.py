#!/usr/bin/env python3
import sys, math, collections, statistics, os

NBINS = 5  # 0.0, 0.25, 0.5, 0.75, 1.0

def read_tokens(path):
    with open(path) as f:
        return [t.strip() for t in f.read().split() if t.strip()]

def entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return -sum((v/total) * math.log2(v/total) for v in counter.values() if v>0)

def main(path):
    tokens = read_tokens(path)
    if not tokens:
        print(f"[ERR] no tokens in {path}")
        return

    # one counter per bin
    bins = [collections.Counter() for _ in range(NBINS)]

    for tok in tokens:
        L = len(tok)
        if L == 0:
            continue
        if L == 1:
            # degenerate: put single char in all bins equally
            for b in range(NBINS):
                bins[b][tok[0]] += 1
            continue
        for i, ch in enumerate(tok):
            r = i / (L - 1)
            b = min(int(round(r * (NBINS - 1))), NBINS - 1)
            bins[b][ch] += 1

    H = [entropy(bc) for bc in bins]
    left, mid, right = H[0], H[NBINS//2], H[-1]
    delta_edges = ((left + right) / 2.0) - mid
    rsym = 0.0
    if (left + right) > 0:
        rsym = (left - right) / (left + right)

    os.makedirs("out/paper8", exist_ok=True)
    out_tsv = "out/paper8/" + path.split("/")[-1].replace(".txt", "_bins.tsv")
    with open(out_tsv, "w") as o:
        o.write("bin\tH1_bits\n")
        for i, h in enumerate(H):
            frac = i / (NBINS - 1)
            o.write(f"{i}\t{frac:.2f}\t{h:.6f}\n")

    print(f"{path}:")
    print(f"  H_bins = {[round(x,3) for x in H]}")
    print(f"  Δedges = {delta_edges:+.3f}   ( (L+R)/2 - mid )")
    print(f"  R_sym  = {rsym:+.3f}   (left vs right symmetry)")
    print(f"  tokens = {len(tokens)}")
    print(f"  [OK] wrote {out_tsv}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: p8_entropy_positional_bins.py <corpus.txt>")
        sys.exit(1)
    main(sys.argv[1])
