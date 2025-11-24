#!/usr/bin/env python3
import sys, csv, math
from collections import defaultdict

attr_path = sys.argv[1]     # Phase110/out/p112_attribution.norm.tsv
sect_path = sys.argv[2]     # Phase77/...norm.tsv
out_join = sys.argv[3]      # Phase110/out/p112_attribution_with_sections.tsv

# Load attribution (needs family_norm, delta)
with open(attr_path, "r", encoding="utf-8", newline="") as f:
    attr = list(csv.DictReader(f, dialect=csv.excel_tab))
if not attr:
    sys.exit("[ERR] Empty attribution file")

# Load sections (needs family_norm, section)
with open(sect_path, "r", encoding="utf-8", newline="") as f:
    sec = list(csv.DictReader(f, dialect=csv.excel_tab))
if not sec:
    sys.exit("[ERR] Empty section file")

# Find section column name
sec_col = None
for cand in ("section", "Section", "dominant_section", "dominant"):
    if cand in sec[0]:
        sec_col = cand
        break
if sec_col is None:
    sys.exit("[ERR] No section-like column in section file")

# Index sections by family_norm (if duplicates, take the most frequent by count/fraction if present)
sec_index = {}
for r in sec:
    key = r.get("family_norm", "")
    if not key:
        continue
    # Prefer entries that have 'count' or 'fraction' if multiple rows per family exist
    if key not in sec_index:
        sec_index[key] = r
    else:
        def score(row):
            c = float(row.get("count", "0") or "0")
            fr = float(row.get("fraction", "0") or "0")
            return (c, fr)
        if score(r) > score(sec_index[key]):
            sec_index[key] = r

# Join
joined = []
unmatched_attr = 0
for r in attr:
    fam = r.get("family_norm", "")
    out = dict(r)
    srow = sec_index.get(fam)
    if srow:
        out["section"] = srow.get(sec_col, "Unknown")
    else:
        out["section"] = "Unknown"
        unmatched_attr += 1
    joined.append(out)

# Write joined table
fields = list(joined[0].keys())
with open(out_join, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, dialect=csv.excel_tab)
    w.writeheader()
    for r in joined:
        w.writerow(r)

# Per-section stats for delta
acc = defaultdict(list)
for r in joined:
    try:
        d = float(r.get("delta", "nan"))
    except:
        continue
    if math.isnan(d):
        continue
    acc[r["section"]].append(d)

print("=== Sectional mean Δ (sim_latin - sim_arabic) ===")
for s, vals in sorted(acc.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    n = len(vals)
    mean = sum(vals)/n if n else float("nan")
    print(f"{s}\tmeanΔ={mean:.4f}\tn={n}")
print(f"[INFO] Unmatched attribution families (no section): {unmatched_attr}")
print(f"[OK] Joined → {out_join}")
