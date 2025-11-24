#!/usr/bin/env python3
import os, sys, hashlib
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
IN=os.environ.get("IN","Phase58/out/prefix_suffix_freq.tsv")
OUTD=os.environ.get("OUTD","figures"); os.makedirs(OUTD, exist_ok=True)
try:
    df=pd.read_csv(IN, sep="\t")
except Exception as e:
    sys.stderr.write(f"[error] cannot read %s: %s\n" % (IN, e)); sys.exit(1)

need_base={"prefix","suffix"}
if not need_base.issubset(df.columns):
    sys.stderr.write(f"[error] {IN} missing {sorted(need_base - set(df.columns))}\n"); sys.exit(1)

# accept either 'count' or 'weight'
valcol = "count" if "count" in df.columns else ("weight" if "weight" in df.columns else None)
if valcol is None:
    sys.stderr.write(f"[error] {IN} needs a numeric 'count' or 'weight' column\n"); sys.exit(1)

with open(IN,"rb") as f: import hashlib; print(f"[hash] {IN} md5={hashlib.md5(f.read()).hexdigest()}")

mat=df.pivot_table(index="prefix", columns="suffix", values=valcol, aggfunc="sum", fill_value=0)
mat=np.log1p(mat)

plt.figure(figsize=(7,6))
im=plt.imshow(mat.values, aspect="auto")
plt.colorbar(im, fraction=0.046, pad=0.04)
plt.xticks(range(len(mat.columns)), mat.columns, rotation=90)
plt.yticks(range(len(mat.index)), mat.index)
plt.xlabel("Suffix"); plt.ylabel("Prefix")
plt.title("Figure 2.5 – Prefix × Suffix Frequency (log1p)")
plt.tight_layout()
plt.savefig(f"{OUTD}/fig2_5_prefix_suffix_heatmap.png")
plt.savefig(f"{OUTD}/fig2_5_prefix_suffix_heatmap.pdf")
print("[ok] fig2_5 written")
