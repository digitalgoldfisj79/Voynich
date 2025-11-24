#!/usr/bin/env python3
import os, sys, hashlib
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
IN=os.environ.get("IN","Phase59/out/prefix_suffix_edges.tsv")
OUTD=os.environ.get("OUTD","figures"); os.makedirs(OUTD, exist_ok=True)
try:
    df=pd.read_csv(IN, sep="\t")
except Exception as e:
    sys.stderr.write(f"[error] cannot read {IN}: {e}\n"); sys.exit(1)
need={"prefix","suffix","weight"}
miss=need - set(df.columns)
if miss: sys.stderr.write(f"[error] {IN} missing {sorted(miss)}\n") or sys.exit(1)
with open(IN,"rb") as f: print(f"[hash] {IN} md5={hashlib.md5(f.read()).hexdigest()}")
df=df.sort_values("weight", ascending=False).head(200)
prefixes=sorted(df["prefix"].unique().tolist())
suffixes=sorted(df["suffix"].unique().tolist())
yL=np.linspace(0,1,len(prefixes)); yR=np.linspace(0,1,len(suffixes))
posL={p:(0.1,yL[i]) for i,p in enumerate(prefixes)}
posR={s:(0.9,yR[i]) for i,s in enumerate(suffixes)}
plt.figure(figsize=(7,6))
for p,(x,y) in posL.items():
    plt.plot(x,y,marker="o"); plt.text(x-0.02,y,p,ha="right",va="center",fontsize=8)
for s,(x,y) in posR.items():
    plt.plot(x,y,marker="o"); plt.text(x+0.02,y,s,ha="left",va="center",fontsize=8)
wmin,wmax=df["weight"].min(), df["weight"].max()
den=(wmax-wmin) if wmax>wmin else 1.0
for _,r in df.iterrows():
    x1,y1=posL[r["prefix"]]; x2,y2=posR[r["suffix"]]
    w=0.5+3.0*(r["weight"]-wmin)/den
    plt.plot([x1,x2],[y1,y2], linewidth=w, alpha=0.5)
plt.axis("off"); plt.title("Figure 7.1 – Prefix–Suffix Connectivity (top edges)")
plt.tight_layout()
plt.savefig(f"{OUTD}/fig7_1_prefix_suffix_network.png")
plt.savefig(f"{OUTD}/fig7_1_prefix_suffix_network.pdf")
print("[ok] fig7_1 written")
