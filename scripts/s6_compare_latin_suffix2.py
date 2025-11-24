#!/usr/bin/env python3
import sys, math, csv

def load_suffix2(path):
    data = {}
    total = 0
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            sfx = row["suffix2"]
            c = int(row["total_count"])
            data[sfx] = c
            total += c
    return data, total

def js_divergence(p, q):
    """
    Jensen–Shannon divergence between two discrete distributions
    p, q: dict suffix -> prob
    """
    keys = set(p.keys()) | set(q.keys())
    js = 0.0
    for k in keys:
        pk = p.get(k, 0.0)
        qk = q.get(k, 0.0)
        m = 0.5 * (pk + qk)
        if pk > 0:
            js += 0.5 * pk * math.log(pk / m)
        if qk > 0:
            js += 0.5 * qk * math.log(qk / m)
    # natural log -> convert to bits if you like, but we’ll just report nat units
    return js

def main():
    if len(sys.argv) != 4:
        print("Usage: s6_compare_latin_suffix2.py <dante_suffix2.tsv> <tac_suffix2.tsv> <out.tsv>", file=sys.stderr)
        sys.exit(1)

    dante_path, tac_path, out_path = sys.argv[1:]

    dante_counts, dante_total = load_suffix2(dante_path)
    tac_counts, tac_total     = load_suffix2(tac_path)

    dante_probs = {k: v / dante_total for k, v in dante_counts.items()}
    tac_probs   = {k: v / tac_total   for k, v in tac_counts.items()}

    js = js_divergence(dante_probs, tac_probs)

    keys = sorted(set(dante_counts.keys()) | set(tac_counts.keys()))
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow([
            "suffix2",
            "dante_count", "dante_frac",
            "tac_count",   "tac_frac",
            "diff_tac_minus_dante",
            "abs_diff"
        ])
        for k in keys:
            dc = dante_counts.get(k, 0)
            tc = tac_counts.get(k, 0)
            df = dante_probs.get(k, 0.0)
            tf = tac_probs.get(k, 0.0)
            diff = tf - df
            w.writerow([k, dc, f"{df:.6f}", tc, f"{tf:.6f}", f"{diff:.6f}", f"{abs(diff):.6f}"])

    print(f"[S6-CT] Dante total tokens: {dante_total}")
    print(f"[S6-CT] Tacuinum total tokens: {tac_total}")
    print(f"[S6-CT] JS divergence (suffix2 distribution): {js:.6f}")

if __name__ == "__main__":
    main()
