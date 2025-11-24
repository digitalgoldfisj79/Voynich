#!/usr/bin/env python3
import os
import sys
import csv
from collections import defaultdict

FAM_FILE = os.path.join(os.path.dirname(__file__),
                        "..", "Phase75", "out", "p75_families.tsv")

def lev_dist(a: str, b: str) -> int:
    """Levenshtein edit distance (insert/delete/substitute, unit cost)."""
    la, lb = len(a), len(b)
    if a == b:
        return 0
    if la == 0:
        return lb
    if lb == 0:
        return la
    # DP matrix (2 rows rolling)
    prev = list(range(lb + 1))
    cur = [0] * (lb + 1)
    for i in range(1, la + 1):
        cur[0] = i
        ca = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ca == b[j - 1] else 1
            cur[j] = min(
                prev[j] + 1,      # deletion
                cur[j - 1] + 1,   # insertion
                prev[j - 1] + cost  # substitution / match
            )
        prev, cur = cur, prev
    return prev[lb]

def load_families(path: str):
    """
    Load families from p75_families.tsv.

    Supports two formats:
    1) Long:
        family <tab> token
    2) Compact:
        family_signature <tab> count <tab> examples
       (in which case we CANNOT reconstruct full membership and will abort)
    """
    families = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = [c.strip() for c in reader.fieldnames] if reader.fieldnames else []

        # Long format: must have 'family' and 'token'
        if "family" in fieldnames and "token" in fieldnames:
            for row in reader:
                fam = row["family"].strip()
                tok = row["token"].strip()
                if fam and tok:
                    families[fam].append(tok)
            fmt = "long"
        # Compact format: only signature + examples (cannot use for ED stats)
        elif "family_signature" in fieldnames:
            fmt = "compact"
        else:
            raise RuntimeError(
                f"Unrecognised p75_families.tsv format; columns={fieldnames}"
            )

    return families, fmt

def main():
    print("=== p75: within-family edit-distance analysis (v2) ===")
    if not os.path.isfile(FAM_FILE):
        print(f"[ERR] Family file not found: {FAM_FILE}")
        sys.exit(1)

    families, fmt = load_families(FAM_FILE)
    if fmt != "long":
        print("[ERR] p75_families.tsv is in compact format (family_signature/examples).")
        print("      Re-run p75_build_families.py with long-output mode to enable this analysis.")
        sys.exit(1)

    # Filter non-trivial families
    non_trivial = {fam: toks for fam, toks in families.items() if len(toks) >= 2}
    n_fam = len(non_trivial)
    print(f"[INFO] Non-trivial families (>=2 tokens): {n_fam}")

    if n_fam == 0:
        print("[ERR] No non-trivial families; nothing to analyse.")
        sys.exit(1)

    # Metrics
    total_pairs = 0
    ed1_pairs = 0

    tokens_in_nt = 0
    tokens_with_ed1 = set()
    tokens_with_ed_le2 = set()  # lenient

    # Assign unique IDs so we can track tokens across families
    # (family,label,index) to avoid collisions
    global_idx = 0
    token_ids = {}  # (fam, i) -> global_id

    for fam, toks in non_trivial.items():
        for i, tok in enumerate(toks):
            token_ids[(fam, i)] = global_idx
            global_idx += 1

    # Now compute pairwise distances within each family
    for fam, toks in non_trivial.items():
        m = len(toks)
        tokens_in_nt += m
        for i in range(m):
            id_i = token_ids[(fam, i)]
            for j in range(i + 1, m):
                id_j = token_ids[(fam, j)]
                total_pairs += 1
                d = lev_dist(toks[i], toks[j])
                if d == 1:
                    ed1_pairs += 1
                    tokens_with_ed1.add(id_i)
                    tokens_with_ed1.add(id_j)
                    tokens_with_ed_le2.add(id_i)
                    tokens_with_ed_le2.add(id_j)
                elif d == 2:
                    tokens_with_ed_le2.add(id_i)
                    tokens_with_ed_le2.add(id_j)

    if total_pairs == 0:
        print("[ERR] No pairs found (unexpected).")
        sys.exit(1)

    # Strict pairwise metric
    pct_pairs_ed1 = ed1_pairs / total_pairs * 100.0

    # Token-level metrics
    n_tokens_ed1 = len(tokens_with_ed1)
    n_tokens_le2 = len(tokens_with_ed_le2)

    pct_tokens_ed1 = n_tokens_ed1 / tokens_in_nt * 100.0 if tokens_in_nt else 0.0
    pct_tokens_le2 = n_tokens_le2 / tokens_in_nt * 100.0 if tokens_in_nt else 0.0

    print(f"[RESULT] Within-family pairs at edit-distance 1: "
          f"{ed1_pairs} / {total_pairs} "
          f"({pct_pairs_ed1:.2f} %)")
    print(f"[RESULT] Tokens in non-trivial families: {tokens_in_nt}")
    print(f"[RESULT] Tokens with ≥1 edit-distance-1 neighbour: "
          f"{n_tokens_ed1} "
          f"({pct_tokens_ed1:.2f} % of tokens in non-trivial families)")
    print(f"[RESULT] Tokens with ≥1 edit-distance≤2 neighbour: "
          f"{n_tokens_le2} "
          f"({pct_tokens_le2:.2f} % of tokens in non-trivial families)")
    print("=== done ===")

if __name__ == "__main__":
    main()
