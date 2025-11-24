#!/usr/bin/env python3
# p113_permutation_control.py — proper label permutation for Δ = simL - simA
import json, io, random, csv

ATTR = "Phase110/out/p112_attribution.tsv"

def load_delta():
    deltas = []
    with io.open(ATTR, "r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            deltas.append(float(row["delta"]))
    return deltas

def main():
    random.seed(2025)
    deltas = load_delta()
    n = len(deltas)
    if n == 0:
        out = {"n_perm": 0, "delta_observed_mean": None, "delta_null_mean": None, "delta_null_sd": None, "p_value": None}
    else:
        obs = sum(deltas)/n
        # sign-flip permutation: swap Latin/Arabic similarity signs with 0.5 prob
        NPERM = 10000
        null = []
        for _ in range(NPERM):
            s = 0.0
            for d in deltas:
                s += d if random.random() < 0.5 else -d
            null.append(s/n)
        mu = sum(null)/NPERM
        sd = (sum((x-mu)*(x-mu) for x in null)/max(NPERM-1,1))**0.5
        # two-sided p
        more = sum(1 for x in null if abs(x) >= abs(obs))
        p = (more+1)/(NPERM+1)
        out = {"n_perm": NPERM, "delta_observed_mean": obs, "delta_null_mean": mu, "delta_null_sd": sd, "p_value": p}
    with io.open("Phase110/out/p113_permutation_summary.json", "w", encoding="utf-8") as w:
        w.write(json.dumps(out, ensure_ascii=False, indent=2))
    print("[OK] Wrote permutation summary → Phase110/out/p113_permutation_summary.json")

if __name__ == "__main__":
    main()
