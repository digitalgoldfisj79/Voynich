#!/usr/bin/env python3
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFILE = os.path.join(BASE, "Phase72", "out", "p72_rule_pmi_network.tsv")
OUTDIR = os.path.join(BASE, "Phase75", "out")
os.makedirs(OUTDIR, exist_ok=True)
OUTFILE = os.path.join(OUTDIR, "p75_rule_communities.tsv")

# Simple label propagation for undirected graph
adj = {}
with open(INFILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip() or line.startswith("#"):
            continue
        a,b,fi,fj,cooc,pmi = line.strip().split("\t")
        # a,b are like 'chargram:che:left'; use them as node ids
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

# init labels: each node its own
labels = {n: n for n in adj.keys()}

changed = True
while changed:
    changed = False
    for n in adj:
        if not adj[n]:
            continue
        # choose most common neighbour label
        counts = {}
        for nb in adj[n]:
            lab = labels[nb]
            counts[lab] = counts.get(lab, 0) + 1
        best = max(counts.items(), key=lambda x: x[1])[0]
        if best != labels[n]:
            labels[n] = best
            changed = True

# compress labels to C1..Ck
label_map = {}
for lab in sorted(set(labels.values())):
    label_map[lab] = f"C{len(label_map)+1}"

with open(OUTFILE, "w", encoding="utf-8") as out:
    out.write("rule_label\tcommunity\n")
    for n in sorted(adj.keys()):
        out.write(f"{n}\t{label_map[labels[n]]}\n")

print(f"[OK] Wrote rule communities → {OUTFILE}")
