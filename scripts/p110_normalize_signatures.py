#!/usr/bin/env python3
import sys, csv

in_path = sys.argv[1]
out_path = sys.argv[2]

with open(in_path, "r", newline="", encoding="utf-8") as f:
    sniffer = csv.Sniffer()
    sample = f.read(2048)
    f.seek(0)
    dialect = csv.excel_tab
    reader = csv.DictReader(f, dialect=dialect)
    rows = list(reader)

fieldnames = reader.fieldnames or []
fam_col = None
for cand in ("family", "family_signature", "signature"):
    if cand in fieldnames:
        fam_col = cand
        break
if fam_col is None:
    sys.exit("[ERR] No family/family_signature/signature column found in %s" % in_path)

def normalise(sig: str) -> str:
    if sig is None:
        return ""
    parts = [p for p in str(sig).replace(" ", "").split("-") if p]
    parts.sort()
    return "-".join(parts)

# add/replace family_norm
if "family_norm" not in fieldnames:
    fieldnames = fieldnames + ["family_norm"]

for r in rows:
    r["family_norm"] = normalise(r.get(fam_col, ""))

with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, dialect=csv.excel_tab)
    w.writeheader()
    for r in rows:
        w.writerow(r)
