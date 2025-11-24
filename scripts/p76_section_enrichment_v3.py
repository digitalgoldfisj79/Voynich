#!/usr/bin/env python3
import os, pandas as pd, re
from collections import defaultdict

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
FAMS = os.path.join(BASE, "Phase75/out/p75_families.tsv")
TOKS = os.path.join(BASE, "p6_voynich_tokens.txt")
SEC  = os.path.join(BASE, "meta/folio_sections.tsv")
OUT  = os.path.join(BASE, "Phase76/out/p76_section_enrichment.tsv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# --- Load section map
secmap = dict(pd.read_csv(SEC, sep="\t", header=None).values)

# --- Load canonical tokens with folio info
toks = []
with open(TOKS) as f:
    for line in f:
        m = re.match(r"^<f(\d+[rv])\.\d+>\s+(\S+)", line.strip())
        if m:
            folio, token = f"f{m.group(1)}", m.group(2)
            toks.append((token, folio))
tokmap = dict(toks)

# --- Load families
df = pd.read_csv(FAMS, sep="\t")
counts = defaultdict(lambda: defaultdict(int))

for _, row in df.iterrows():
    fam = row["family_signature"]
    examples = str(row["examples"]).split(",")
    for tok in examples:
        tok = tok.strip()
        folio = tokmap.get(tok)
        section = secmap.get(folio, "Unknown")
        counts[fam][section] += 1

# --- Aggregate counts and fractions
rows = []
for fam, sects in counts.items():
    total = sum(sects.values())
    for s, c in sects.items():
        frac = c / total if total else 0
        rows.append((fam, s, c, round(frac, 3)))

out = pd.DataFrame(rows, columns=["family", "section", "count", "fraction"])
out.to_csv(OUT, sep="\t", index=False)

print(f"[OK] Section enrichment written → {OUT}")
print(out.head(20))
