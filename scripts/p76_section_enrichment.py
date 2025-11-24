#!/usr/bin/env python3
import os, pandas as pd, re
from collections import defaultdict

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
FAMS = os.path.join(BASE, "Phase75/out/p75_families.tsv")
SEC = os.path.join(BASE, "meta/folio_sections.tsv")
OUT = os.path.join(BASE, "Phase76/out/p76_section_enrichment.tsv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# --- Load section map
secmap = dict(pd.read_csv(SEC, sep="\t", header=None).values)

# --- Helper to extract bare folio ID
def get_folio(tok: str) -> str:
    m = re.search(r"f\d+[rv]", tok)
    return m.group(0) if m else None

# --- Load families
df = pd.read_csv(FAMS, sep="\t")
counts = defaultdict(lambda: defaultdict(int))

for _, row in df.iterrows():
    fam = row["family_signature"]
    examples = str(row["examples"])
    for tok in examples.split(","):
        folio = get_folio(tok)
        section = secmap.get(folio, "Unknown")
        counts[fam][section] += 1

# --- Compute totals
rows = []
for fam, sects in counts.items():
    total = sum(sects.values())
    for s, c in sects.items():
        frac = c / total if total > 0 else 0
        rows.append((fam, s, c, round(frac, 3)))

out = pd.DataFrame(rows, columns=["family", "section", "count", "fraction"])
out.to_csv(OUT, sep="\t", index=False)
print(f"[OK] Section enrichment written → {OUT}")
print(out.head(20))
