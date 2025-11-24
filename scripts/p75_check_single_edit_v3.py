#!/usr/bin/env python3
import os
import sys
import csv
from collections import defaultdict

BASE = os.path.dirname(__file__)
FAM_FILE = os.path.join(BASE, "..", "Phase75", "out", "p75_families_long.tsv")

def edit_distance(a: str, b: str, max_d: int = 2) -> int:
    """
    Standard Levenshtein distance with early cutoff at max_d.
    We only ever care about d <= 2 for our summary.
    """
    la, lb = len(a), len(b)
    # Quick bounds
    if abs(la - lb) > max_d:
        return max_d + 1
    if a == b:
        return 0

    # DP with banded optimization
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        # Only need to compute within a band of width max_d
        j_start = max(1, i - max_d)
        j_end = min(lb, i + max_d)
        # Fill left of band with large values
        for j in range(1, j_start):
            cur[j] = max_d + 1
        for j in range(j_start, j_end + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(
                prev[j] + 1,        # deletion
                cur[j - 1] + 1,     # insertion
                prev[j - 1] + cost  # substitution
            )
        # Fill right of band with large values
        for j in range(j_end + 1, lb + 1):
            cur[j] = max_d + 1
        prev = cur
        # Early exit: if row minimum already > max_d
        if min(prev) > max_d:
            return max_d + 1
    return prev[lb]

def main():
    print("=== p75: within-family edit-distance analysis (v3, long-format) ===")

    if not os.path.isfile(FAM_FILE):
        print(f"[ERR] Long-format family file not found: {FAM_FILE}")
        sys.exit(1)

    # Load families
    fam2tokens = defaultdict(list)
    with open(FAM_FILE, "r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        if "family" not in r.fieldnames or "token" not in r.fieldnames:
            print("[ERR] Expected columns 'family' and 'token' in p75_families_long.tsv")
            sys.exit(1)
        for row in r:
            fam = row["family"].strip()
            tok = row["token"].strip()
            if fam and tok:
                fam2tokens[fam].append(tok)

    # Keep only non-trivial families
    fam2tokens = {f: toks for f, toks in fam2tokens.items() if len(toks) >= 2}
    if not fam2tokens:
        print("[ERR] No non-trivial families (len>=2) found.")
        sys.exit(1)

    print(f"[INFO] Non-trivial families: {len(fam2tokens)}")

    total_pairs = 0
    ed1_pairs = 0
    ed_le2_pairs = 0

    # For token-level metrics
    token_has_ed1 = set()
    token_has_ed_le2 = set()

    for fam, toks in fam2tokens.items():
        n = len(toks)
        # small optimisation: work on index, not combinations import
        for i in range(n):
            ti = toks[i]
            for j in range(i + 1, n):
                tj = toks[j]
                total_pairs += 1
                d = edit_distance(ti, tj, max_d=2)
                if d == 1:
                    ed1_pairs += 1
                    token_has_ed1.add(ti)
                    token_has_ed1.add(tj)
                    token_has_ed_le2.add(ti)
                    token_has_ed_le2.add(tj)
                elif d == 2:
                    ed_le2_pairs += 1
                    token_has_ed_le2.add(ti)
                    token_has_ed_le2.add(tj)

    if total_pairs == 0:
        print("[ERR] No pairs to compare; something is wrong upstream.")
        sys.exit(1)

    # Deduplicate tokens across families
    all_family_tokens = set()
    for toks in fam2tokens.values():
        all_family_tokens.update(toks)

    # Stats
    pct_pairs_ed1 = ed1_pairs / total_pairs * 100.0
    pct_pairs_ed_le2 = (ed1_pairs + ed_le2_pairs) / total_pairs * 100.0
    pct_tokens_ed1 = len(token_has_ed1) / len(all_family_tokens) * 100.0
    pct_tokens_ed_le2 = len(token_has_ed_le2) / len(all_family_tokens) * 100.0

    print(f"[RESULT] Pairwise ED=1:       {ed1_pairs} / {total_pairs} "
          f"({pct_pairs_ed1:.2f} % of within-family pairs)")
    print(f"[RESULT] Pairwise ED≤2:      {ed1_pairs + ed_le2_pairs} / {total_pairs} "
          f"({pct_pairs_ed_le2:.2f} % of within-family pairs)")
    print(f"[RESULT] Tokens w/ ED=1 nbr: {len(token_has_ed1)} / {len(all_family_tokens)} "
          f"({pct_tokens_ed1:.2f} % of family tokens)")
    print(f"[RESULT] Tokens w/ ED≤2 nbr: {len(token_has_ed_le2)} / {len(all_family_tokens)} "
          f"({pct_tokens_ed_le2:.2f} % of family tokens)")
    print("=== done ===")

if __name__ == "__main__":
    main()
