#!/usr/bin/env python3
import os
import csv
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

F_GRAPH   = os.path.join(ROOT, "Phase78", "out", "p78_family_graph.tsv")
F_ANCHORS = os.path.join(ROOT, "Phase77", "out", "p77_anchor_families.tsv")
OUT_DIR   = os.path.join(ROOT, "Phase80", "out")
NODES_OUT = os.path.join(OUT_DIR, "p80_nodes.tsv")
EDGES_OUT = os.path.join(OUT_DIR, "p80_edges.tsv")

os.makedirs(OUT_DIR, exist_ok=True)

def load_anchor_sections(path):
    """
    Load anchor-derived section labels for families.
    Expects TSV with columns: family, section, count, fraction
    """
    fam_section = {}
    if not os.path.isfile(path):
        print(f"[WARN] Anchor file missing: {path}")
        return fam_section

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        # Handle possible variants in header naming
        cols = reader.fieldnames or []
        fam_col = "family" if "family" in cols else cols[0]
        sec_col = "section" if "section" in cols else (cols[1] if len(cols) > 1 else None)

        for row in reader:
            fam = row.get(fam_col, "").strip()
            sec = row.get(sec_col, "").strip() if sec_col else ""
            if not fam:
                continue
            # If family appears multiple times, prefer the section with highest count / fraction
            # Here we just overwrite; upstream already thresholded anchors to be clean.
            if sec:
                fam_section[fam] = sec

    print(f"[INFO] Loaded {len(fam_section)} anchor family→section mappings.")
    return fam_section

def load_family_graph(path):
    """
    Load family graph edges from TSV.
    Expects header: fam_i, fam_j, jaccard, section_i, section_j, same_section
    (or at least fam_i, fam_j, jaccard)
    """
    edges = []
    families = set()

    if not os.path.isfile(path):
        print(f"[ERR] Family graph file missing: {path}")
        return families, edges

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = None
        for row in reader:
            # Skip comments / blank lines
            if not row or row[0].startswith("#"):
                continue
            if header is None:
                header = row
                # normalize
                header = [h.strip() for h in header]
                continue

            data = dict(zip(header, row))
            fi = data.get("fam_i", "").strip()
            fj = data.get("fam_j", "").strip()
            if not fi or not fj:
                continue

            try:
                j = float(data.get("jaccard", "0").strip())
            except ValueError:
                continue

            families.add(fi)
            families.add(fj)

            edges.append({
                "fam_i": fi,
                "fam_j": fj,
                "jaccard": j,
            })

    print(f"[INFO] Loaded {len(edges)} edges among {len(families)} families from {path}.")
    return families, edges

def infer_sections_for_nodes(families, edges, anchor_sections):
    """
    Assign a section label to each family:
      - If in anchor_sections: use that
      - Else: infer from neighbors' anchor sections (majority vote)
      - Else: 'Unknown'
    """
    # Start with known anchors
    fam_sec = dict(anchor_sections)

    # Build adjacency for propagation
    neigh = defaultdict(list)
    for e in edges:
        fi, fj = e["fam_i"], e["fam_j"]
        neigh[fi].append(fj)
        neigh[fj].append(fi)

    # One pass of neighbor-based inference
    changed = True
    while changed:
        changed = False
        for f in families:
            if f in fam_sec:
                continue
            # Look at neighbors with known section
            secs = [fam_sec[n] for n in neigh[f] if n in fam_sec]
            if not secs:
                continue
            # Majority vote
            c = Counter(secs)
            best_sec, best_count = c.most_common(1)[0]
            if best_count >= 2:  # require at least 2 neighbors to agree
                fam_sec[f] = best_sec
                changed = True

    # Fill any remaining as Unknown
    for f in families:
        fam_sec.setdefault(f, "Unknown")

    return fam_sec

def compute_degrees(families, edges):
    deg = {f: 0 for f in families}
    for e in edges:
        fi, fj = e["fam_i"], e["fam_j"]
        if fi in deg:
            deg[fi] += 1
        if fj in deg:
            deg[fj] += 1
    return deg

def write_nodes(families, fam_sec, degrees, anchor_sections, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["family", "section", "degree", "is_anchor"])
        for fam in sorted(families):
            sec = fam_sec.get(fam, "Unknown")
            deg = degrees.get(fam, 0)
            is_anchor = 1 if fam in anchor_sections else 0
            w.writerow([fam, sec, deg, is_anchor])
    print(f"[OK] Wrote nodes → {path}")

def write_edges(edges, fam_sec, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["fam_i", "fam_j", "jaccard", "section_i", "section_j", "same_section"])
        for e in edges:
            fi, fj = e["fam_i"], e["fam_j"]
            j = e["jaccard"]
            si = fam_sec.get(fi, "Unknown")
            sj = fam_sec.get(fj, "Unknown")
            same = 1 if si == sj and si != "Unknown" else 0
            w.writerow([fi, fj, f"{j:.3f}", si, sj, same])
    print(f"[OK] Wrote edges → {path}")

def main():
    print("=== Phase 80: Sectional family graph export ===")

    anchor_sections = load_anchor_sections(F_ANCHORS)
    families, edges = load_family_graph(F_GRAPH)

    if not edges or not families:
        print("[ERR] No edges or families loaded; aborting.")
        return

    fam_sec = infer_sections_for_nodes(families, edges, anchor_sections)
    degrees = compute_degrees(families, edges)

    write_nodes(families, fam_sec, degrees, anchor_sections, NODES_OUT)
    write_edges(edges, fam_sec, EDGES_OUT)

    # Quick summary
    sec_counts = Counter(fam_sec.values())
    print("[SUMMARY] Families per section:")
    for sec, c in sorted(sec_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {sec:12s} {c:4d}")

    print("=== Phase 80 complete ===")

if __name__ == "__main__":
    main()
