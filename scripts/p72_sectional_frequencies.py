#!/usr/bin/env python3
import pandas as pd
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(BASE, "meta", "folio_sections.tsv")
INFILE = os.path.join(BASE, "Phase71", "out", "p71_token_families.tsv")
OUTDIR = os.path.join(BASE, "Phase72", "out")
OUTFILE = os.path.join(OUTDIR, "p72_family_sections.tsv")

os.makedirs(OUTDIR, exist_ok=True)

if not os.path.isfile(INFILE):
    raise SystemExit(f"[ERR] Missing input families file: {INFILE}")

families = pd.read_csv(INFILE, sep="\t")

# If no folio_sections map, fall back to UNKNOWN so the script still runs
secmap = {}
if os.path.isfile(META):
    m = pd.read_csv(META, sep="\t", header=None)
    # Expect: folio_id \t section_label
    for row in m.itertuples(index=False):
        folio, sec = str(row[0]).strip(), str(row[1]).strip()
        if folio and sec:
            secmap[folio] = sec
    print(f"[INFO] Loaded {len(secmap)} folio→section mappings from {META}")
else:
    print(f"[WARN] No {META} found. All tokens will be labeled section='UNKNOWN'.")

rows = []
for row in families.itertuples(index=False):
    fam = row.family_key
    tokens = str(row.token).split(",") if isinstance(row.token, str) else []
    section_counts = {}
    for t in tokens:
        # Expect tokens like f18r.1.qokedy or similar; adapt if needed
        m = re.match(r"^f(\d+[rv])", t)
        if m:
            folio = m.group(1)
            sec = secmap.get(folio, "UNKNOWN")
        else:
            sec = "UNKNOWN"
        section_counts[sec] = section_counts.get(sec, 0) + 1
    for sec, count in section_counts.items():
        rows.append((fam, sec, count))

pd.DataFrame(rows, columns=["family", "section", "count"]).to_csv(
    OUTFILE, sep="\t", index=False
)
print(f"[OK] Wrote {OUTFILE}")
