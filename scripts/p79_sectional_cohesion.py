#!/usr/bin/env python3
"""
Phase 79: Sectional cohesion via family graph permutation test

This script:
  - Reads Phase78/out/p78_family_graph.tsv
  - Reconstructs a dominant section label for each family
  - Computes:
        mean Jaccard (within-section edges)
        mean Jaccard (cross-section edges)
        Δ = within - cross
  - Runs a permutation test by shuffling section labels across families
    while preserving the global section-label multiset.
  - Writes a human-readable summary to Phase79/out/p79_sectional_cohesion.txt

Assumptions:
  - p78_family_graph.tsv has tab-separated columns:
        fam_i  fam_j  jaccard  section_i  section_j  same_section
    with a header line and no weird quoting.
  - Only edges with jaccard > 0 are considered (as in Phase 78).
"""

import os
import sys
import csv
import random
from collections import defaultdict, Counter
from statistics import mean

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_TSV = os.path.join(BASE, "Phase78", "out", "p78_family_graph.tsv")
OUT_DIR = os.path.join(BASE, "Phase79", "out")
OUT_TXT = os.path.join(OUT_DIR, "p79_sectional_cohesion.txt")

N_PERM = 1000
RANDOM_SEED = 12345


def load_edges_and_labels(path):
    edges = []
    fam_sections = defaultdict(list)

    if not os.path.isfile(path):
        print(f"[ERR] Missing input graph: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(
            (line for line in f if line.strip() and not line.startswith("#")),
            delimiter="\t"
        )
        required = {"fam_i", "fam_j", "jaccard", "section_i", "section_j"}
        if not required.issubset(reader.fieldnames):
            print(f"[ERR] p78_family_graph.tsv missing required columns. "
                  f"Found: {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)

        for row in reader:
            try:
                fi = row["fam_i"].strip()
                fj = row["fam_j"].strip()
                sec_i = row["section_i"].strip()
                sec_j = row["section_j"].strip()
                j = float(row["jaccard"])
            except Exception:
                continue

            if j <= 0.0:
                continue

            edges.append((fi, fj, j))

            if sec_i:
                fam_sections[fi].append(sec_i)
            if sec_j:
                fam_sections[fj].append(sec_j)

    if not edges:
        print("[ERR] No usable edges loaded from p78_family_graph.tsv", file=sys.stderr)
        sys.exit(1)

    # Derive dominant section label per family via majority vote
    fam_to_sec = {}
    for fam, labels in fam_sections.items():
        if not labels:
            continue
        counts = Counter(labels)
        # deterministic tie-break by label sorting
        best_label, _ = max(counts.items(), key=lambda x: (x[1], x[0]))
        fam_to_sec[fam] = best_label

    return edges, fam_to_sec


def compute_delta(edges, fam_to_sec):
    """Compute within vs cross mean Jaccard and Δ for a given mapping."""
    within = []
    cross = []

    for fi, fj, j in edges:
        si = fam_to_sec.get(fi)
        sj = fam_to_sec.get(fj)
        if si is None or sj is None:
            continue
        if si == sj:
            within.append(j)
        else:
            cross.append(j)

    if not within or not cross:
        return None, None, None

    m_within = mean(within)
    m_cross = mean(cross)
    delta = m_within - m_cross
    return delta, m_within, m_cross


def perm_test(edges, fam_to_sec, n_perm=N_PERM, seed=RANDOM_SEED):
    random.seed(seed)
    fams = sorted(fam_to_sec.keys())
    labels = [fam_to_sec[f] for f in fams]

    real_delta, real_within, real_cross = compute_delta(edges, fam_to_sec)
    if real_delta is None:
        print("[ERR] Could not compute real Δ (no within or cross edges).", file=sys.stderr)
        sys.exit(1)

    perm_deltas = []
    for _ in range(n_perm):
        shuffled = labels[:]
        random.shuffle(shuffled)
        perm_map = dict(zip(fams, shuffled))
        d, _, _ = compute_delta(edges, perm_map)
        if d is not None:
            perm_deltas.append(d)

    if not perm_deltas:
        print("[ERR] No valid permutations produced Δ values.", file=sys.stderr)
        sys.exit(1)

    # one-sided: how often permuted Δ >= observed Δ
    more_extreme = sum(1 for d in perm_deltas if d >= real_delta)
    p_val = (more_extreme + 1) / (len(perm_deltas) + 1)

    return real_delta, real_within, real_cross, p_val, perm_deltas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("=== Phase 79: Sectional cohesion permutation test ===")
    print(f"[INFO] Reading graph from: {GRAPH_TSV}")

    edges, fam_to_sec = load_edges_and_labels(GRAPH_TSV)

    print(f"[INFO] Edges used: {len(edges)}")
    print(f"[INFO] Families with section labels: {len(fam_to_sec)}")
    sections = sorted(set(fam_to_sec.values()))
    print(f"[INFO] Sections present: {sections}")

    real_delta, real_within, real_cross, p_val, perm_deltas = perm_test(
        edges, fam_to_sec
    )

    print(f"[RESULT] Mean Jaccard (within-section): {real_within:.3f}")
    print(f"[RESULT] Mean Jaccard (cross-section): {real_cross:.3f}")
    print(f"[RESULT] Δ = within - cross:           {real_delta:.3f}")
    print(f"[RESULT] Permutation p-value:          {p_val:.4f}")

    # Write summary
    with open(OUT_TXT, "w", encoding="utf-8") as out:
        out.write("Phase 79: Sectional cohesion via family graph permutation test\n")
        out.write(f"Input graph: {GRAPH_TSV}\n")
        out.write(f"Families with labels: {len(fam_to_sec)}\n")
        out.write(f"Sections: {', '.join(sections)}\n")
        out.write(f"Edges used (J>0): {len(edges)}\n\n")
        out.write(f"Mean Jaccard (within-section): {real_within:.6f}\n")
        out.write(f"Mean Jaccard (cross-section):  {real_cross:.6f}\n")
        out.write(f"Delta (within - cross):        {real_delta:.6f}\n")
        out.write(f"Permutations:                  {len(perm_deltas)}\n")
        out.write(f"One-sided p-value (Δ_perm >= Δ_real): {p_val:.6f}\n")

    print(f"[OK] Summary written → {OUT_TXT}")
    print("=== Phase 79 complete ===")


if __name__ == "__main__":
    main()
