#!/usr/bin/env python3
import pandas as pd, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFILE = os.path.join(BASE, "Phase70", "out", "p70_token_hits.tsv")
OUTFILE = os.path.join(BASE, "Phase71", "out", "p71_token_families.tsv")
os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)

df = pd.read_csv(INFILE, sep="\t")
df["family_key"] = df["rules"].apply(lambda x: "-".join(sorted(x.split(","))))
families = df.groupby("family_key")["token"].apply(list).reset_index()
families["family_size"] = families["token"].apply(len)
families.to_csv(OUTFILE, sep="\t", index=False)
print(f"[OK] {len(families)} families → {OUTFILE}")
