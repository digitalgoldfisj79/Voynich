#!/bin/sh
# S59 – Stem positional profiles and register divergence

set -eu

BASE="${BASE:-$PWD}"
OUTD="$BASE/PhaseS/out"

P6="$OUTD/p6_folio_tokens.tsv"
REG="$OUTD/s50_folio_register_matrix.tsv"

OUT_PROFILE="$OUTD/s59_stem_positional_profiles.tsv"
OUT_SUMMARY="$OUTD/s59_positional_divergence_summary.tsv"
OUT_REPORT="$OUTD/s59_positional_report.txt"

mkdir -p "$OUTD"

echo "[S59] Stem positional profiles" >&2
echo "[S59] BASE:  $BASE" >&2
echo "[S59] OUTD:  $OUTD" >&2
echo "[S59] P6:    $P6" >&2
echo "[S59] REG:   $REG" >&2

[ -s "$P6" ]  || { echo "[S59] ERROR: missing $P6" >&2; exit 1; }
[ -s "$REG" ] || { echo "[S59] ERROR: missing $REG" >&2; exit 1; }

export P6 REG OUT_PROFILE OUT_SUMMARY OUT_REPORT

python3 << 'PY'
import os
import sys
import pandas as pd
import numpy as np

P6 = os.environ["P6"]
REG = os.environ["REG"]
OUT_PROFILE = os.environ["OUT_PROFILE"]
OUT_SUMMARY = os.environ["OUT_SUMMARY"]
OUT_REPORT = os.environ["OUT_REPORT"]

print(f"[S59] Loading tokens from: {P6}", file=sys.stderr)
tok = pd.read_csv(P6, sep="\t")
required_p6 = {"token", "folio", "pos"}
if not required_p6.issubset(tok.columns):
    raise ValueError(f"[S59] p6_folio_tokens.tsv missing columns: {required_p6 - set(tok.columns)}")

print(f"[S59] Rows in p6: {len(tok)}", file=sys.stderr)

print(f"[S59] Loading register matrix from: {REG}", file=sys.stderr)
reg = pd.read_csv(REG, sep="\t")
required_reg = {"folio", "register"}
if not required_reg.issubset(reg.columns):
    raise ValueError(f"[S59] s50_folio_register_matrix.tsv missing columns: {required_reg - set(reg.columns)}")

def norm_folio(s):
    s = str(s)
    return s.split(">")[0].strip()

tok["folio_norm"] = tok["folio"].apply(norm_folio)
reg["folio_norm"] = reg["folio"].astype(str).str.strip()

tok = tok.merge(reg[["folio_norm", "register"]], on="folio_norm", how="inner")
print(f"[S59] Tokens after join with register: {len(tok)}", file=sys.stderr)

tok = tok[tok["register"].isin(["REGISTER_A", "REGISTER_B"])].copy()
print(f"[S59] Tokens with REGISTER_A/B: {len(tok)}", file=sys.stderr)

# Stem segmentation as in S58/T01
SUFFIXES = ["aiin", "iin", "ain", "am", "al", "ody", "ol", "or", "y"]

def seg_token(token: str):
    token = str(token)
    for suf in SUFFIXES:
        if token.endswith(suf) and len(token) > len(suf):
            return token[:-len(suf)], suf
    return token, ""

stems, suffixes = zip(*tok["token"].astype(str).map(seg_token))
tok["stem"] = stems
tok["suffix"] = suffixes

print(f"[S59] Unique stems after segmentation: {tok['stem'].nunique()}", file=sys.stderr)

# Compute per-folio max_pos and relative position
tok["pos"] = pd.to_numeric(tok["pos"], errors="coerce")
tok = tok.dropna(subset=["pos"]).copy()
tok["pos"] = tok["pos"].astype(int)

max_pos = tok.groupby("folio_norm")["pos"].max().rename("max_pos")
tok = tok.merge(max_pos, on="folio_norm", how="left")
tok["rel_pos"] = tok["pos"] / tok["max_pos"].replace(0, np.nan)

# Drop any rows with NaN rel_pos
tok = tok.dropna(subset=["rel_pos"]).copy()
print(f"[S59] Tokens with rel_pos: {len(tok)}", file=sys.stderr)

# Stem-level positional profiles
grp = tok.groupby(["stem", "register"])
profiles = grp["rel_pos"].agg(
    n_tokens="size",
    mean_rel_pos="mean",
    std_rel_pos="std",
).reset_index()

# Optional: coarse bins for shape (0-0.2,0.2-0.4,...)
bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0000001]
labels = ["bin_1", "bin_2", "bin_3", "bin_4", "bin_5"]
tok["pos_bin"] = pd.cut(tok["rel_pos"], bins=bins, labels=labels, include_lowest=True)

bin_counts = (
    tok.groupby(["stem", "register", "pos_bin"])
    .size()
    .reset_index(name="n_bin")
    .pivot_table(
        index=["stem", "register"],
        columns="pos_bin",
        values="n_bin",
        fill_value=0,
        aggfunc="sum",
    )
)
bin_counts.columns = [f"n_{c}" for c in bin_counts.columns]
bin_counts = bin_counts.reset_index()

profiles = profiles.merge(bin_counts, on=["stem", "register"], how="left")

# Write full profiles
profiles.to_csv(OUT_PROFILE, sep="\t", index=False)

# Divergence summary for shared stems
has_A = profiles[profiles["register"] == "REGISTER_A"]["stem"].unique()
has_B = profiles[profiles["register"] == "REGISTER_B"]["stem"].unique()
shared_stems = sorted(set(has_A) & set(has_B))
print(f"[S59] Shared stems with positional info (A & B): {len(shared_stems)}", file=sys.stderr)

profiles2 = profiles.set_index(["stem", "register"])
rows = []
for stem in shared_stems:
    try:
        a_row = profiles2.loc[(stem, "REGISTER_A")]
        b_row = profiles2.loc[(stem, "REGISTER_B")]
    except KeyError:
        continue

    meanA = float(a_row["mean_rel_pos"])
    meanB = float(b_row["mean_rel_pos"])
    rows.append({
        "stem": stem,
        "n_A": int(a_row["n_tokens"]),
        "n_B": int(b_row["n_tokens"]),
        "meanA": meanA,
        "meanB": meanB,
        "delta_mean": meanB - meanA,
        "abs_delta_mean": abs(meanB - meanA),
    })

summary = pd.DataFrame(rows)
# Filter to stems with enough tokens in both registers
summary = summary[(summary["n_A"] >= 5) & (summary["n_B"] >= 5)].copy()

# Mark "strong" positional shift
thr = 0.15  # ~15% of line
summary["strong_shift"] = summary["abs_delta_mean"] >= thr

summary.to_csv(OUT_SUMMARY, sep="\t", index=False)

with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("S59 – Stem positional profiles and register divergence\n")
    f.write("=====================================================\n\n")
    f.write(f"Tokens with REGISTER_A/B and rel_pos: {len(tok)}\n")
    f.write(f"Shared stems (A & B) with positional info: {len(shared_stems)}\n")
    f.write(f"Shared stems with n_A>=5,n_B>=5: {len(summary)}\n\n")

    if not summary.empty:
        f.write("Strong positional shifts (|Δmean_rel_pos| ≥ 0.15):\n")
        f.write(f"  Count: {summary['strong_shift'].sum()} stems\n\n")
        f.write("Top 20 stems by |Δmean_rel_pos|:\n")
        top = summary.sort_values("abs_delta_mean", ascending=False).head(20)
        for _, row in top.iterrows():
            f.write(
                f"  {row['stem']}: meanA={row['meanA']:.3f}, "
                f"meanB={row['meanB']:.3f}, Δ={row['delta_mean']:.3f}, "
                f"n_A={row['n_A']}, n_B={row['n_B']}\n"
            )
    else:
        f.write("No usable shared stems for positional divergence.\n")

print(f"[S59] Wrote profiles to: {OUT_PROFILE}", file=sys.stderr)
print(f"[S59] Wrote summary to:  {OUT_SUMMARY}", file=sys.stderr)
print(f"[S59] Wrote report to:   {OUT_REPORT}", file=sys.stderr)
PY

