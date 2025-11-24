#!/usr/bin/env bash
set -euo pipefail

echo "[S58] Stem valency tests (folio-based proxy)"

# Base + OUTD
BASE="${PWD}"
OUTD="${BASE}/PhaseS/out"

P6="${OUTD}/p6_folio_tokens.tsv"
REG="${OUTD}/s50_folio_register_matrix.tsv"
S46="${OUTD}/s46_stem_semantic_envelopes.tsv"

OUT_PROFILES="${OUTD}/s58_stem_valency_profiles.tsv"
OUT_SUMMARY="${OUTD}/s58_valency_divergence_summary.tsv"
OUT_REPORT="${OUTD}/s58_valency_report.txt"

echo "[S58] BASE:  ${BASE}"
echo "[S58] OUTD:  ${OUTD}"
echo "[S58] P6:    ${P6}"
echo "[S58] REG:   ${REG}"
echo "[S58] S46:   ${S46}"

mkdir -p "${OUTD}"

if [ ! -s "${P6}" ]; then
  echo "[S58][ERROR] Missing or empty ${P6}"
  exit 1
fi

if [ ! -s "${REG}" ]; then
  echo "[S58][ERROR] Missing or empty ${REG}"
  exit 1
fi

python3 - << 'PY'
import pandas as pd
from pathlib import Path
import sys

BASE = Path.cwd()
OUTD = BASE / "PhaseS" / "out"

p6_path   = OUTD / "p6_folio_tokens.tsv"
reg_path  = OUTD / "s50_folio_register_matrix.tsv"
s46_path  = OUTD / "s46_stem_semantic_envelopes.tsv"

out_profiles = OUTD / "s58_stem_valency_profiles.tsv"
out_summary  = OUTD / "s58_valency_divergence_summary.tsv"
out_report   = OUTD / "s58_valency_report.txt"

print(f"[S58] Loading tokens from: {p6_path}")
p6 = pd.read_csv(p6_path, sep="\t", dtype=str)

print(f"[S58] Rows in p6: {len(p6)}")

print(f"[S58] Loading register matrix from: {reg_path}")
reg = pd.read_csv(reg_path, sep="\t", dtype=str)

# Normalise folio labels (strip metadata like '> ...')
import re

def norm_folio(s: str) -> str:
    if not isinstance(s, str):
        return s
    m = re.match(r'^(f[0-9]+[rv])', s)
    return m.group(1) if m else s

p6["folio_norm"] = p6["folio"].apply(norm_folio) if "folio" in p6.columns else p6.iloc[:,0].apply(norm_folio)
reg["folio_norm"] = reg["folio"].apply(norm_folio) if "folio" in reg.columns else reg.iloc[:,0].apply(norm_folio)

print(f"[S58] Tokens with normalised folio: {p6['folio_norm'].notna().sum()}")
print(f"[S58] Reg rows with normalised folio: {reg['folio_norm'].notna().sum()}")

# Join tokens with register matrix
merged = pd.merge(
    p6,
    reg[["folio_norm", "section", "currier", "register", "dominant_semantic_register"]],
    on="folio_norm",
    how="inner",
    suffixes=("", "_reg"),
)

print(f"[S58] Tokens after join with register: {len(merged)}")

# Keep only REGISTER_A / REGISTER_B
mask_reg = merged["register"].isin(["REGISTER_A", "REGISTER_B"])
merged = merged.loc[mask_reg].copy()
print(f"[S58] Tokens with REGISTER_A/B: {len(merged)}")

# Simple stem segmentation as in S57/S58 original: token = stem + suffix (from fallback list)
fallback_suffixes = ["aiin", "iin", "ain", "am", "al", "ody", "ol", "or", "y"]

def segment(token: str):
    if not isinstance(token, str):
        return token, ""
    for suf in sorted(fallback_suffixes, key=len, reverse=True):
        if token.endswith(suf):
            return token[:-len(suf)] or token, suf
    return token, ""

merged["token"] = merged["token"].astype(str)
stems, suffixes = zip(*[segment(t) for t in merged["token"]])
merged["stem"] = stems
merged["suffix"] = suffixes

unique_stems = merged["stem"].nunique()
print(f"[S58] Unique stems after segmentation: {unique_stems}")

# Aggregate per (stem, register): token_count, n_folios, tokens_per_folio
group_cols = ["stem", "register"]
agg = (
    merged
    .groupby(group_cols)
    .agg(
        token_count=("token", "size"),
        n_folios=("folio_norm", pd.Series.nunique),
    )
    .reset_index()
)

# Guard: avoid division by zero
agg["n_folios"] = agg["n_folios"].replace(0, 1)
agg["tokens_per_folio"] = agg["token_count"] / agg["n_folios"]

# Try to merge semantic envelopes from S46 if possible (best-effort only)
if s46_path.exists() and s46_path.stat().st_size > 0:
    try:
        s46 = pd.read_csv(s46_path, sep="\t", dtype=str)
        if "stem" in s46.columns:
            cols = ["stem"]
            extra_cols = [c for c in ["semantic_family", "role_group", "primary_section", "structural_class"] if c in s46.columns]
            cols = cols + extra_cols
            s46_small = s46[cols].drop_duplicates("stem")
            agg = agg.merge(s46_small, on="stem", how="left")
        else:
            print("[S58][WARN] S46 has no 'stem' column – skipping semantic envelopes.")
    except Exception as e:
        print(f"[S58][WARN] Could not merge S46 semantic envelopes: {e}")
else:
    print("[S58][WARN] S46 semantic file missing or empty – skipping semantic envelopes.")

# Ensure expected columns exist (even if empty) for downstream compatibility
for col in ["semantic_family", "role_group", "primary_section", "structural_class"]:
    if col not in agg.columns:
        agg[col] = ""

# Write profiles
agg_cols_order = [
    "stem", "register",
    "token_count", "n_folios", "tokens_per_folio",
    "semantic_family", "role_group", "primary_section", "structural_class",
]
agg[agg_cols_order].to_csv(out_profiles, sep="\t", index=False)
print(f"[S58] Wrote stem valency (folio) profiles to: {out_profiles}")

# Build divergence summary: focus on stems with both registers
pivot = agg.pivot(index="stem", columns="register", values="tokens_per_folio")
for col in ["REGISTER_A", "REGISTER_B"]:
    if col not in pivot.columns:
        pivot[col] = float("nan")

both = pivot.dropna(subset=["REGISTER_A", "REGISTER_B"])
total_shared = len(both)
if total_shared == 0:
    divergent_stems = 0
    prop_divergent = 0.0
else:
    delta = (both["REGISTER_A"] - both["REGISTER_B"]).abs()
    # Threshold: difference of at least 0.5 tokens per folio between registers
    divergent_mask = delta >= 0.5
    divergent_stems = int(divergent_mask.sum())
    prop_divergent = divergent_stems / total_shared

summary = pd.DataFrame(
    [
        ["total_shared_stems", total_shared],
        ["divergent_stems", divergent_stems],
        ["prop_divergent", prop_divergent],
    ],
    columns=["metric", "value"],
)
summary.to_csv(out_summary, sep="\t", index=False)
print(f"[S58] Wrote divergence summary to: {out_summary}")

# Text report
with open(out_report, "w", encoding="utf-8") as f:
    f.write("S58 – Stem valency tests (folio-based proxy)\n")
    f.write("============================================\n\n")
    f.write(f"Tokens with register labels: {len(merged)}\n")
    f.write(f"Unique stems after segmentation: {unique_stems}\n")
    f.write(f"Stems with both REGISTER_A and REGISTER_B presence: {total_shared}\n")
    f.write(f"Divergent stems (|Δ tokens_per_folio| ≥ 0.5): {divergent_stems} ({prop_divergent:.3f} of shared stems)\n\n")
    f.write("Interpretation (provisional):\n")
    f.write("  * This pass approximates 'valency' by how widely a stem is distributed across folios\n")
    f.write("    within each register (tokens_per_folio), rather than by full argument structure.\n")
    f.write("  * Divergent stems are those whose per-folio distribution differs substantially between\n")
    f.write("    REGISTER_A and REGISTER_B, even though the stem itself is shared.\n")
    f.write("  * A substantial fraction of divergent stems supports a register-sensitive deployment of\n")
    f.write("    shared lexemes, rather than purely disjoint lexica.\n\n")
    f.write("Limitations:\n")
    f.write("  * True valency (subject/object/oblique roles) would require clause-structure data from\n")
    f.write("    the S35/S47 pipelines; here we only use folio-level distributions as a tractable proxy.\n")
    f.write("  * Results should be reported as exploratory evidence, not as a full valency model.\n")

print(f"[S58] Wrote report to: {out_report}")
print("[S58] Done.")
PY
