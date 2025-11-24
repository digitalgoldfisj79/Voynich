#!/data/data/com.termux/files/usr/bin/sh
set -eu

echo "[S50] Building register heatmap + transitions..."

python3 << 'EOF'
import pandas as pd
import re

# --- Input paths ---
p49c_path = "PhaseS/out/s49c_folio_semantic_profiles.tsv"
sec_path  = "metadata/folio_sections.tsv"
cur_path  = "PhaseS/out/currier_map.tsv"

# --- Load data ---
p49c = pd.read_csv(p49c_path, sep="\t")
sec  = pd.read_csv(sec_path,  sep="\t")
cur  = pd.read_csv(cur_path,  sep="\t", header=None, names=["folio", "currier"])

def norm_folio(f):
    s = str(f)
    if ">" in s:
        s = s.split(">", 1)[0]
    return s.strip()

p49c["folio"] = p49c["folio"].apply(norm_folio)
sec["folio"]  = sec["folio"].apply(norm_folio)
cur["folio"]  = cur["folio"].apply(norm_folio)

# Keep only clean Currier labels (A/B)
cur = cur[cur["currier"].isin(["A", "B"])]

# --- Merge semantic profiles + sections + Currier ---
df = p49c.merge(sec, on="folio", how="left")
df = df.merge(cur, on="folio", how="left")

# --- Natural folio order: f<number><r|v><idx?> ---
def folio_key(f):
    s = str(f)
    m = re.match(r"^f(\d+)([rv])(\d*)$", s)
    if not m:
        # push weird things to the end, keep stable secondary sort
        return (999, 2, s)
    num = int(m.group(1))
    side = 0 if m.group(2) == "r" else 1
    idx = int(m.group(3)) if m.group(3) else 0
    return (num, side, idx)

keys = df["folio"].apply(folio_key)
df["folio_num"]  = keys.apply(lambda t: t[0])
df["folio_side"] = keys.apply(lambda t: t[1])
df["folio_idx"]  = keys.apply(lambda t: t[2])

df = df.sort_values(["folio_num", "folio_side", "folio_idx"])

# --- Map dominant_semantic_register to A/B-style register label ---
def reg_label(dom):
    if dom == "PROC_DOM":
        return "REGISTER_B"   # procedural / Currier-B-like
    if dom in ("BOT_DOM", "BIO_DOM"):
        return "REGISTER_A"   # descriptive / Currier-A-like
    return "UNKNOWN"

df["register"] = df["dominant_semantic_register"].apply(reg_label)

# 1) Full folio-level register matrix
df_out = df.drop(columns=["folio_num", "folio_side", "folio_idx"])
df_out.to_csv("PhaseS/out/s50_folio_register_matrix.tsv", sep="\t", index=False)

# 2) Register transition points
rows = []
prev = None
for _, r in df.iterrows():
    if prev is not None and r["register"] != prev["register"]:
        rows.append({
            "from_folio": prev["folio"],
            "to_folio": r["folio"],
            "from_reg": prev["register"],
            "to_reg": r["register"],
            "section_from": prev.get("section", ""),
            "section_to": r.get("section", ""),
            "currier_from": prev.get("currier", ""),
            "currier_to": r.get("currier", ""),
        })
    prev = r

pd.DataFrame(rows).to_csv("PhaseS/out/s50_transition_points.tsv",
                          sep="\t", index=False)

# 3) Collapsed register blocks
blocks = []
current = None
for _, r in df.iterrows():
    reg = r["register"]
    fol = r["folio"]
    if current is None:
        current = {"register": reg, "start": fol, "end": fol, "n_folios": 1}
    else:
        if reg == current["register"]:
            current["end"] = fol
            current["n_folios"] += 1
        else:
            blocks.append(current)
            current = {"register": reg, "start": fol, "end": fol, "n_folios": 1}
if current is not None:
    blocks.append(current)

pd.DataFrame(blocks).to_csv("PhaseS/out/s50_register_blocks.tsv",
                            sep="\t", index=False)

# 4) Simple ASCII heatmap
with open("PhaseS/out/s50_register_heatmap.txt", "w") as f:
    for _, r in df.iterrows():
        reg = r["register"]
        if reg == "REGISTER_A":
            symbol = "A"
        elif reg == "REGISTER_B":
            symbol = "B"
        else:
            symbol = "?"
        section = r.get("section", "")
        currier = r.get("currier", "")
        f.write(f"{r['folio']}\t{symbol}\t{section}\t{currier}\n")

print("[S50] Complete.")
EOF
