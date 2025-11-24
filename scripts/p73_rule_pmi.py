#!/usr/bin/env python3
import pandas as pd, itertools, math, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFILE = os.path.join(BASE, "Phase70", "out", "p70_token_hits.tsv")
OUTFILE = os.path.join(BASE, "Phase73", "out", "p73_rule_pmi.tsv")
os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)

df = pd.read_csv(INFILE, sep="\t")
rulesets = [set(r.split(",")) for r in df["rules"]]
counts = {}
for r in itertools.chain.from_iterable(rulesets):
    counts[r] = counts.get(r,0)+1
edges = {}
for s in rulesets:
    for a,b in itertools.combinations(sorted(s),2):
        edges[(a,b)] = edges.get((a,b),0)+1

rows=[]
N=len(df)
for (a,b),co in edges.items():
    pa, pb = counts[a]/N, counts[b]/N
    pxy = co/N
    pmi = math.log2(pxy/(pa*pb)) if pxy>0 else 0
    if co>=5 and pmi>=0.5:
        rows.append((a,b,co,round(pmi,3)))
pd.DataFrame(rows,columns=["rule_i","rule_j","cooc","PMI_bits"]).to_csv(OUTFILE,sep="\t",index=False)
print(f"[OK] {len(rows)} edges → {OUTFILE}")
