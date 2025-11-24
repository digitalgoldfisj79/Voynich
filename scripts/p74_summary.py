#!/usr/bin/env python3
import pandas as pd, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTFILE = os.path.join(BASE,"Phase74","out","p74_summary.txt")
os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)

tok_hits = pd.read_csv(os.path.join(BASE,"Phase70","out","p70_token_hits.tsv"),sep="\t")
fam = pd.read_csv(os.path.join(BASE,"Phase71","out","p71_token_families.tsv"),sep="\t")
pmi = pd.read_csv(os.path.join(BASE,"Phase73","out","p73_rule_pmi.tsv"),sep="\t")

with open(OUTFILE,"w") as f:
    f.write("=== Phase74 Summary ===\n")
    f.write(f"Tokens w/ rules: {len(tok_hits)}\n")
    f.write(f"Families: {len(fam)} (mean size {fam['family_size'].mean():.1f})\n")
    f.write(f"PMI edges: {len(pmi)}\n")
    f.write(f"Mean PMI: {pmi['PMI_bits'].mean():.2f}\n")
print(f"[OK] Summary → {OUTFILE}")
