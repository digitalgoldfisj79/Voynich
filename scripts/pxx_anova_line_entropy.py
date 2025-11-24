#!/usr/bin/env python3
import os
import csv
import math
import statistics
from collections import defaultdict

# ---------- Helper to find files ----------

def first_existing(paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None

# ---------- Locate inputs ----------

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root

line_paths = [
    os.path.join(BASE, "Phase95", "out", "p95_line_metrics.tsv"),
    os.path.join(BASE, "Phase95", "p95_line_metrics.tsv"),
    os.path.join(BASE, "p95_line_metrics.tsv"),
]

sec_paths = [
    os.path.join(BASE, "meta", "folio_sections.tsv"),
    os.path.join(BASE, "folio_sections.tsv"),
]

line_file = first_existing(line_paths)
sec_file = first_existing(sec_paths)

print("=== Line entropy ANOVA (v2) ===")

if not line_file:
    print("[ERR] Could not find p95_line_metrics TSV in any expected location.")
    print("      Tried:")
    for p in line_paths:
        print("       -", p)
    raise SystemExit(1)

if not sec_file:
    print("[ERR] Could not find sections_map.tsv in any expected location.")
    print("      Tried:")
    for p in sec_paths:
        print("       -", p)
    raise SystemExit(1)

print(f"[INFO] Using line metrics: {line_file}")
print(f"[INFO] Using folio→section map: {sec_file}")

# ---------- Load folio → section ----------

folio_to_section = {}
with open(sec_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if not row or row[0].lower() == "folio":
            continue
        fol, sec = row[0].strip(), row[1].strip()
        if fol:
            folio_to_section[fol] = sec

if not folio_to_section:
    print("[ERR] folio_to_section map is empty after parsing.")
    raise SystemExit(1)

# ---------- Load line metrics ----------

lines = []
with open(line_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    # Expect at least: folio, line_no, mean_H1_local_bits
    for row in reader:
        fol = row.get("folio", "").strip()
        if not fol:
            continue
        sec = folio_to_section.get(fol)
        if not sec:
            # skip lines with unknown section
            continue
        try:
            line_no = int(row.get("line_no", "0"))
        except ValueError:
            continue
        try:
            h = float(row.get("mean_H1_local_bits", "nan"))
        except ValueError:
            continue
        if math.isnan(h):
            continue
        lines.append((fol, line_no, sec, h))

if not lines:
    print("[ERR] No usable line records after merge with sections + entropy.")
    raise SystemExit(1)

print(f"[INFO] Loaded {len(lines)} lines with section + entropy.")

# ---------- Derive position category per folio ----------

max_line_per_folio = defaultdict(int)
for fol, line_no, sec, h in lines:
    if line_no > max_line_per_folio[fol]:
        max_line_per_folio[fol] = line_no

records = []
for fol, line_no, sec, h in lines:
    max_ln = max_line_per_folio[fol]
    if max_ln <= 0:
        continue
    if line_no == 1:
        pos = "initial"
    elif line_no == max_ln:
        pos = "final"
    else:
        pos = "medial"
    records.append((sec, pos, h))

if not records:
    print("[ERR] No records after assigning position categories.")
    raise SystemExit(1)

sections = sorted({r[0] for r in records})
positions = ["initial", "medial", "final"]

print(f"[INFO] Sections: {sections}")
print(f"[INFO] Positions: {positions}")

# ---------- Organise data for 2-way ANOVA ----------

# data[(sec, pos)] = [H1, H1, ...]
data = defaultdict(list)
all_values = []

for sec, pos, h in records:
    data[(sec, pos)].append(h)
    all_values.append(h)

if not all_values:
    print("[ERR] No entropy values collected.")
    raise SystemExit(1)

grand_mean = statistics.mean(all_values)

# group means
mean_sec = {}
mean_pos = {}
mean_cell = {}

for sec in sections:
    vals = [h for (s, p), hs in data.items() if s == sec for h in hs]
    if vals:
        mean_sec[sec] = statistics.mean(vals)

for pos in positions:
    vals = [h for (s, p), hs in data.items() if p == pos for h in hs]
    if vals:
        mean_pos[pos] = statistics.mean(vals)

for sec in sections:
    for pos in positions:
        vals = data.get((sec, pos), [])
        if vals:
            mean_cell[(sec, pos)] = statistics.mean(vals)

# ---------- Sum of squares ----------

# Total
SST = sum((h - grand_mean) ** 2 for h in all_values)

# Section (A)
SSA = 0.0
for sec in sections:
    vals = [h for (s, p), hs in data.items() if s == sec for h in hs]
    if not vals:
        continue
    m = mean_sec[sec]
    SSA += len(vals) * (m - grand_mean) ** 2

# Position (B)
SSB = 0.0
for pos in positions:
    vals = [h for (s, p), hs in data.items() if p == pos for h in hs]
    if not vals:
        continue
    m = mean_pos[pos]
    SSB += len(vals) * (m - grand_mean) ** 2

# Interaction (A×B)
SSAB = 0.0
for (sec, pos), vals in data.items():
    m_cell = mean_cell[(sec, pos)]
    m_sec = mean_sec[sec]
    m_pos = mean_pos[pos]
    SSAB += len(vals) * (m_cell - m_sec - m_pos + grand_mean) ** 2

# Error
SSE = SST - SSA - SSB - SSAB

# degrees of freedom
N = len(all_values)
a = len(sections)
b = len(positions)

dfA = a - 1
dfB = b - 1
dfAB = dfA * dfB
dfE = N - a * b

def safe_F(SS, df, SSE, dfE):
    if df <= 0 or dfE <= 0 or SSE <= 0:
        return float('nan')
    return (SS / df) / (SSE / dfE)

FA = safe_F(SSA, dfA, SSE, dfE)
FB = safe_F(SSB, dfB, SSE, dfE)
FAB = safe_F(SSAB, dfAB, SSE, dfE)

print("=== ANOVA summary (mean_H1_local_bits) ===")
print(f"N (lines)                    = {N}")
print(f"Grand mean                   = {grand_mean:.4f}")
print()
print(f"SSA (Section)                = {SSA:.4f}, df={dfA}, F={FA:.3f}")
print(f"SSB (Position)               = {SSB:.4f}, df={dfB}, F={FB:.3f}")
print(f"SSAB (Interaction)           = {SSAB:.4f}, df={dfAB}, F={FAB:.3f}")
print(f"SSE (Error)                  = {SSE:.4f}, df={dfE}")
print(f"SST (Total)                  = {SST:.4f}")
print("=== Done ===")
