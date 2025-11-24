#!/usr/bin/env python3
import os, sys, hashlib
import pandas as pd
import matplotlib.pyplot as plt
IN=os.environ.get("IN","Phase70/out/entropy_by_pos.tsv")
OUTD=os.environ.get("OUTD","figures"); os.makedirs(OUTD, exist_ok=True)
try:
    df=pd.read_csv(IN, sep="\t")
except Exception as e:
    sys.stderr.write(f"[error] cannot read %s: %s\n" % (IN, e)); sys.exit(1)

need={"position","mean_H","sd_H"}
miss=need - set(df.columns)
if miss:
    sys.stderr.write(f"[error] {IN} missing {sorted(miss)}\n"); sys.exit(1)

# coerce to numeric
for c in ["position","mean_H","sd_H"]:
    df[c]=pd.to_numeric(df[c], errors="coerce")
df=df.dropna(subset=["position","mean_H"])  # sd_H can be NaN; treat as 0
df["sd_H"]=df["sd_H"].fillna(0.0)
df=df.sort_values("position")

with open(IN,"rb") as f: print(f"[hash] {IN} md5={__import__('hashlib').md5(f.read()).hexdigest()}")

plt.figure(figsize=(6,4))
plt.plot(df["position"], df["mean_H"], marker="o")
plt.fill_between(df["position"], df["mean_H"]-df["sd_H"], df["mean_H"]+df["sd_H"], alpha=0.2)
plt.xlabel("Word position (1 = initial)"); plt.ylabel("Entropy (bits)")
plt.title("Figure 7.2 – Entropy by Word Position")
plt.tight_layout()
plt.savefig(f"{OUTD}/fig7_2_entropy_by_pos.png")
plt.savefig(f"{OUTD}/fig7_2_entropy_by_pos.pdf")
print("[ok] fig7_2 written")
