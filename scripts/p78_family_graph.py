#!/usr/bin/env python3
import os
import csv
from collections import defaultdict
from itertools import combinations

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P75_FAMILIES = os.path.join(BASE, "Phase75", "out", "p75_families.tsv")
P77_ANCHORS = os.path.join(BASE, "Phase77", "out", "p77_anchor_families.tsv")
OUT_DIR = os.path.join(BASE, "Phase78", "out")
EDGE_OUT = os.path.join(OUT_DIR, "p78_family_graph.tsv")
SUMMARY_OUT = os.path.join(OUT_DIR, "p78_family_graph_summary.txt")

# Jaccard threshold for writing an edge
MIN_JACCARD = 0.20


def load_families(path):
    """
    Load family_signature → set(morphemes) from p75_families.tsv.
    Expected columns: family_signature, count, examples
    """
    families = {}
    if not os.path.isfile(path):
        raise FileNotFoundError(f"[ERR] Family file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if "family_signature" not in reader.fieldnames:
            raise ValueError(
                f"[ERR] Expected 'family_signature' column in {path}, "
                f"found: {reader.fieldnames}"
            )
        for row in reader:
            sig = row["family_signature"].strip()
            if not sig:
                continue
            parts = [p.strip() for p in sig.split("-") if p.strip()]
            if parts:
                families[sig] = set(parts)

    return families


def load_anchor_families(path):
    """
    Load subset of families that are anchors, with their dominant section.

    Expected columns in p77_anchor_families.tsv:
      - family OR family_signature
      - section
      - count
      - fraction

    Returns:
      anchors: dict(family_signature -> {"section": str, "count": int, "fraction": float})
    """
    anchors = {}
    if not os.path.isfile(path):
        raise FileNotFoundError(f"[ERR] Anchor file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        # Try to resolve column names flexibly
        cols = reader.fieldnames or []
        fam_col = None
        for cand in ("family", "family_signature"):
            if cand in cols:
                fam_col = cand
                break
        if fam_col is None or "section" not in cols:
            raise ValueError(
                f"[ERR] Expected 'family' or 'family_signature' and 'section' in {path}, "
                f"found: {cols}"
            )

        for row in reader:
            sig = row[fam_col].strip()
            if not sig:
                continue
            section = row.get("section", "").strip() or "Unknown"
            try:
                cnt = int(row.get("count", "0"))
            except ValueError:
                cnt = 0
            try:
                frac = float(row.get("fraction", "0"))
            except ValueError:
                frac = 0.0
            anchors[sig] = {
                "section": section,
                "count": cnt,
                "fraction": frac,
            }

    return anchors


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    union = len(a | b)
    return inter / union if union > 0 else 0.0


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("=== Phase 78: Family graph & sectional clustering ===")

    # 1) Load data
    families = load_families(P75_FAMILIES)
    print(f"[INFO] Loaded {len(families)} families from {P75_FAMILIES}")

    anchors = load_anchor_families(P77_ANCHORS)
    print(f"[INFO] Loaded {len(anchors)} anchor families from {P77_ANCHORS}")

    # Filter anchors to those we have family signatures for
    anchor_sigs = [sig for sig in anchors.keys() if sig in families]
    missing = [sig for sig in anchors.keys() if sig not in families]
    if missing:
        print(f"[WARN] {len(missing)} anchor families not found in p75_families.tsv; ignoring them.")

    print(f"[INFO] Using {len(anchor_sigs)} anchor families with known signatures.")

    if len(anchor_sigs) < 2:
        print("[WARN] Fewer than 2 usable anchors; no graph to build.")
        # Still write empty files for reproducibility
        with open(EDGE_OUT, "w", encoding="utf-8", newline="") as f:
            f.write("#fam_i\tfam_j\tjaccard\tsection_i\tsection_j\tsame_section\n")
        with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
            f.write("Phase 78: not enough anchor families to compute graph.\n")
        print("[OK] Wrote empty outputs.")
        return

    # 2) Compute pairwise Jaccard similarities
    edges = []
    within_vals = []
    cross_vals = []

    for f1, f2 in combinations(anchor_sigs, 2):
        s1 = families[f1]
        s2 = families[f2]
        j = jaccard(s1, s2)
        if j <= 0:
            continue

        sec1 = anchors[f1]["section"]
        sec2 = anchors[f2]["section"]
        same = int(sec1 == sec2)

        # Collect stats for all positive pairs
        if same:
            within_vals.append(j)
        else:
            cross_vals.append(j)

        # Only write edges above threshold
        if j >= MIN_JACCARD:
            edges.append((f1, f2, j, sec1, sec2, same))

    # 3) Write edge list
    with open(EDGE_OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["fam_i", "fam_j", "jaccard", "section_i", "section_j", "same_section"])
        for fam_i, fam_j, j, sec_i, sec_j, same in sorted(
            edges, key=lambda x: (-x[2], x[0], x[1])
        ):
            w.writerow([fam_i, fam_j, f"{j:.3f}", sec_i, sec_j, same])

    # 4) Summary stats
    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        f.write("=== Phase 78: Family graph & sectional clustering ===\n")
        f.write(f"Anchor families used: {len(anchor_sigs)}\n")
        f.write(f"Edges written (Jaccard ≥ {MIN_JACCARD:.2f}): {len(edges)}\n")
        f.write("\n")
        f.write(f"Within-section pairs (J>0): {len(within_vals)}, "
                f"mean J = {mean(within_vals):.3f}\n")
        f.write(f"Cross-section pairs  (J>0): {len(cross_vals)}, "
                f"mean J = {mean(cross_vals):.3f}\n")
        f.write("\nInterpretation:\n")
        f.write("- Families are nodes; edges link families sharing morphemes.\n")
        f.write("- Higher within-section mean Jaccard than cross-section implies\n")
        f.write("  that anchor families group by manuscript section, consistent\n")
        f.write("  with functionally specialized morphological subsystems.\n")

    print(f"[OK] Wrote family graph edges → {EDGE_OUT}")
    print(f"[OK] Wrote summary → {SUMMARY_OUT}")
    print("=== Phase 78 complete ===")


if __name__ == "__main__":
    main()
