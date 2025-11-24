#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "[S60] Clause-role × Register tests"

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
OUTD="$BASE/PhaseS/out"

S35="$OUTD/s35_clause_role_patterns.tsv"
S47="$OUTD/s47_clause_semantic_skeletons.tsv"
S50="$OUTD/s50_folio_register_matrix.tsv"

OUT_CONT="$OUTD/s60_clause_role_contingency.tsv"
OUT_EX="$OUTD/s60_clause_role_examples.tsv"
OUT_REP="$OUTD/s60_clause_role_report.txt"

echo "[S60] BASE: $BASE"
echo "[S60] S35:  $S35"
echo "[S60] S47:  $S47"
echo "[S60] S50:  $S50"

python3 << 'EOF'
import pandas as pd
import numpy as np
import sys, random
from collections import Counter

S35 = pd.read_csv("$S35", sep="\t")
S47 = pd.read_csv("$S47", sep="\t")
S50 = pd.read_csv("$S50", sep="\t")

# ---- NORMALISE FOLIO ----
def norm(x):
    if isinstance(x,str):
        return x.lower().replace(".png","").replace(".jpg","").replace(".jpeg","")
    return x

for df in (S35,S47,S50):
    for col in ["folio","folio_norm","folio_id"]:
        if col in df.columns:
            df[col] = df[col].apply(norm)

# pick folio column
folio_col = None
for c in ["folio_norm","folio","folio_id"]:
    if c in S35.columns:
        folio_col=c
        break
if folio_col is None:
    raise ValueError("[S60] Could not find folio column in S35")

reg_col=None
for c in ["register","dominant_semantic_register"]:
    if c in S50.columns:
        reg_col=c
        break
if reg_col is None:
    raise ValueError("[S60] No register column in S50")

# ---- JOIN ----
merged = pd.merge(S35, S50[[folio_col,reg_col]], on=folio_col, how="inner")
print("[S60] Rows after join:", len(merged))

# ---- Define clause pattern signature ----
def signature(row):
    a = row.get("agent_role","")
    p = row.get("process_suffix","")
    b = row.get("patient_role","")
    return f"{a}>{p}>{b}"

if "agent_role" in merged.columns and "patient_role" in merged.columns:
    pass
else:
    raise ValueError("[S60] Missing agent_role/patient_role in S35")

merged["sig"] = merged.apply(signature, axis=1)

# ---- Build contingency ----
cont = merged.groupby([reg_col,"sig"]).size().reset_index(name="count")

# ---- Wide format ----
wide = cont.pivot(index=reg_col, columns="sig", values="count").fillna(0).astype(int)
wide.to_csv("$OUT_CONT", sep="\t")

# ---- Compute χ² and Cramer's V ----
O = wide.values
row_sums = O.sum(axis=1, keepdims=True)
col_sums = O.sum(axis=0, keepdims=True)
N = O.sum()
E = row_sums @ col_sums / N

chi2 = ((O-E)**2 / (E+1e-9)).sum()
k = min(O.shape)
cramer_v = np.sqrt(chi2 / (N*(k-1)))

# ---- Permutation test ----
iters = 200
v_null=[]
labels = merged[reg_col].values.copy()
for _ in range(iters):
    perm = np.random.permutation(labels)
    tmp = merged.copy()
    tmp[reg_col] = perm
    cc = tmp.groupby([reg_col,"sig"]).size().reset_index(name="count")
    w = cc.pivot(index=reg_col, columns="sig", values="count").fillna(0).astype(int)
    O2 = w.values
    row_sums2 = O2.sum(axis=1, keepdims=True)
    col_sums2 = O2.sum(axis=0, keepdims=True)
    N2 = O2.sum()
    E2 = row_sums2 @ col_sums2 / N2
    chi2_2 = ((O2-E2)**2 / (E2+1e-9)).sum()
    v2 = np.sqrt(chi2_2 / (N2*(k-1)))
    v_null.append(v2)

# ---- Examples of strong differences ----
examples=[]
for sig in wide.columns:
    a = wide.loc["REGISTER_A",sig] if "REGISTER_A" in wide.index else 0
    b = wide.loc["REGISTER_B",sig] if "REGISTER_B" in wide.index else 0
    if abs(a-b) >= 5:  # strong difference
        examples.append((sig,a,b))
ex = pd.DataFrame(examples, columns=["sig","A_count","B_count"])
ex.to_csv("$OUT_EX", sep="\t", index=False)

# ---- Write report ----
with open("$OUT_REP","w") as f:
    f.write("S60 – Clause-role × Register tests\n")
    f.write("=================================\n\n")
    f.write(f"Rows merged: {len(merged)}\n")
    f.write("\nChi-square stats:\n")
    f.write(f"  chi² = {chi2:.4f}\n")
    f.write(f"  Cramer's V = {cramer_v:.4f}\n")
    f.write(f"  df = {wide.size - wide.shape[0] - wide.shape[1] + 1}\n")
    f.write("\nPermutation baseline:\n")
    f.write(f"  mean V_null = {np.mean(v_null):.4f}\n")
    f.write(f"  sd V_null   = {np.std(v_null):.4f}\n")
    f.write(f"  95th pct    = {np.percentile(v_null,95):.4f}\n")
    f.write("\nStrongly differing clause signatures:\n")
    for sig,a,b in examples:
        f.write(f"  {sig}: A={a}, B={b}\n")

print("[S60] Done.")
EOF
