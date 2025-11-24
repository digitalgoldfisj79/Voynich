#!/usr/bin/env python3
import csv
from collections import defaultdict
import os

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
OUTD = os.path.join(BASE, "PhaseS", "out")
METAD = os.path.join(BASE, "metadata")
section_map_path = os.path.join(METAD, "folio_sections.tsv")

currier_path = os.path.join(OUTD, "currier_map.tsv")
section_map_path = os.path.join(METAD, "folio_sections.tsv")
out_path = os.path.join(OUTD, "s45_section_currier_counts.tsv")

# 1. Load Currier map: folio -> A/B
folio_to_currier = {}
with open(currier_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        folio, cur = parts[0], parts[1]
        if cur in ("A", "B"):
            folio_to_currier[folio] = cur

# 2. Load explicit section map: folio -> section
folio_to_section = {}
with open(section_map_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        folio, section = parts[0], parts[1]
        # Skip header line if present
        if folio.lower() == "folio":
            continue
        folio_to_section[folio] = section

# 3. Count folios per (section, Currier)
section_counts = defaultdict(lambda: {"A": 0, "B": 0})

for folio, cur in folio_to_currier.items():
    section = folio_to_section.get(folio, "Unknown")
    if cur in ("A", "B"):
        section_counts[section][cur] += 1

# 4. Write output
with open(out_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([
        "section",
        "n_folios_A",
        "n_folios_B",
        "n_folios_total",
        "prop_A",
        "prop_B",
    ])
    for section in sorted(section_counts.keys()):
        A = section_counts[section]["A"]
        B = section_counts[section]["B"]
        total = A + B
        prop_A = A / total if total > 0 else 0.0
        prop_B = B / total if total > 0 else 0.0
        writer.writerow([
            section,
            A,
            B,
            total,
            f"{prop_A:.4f}",
            f"{prop_B:.4f}",
        ])

print(f"[S45] Wrote section × Currier counts to: {out_path}")
