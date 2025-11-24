#!/usr/bin/env bash
set -euo pipefail

echo "[S57] Stem–suffix register shift tests"

# Assume we are run from Voynich_Reproducible_Core
BASE="$(pwd)"
OUTD="$BASE/PhaseS/out"

P6="$OUTD/p6_folio_tokens.tsv"
REG="$OUTD/s50_folio_register_matrix.tsv"

OUT_SUMMARY="$OUTD/s57_suffix_shift_summary.tsv"
OUT_REPORT="$OUTD/s57_suffix_shift_report.txt"

echo "[S57] BASE:  $BASE"
echo "[S57] OUTD:  $OUTD"
echo "[S57] P6:    $P6"
echo "[S57] REG:   $REG"

if [ ! -s "$P6" ]; then
  echo "[S57] ERROR: missing or empty $P6" >&2
  exit 1
fi

if [ ! -s "$REG" ]; then
  echo "[S57] ERROR: missing or empty $REG" >&2
  exit 1
fi

python3 - << 'PYEOF'
import pandas as pd
import numpy as np
import os
import re

base = os.getcwd()
outd = os.path.join(base, "PhaseS", "out")
p6_path  = os.path.join(outd, "p6_folio_tokens.tsv")
reg_path = os.path.join(outd, "s50_folio_register_matrix.tsv")
summary_path = os.path.join(outd, "s57_suffix_shift_summary.tsv")
report_path  = os.path.join(outd, "s57_suffix_shift_report.txt")

print("[S57] Loading tokens from:", p6_path)
tokens = pd.read_csv(p6_path, sep="\t")

print("[S57] Loading register matrix from:", reg_path)
reg = pd.read_csv(reg_path, sep="\t")

# ---- sanity checks ----
for col in ["folio", "token"]:
    if col not in tokens.columns:
        raise ValueError("[S57] Missing column in p6 tokens: %s" % col)

for col in ["folio", "register"]:
    if col not in reg.columns:
        raise ValueError("[S57] Missing column in register matrix: %s" % col)

# ---- normalise folio IDs on both sides ----
def norm_folio(x: str) -> str:
    s = str(x)
    # extract patterns like f1r, f1v, f10r, f100v, etc.
    m = re.search(r"(f\d+[rv])", s)
    return m.group(1) if m else ""

tokens["folio_norm"] = tokens["folio"].astype(str).map(norm_folio)
reg["folio_norm"]    = reg["folio"].astype(str).map(norm_folio)

# drop rows without a normalised folio
tokens = tokens[tokens["folio_norm"] != ""].copy()
reg    = reg[reg["folio_norm"] != ""].copy()

print("[S57] Tokens with normalised folio:", len(tokens))
print("[S57] Reg rows with normalised folio:", len(reg))

if len(tokens) == 0:
    raise ValueError("[S57] No tokens with normalised folio")
if len(reg) == 0:
    raise ValueError("[S57] No register rows with normalised folio")

# use only folio_norm + register from reg
reg_min = reg[["folio_norm", "register"]].drop_duplicates()

# inner join on folio_norm
df = tokens.merge(reg_min, on="folio_norm", how="inner")
print("[S57] Tokens after join on folio_norm:", len(df))

if len(df) == 0:
    raise ValueError("[S57] No tokens after joining p6 tokens with register matrix")

# Keep only REGISTER_A / REGISTER_B
df = df[df["register"].isin(["REGISTER_A", "REGISTER_B"])].copy()
print("[S57] Tokens with REGISTER_A/B only:", len(df))

if len(df) == 0:
    raise ValueError("[S57] No tokens with REGISTER_A/REGISTER_B after filtering")

# ---- crude stem/suffix split ----
SUFFIXES = [
    "aiin", "aiir", "ain", "air", "oin", "iin",
    "dy", "edy", "ody",
    "am", "al", "ar", "ol", "or", "y"
]
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def split_stem_suffix(tok: str):
    tok = str(tok)
    for suf in SUFFIXES:
        if tok.endswith(suf) and len(tok) > len(suf):
            return tok[:-len(suf)], suf
    return tok, ""  # no recognised suffix

stems = []
suffixes = []
for t in df["token"].astype(str):
    s, suf = split_stem_suffix(t)
    stems.append(s)
    suffixes.append(suf)

df["stem"] = stems
df["suffix"] = suffixes

# Drop tokens without recognisable suffix
df = df[df["suffix"] != ""].copy()
print("[S57] Tokens with recognisable suffix:", len(df))

if len(df) == 0:
    raise ValueError("[S57] No tokens with recognisable suffix")

# ---- restrict to stems that appear in both registers ----
stem_reg_counts = (
    df.groupby(["stem", "register"])
      .size()
      .reset_index(name="n_tokens")
)

pivot = stem_reg_counts.pivot(index="stem", columns="register", values="n_tokens").fillna(0)
for col in ["REGISTER_A", "REGISTER_B"]:
    if col not in pivot.columns:
        pivot[col] = 0

pivot["total"] = pivot["REGISTER_A"] + pivot["REGISTER_B"]
shared_stems = pivot[(pivot["REGISTER_A"] > 0) & (pivot["REGISTER_B"] > 0)].index
print("[S57] Shared stems (A>0 & B>0):", len(shared_stems))

df_shared = df[df["stem"].isin(shared_stems)].copy()
print("[S57] Tokens belonging to shared stems:", len(df_shared))

if len(df_shared) == 0:
    raise ValueError("[S57] No tokens for shared stems")

# ---- per (stem, suffix, register) counts ----
suf_counts = (
    df_shared.groupby(["stem", "suffix", "register"])
             .size()
             .reset_index(name="n_tokens")
)

suf_pivot = suf_counts.pivot(index=["stem", "suffix"],
                             columns="register",
                             values="n_tokens").fillna(0)

for col in ["REGISTER_A", "REGISTER_B"]:
    if col not in suf_pivot.columns:
        suf_pivot[col] = 0

suf_pivot["total"] = suf_pivot["REGISTER_A"] + suf_pivot["REGISTER_B"]
suf_pivot = suf_pivot[suf_pivot["total"] > 0].copy()

suf_pivot["frac_A"] = suf_pivot["REGISTER_A"] / suf_pivot["total"]
suf_pivot["frac_B"] = suf_pivot["REGISTER_B"] / suf_pivot["total"]

def label_bias(row):
    fa = row["frac_A"]
    fb = row["frac_B"]
    if row["REGISTER_A"] > 0 and row["REGISTER_B"] == 0:
        return "A_only"
    if row["REGISTER_B"] > 0 and row["REGISTER_A"] == 0:
        return "B_only"
    if fa >= 0.8:
        return "mixed_biased_A"
    if fb >= 0.8:
        return "mixed_biased_B"
    return "mixed_balanced"

suf_pivot["bias_label"] = suf_pivot.apply(label_bias, axis=1)

# save detailed table
suf_pivot_reset = suf_pivot.reset_index()
suf_pivot_reset[[
    "stem", "suffix",
    "REGISTER_A", "REGISTER_B", "total",
    "frac_A", "frac_B", "bias_label"
]].to_csv(summary_path, sep="\t", index=False)

# ---- aggregate stats for report ----
label_counts = suf_pivot["bias_label"].value_counts().to_dict()

biased_stems = suf_pivot[
    suf_pivot["bias_label"].isin(["mixed_biased_A", "mixed_biased_B"])
].index.get_level_values("stem").unique()
n_biased_stems = len(biased_stems)
prop_biased_stems = float(n_biased_stems) / float(len(shared_stems)) if len(shared_stems) > 0 else 0.0

with open(report_path, "w", encoding="utf-8") as f:
    f.write("S57 – Stem–suffix register shift tests\n")
    f.write("======================================\n\n")
    f.write("Tokens after join with register matrix: %d\n" % len(df))
    f.write("Tokens with recognisable suffix (shared stems only): %d\n" % len(df_shared))
    f.write("Total stems with any A/B usage: %d\n" % len(pivot))
    f.write("Shared stems (A>0 & B>0): %d\n" % len(shared_stems))
    f.write("Stem–suffix rows (shared stems only): %d\n\n" % len(suf_pivot))

    f.write("Bias label counts (stem–suffix pairs):\n")
    for lab in ["A_only", "B_only", "mixed_biased_A", "mixed_biased_B", "mixed_balanced"]:
        f.write("  %-16s %5d\n" % (lab, label_counts.get(lab, 0)))
    f.write("\n")

    f.write("Stems with at least one biased mixed suffix (>=80%% in one register): %d\n" % n_biased_stems)
    f.write("Proportion of shared stems with biased mixed suffix: %.4f\n" % prop_biased_stems)
    f.write("\n")
    f.write("Interpretation hooks:\n")
    f.write("  * A_only / B_only: suffix appears exclusively in one register for that stem.\n")
    f.write("  * mixed_biased_A / mixed_biased_B: suffix used in both registers but >=80%% in one.\n")
    f.write("  * mixed_balanced: suffix used more evenly across A/B.\n")
    f.write("  * A non-trivial fraction of biased stems supports a register-sensitive\n")
    f.write("    suffix system rather than a purely lexical separation.\n")

print("[S57] Wrote summary to:", summary_path)
print("[S57] Wrote report to:", report_path)

PYEOF
