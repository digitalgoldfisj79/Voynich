#!/usr/bin/env sh
# S55 – Cross-register stem overlap (lexical vs register)
# Uses:
#   PhaseS/out/p6_folio_tokens.tsv
#   PhaseS/out/s50_folio_register_matrix.tsv
# Writes:
#   PhaseS/out/s55_stem_register_counts.tsv
#   PhaseS/out/s55_stem_overlap_summary.tsv
#   PhaseS/out/s55_stem_overlap_report.txt

set -eu

# Derive BASE from this script's location (…/Voynich_Reproducible_Core)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
export BASE

OUTD="$BASE/PhaseS/out"

P6="$OUTD/p6_folio_tokens.tsv"
REG="$OUTD/s50_folio_register_matrix.tsv"

OUT_COUNTS="$OUTD/s55_stem_register_counts.tsv"
OUT_SUMMARY="$OUTD/s55_stem_overlap_summary.tsv"
OUT_REPORT="$OUTD/s55_stem_overlap_report.txt"

echo "[S55] Cross-register stem overlap"
echo "[S55] BASE:       $BASE"
echo "[S55] OUTD:       $OUTD"
echo "[S55] P6 tokens:  $P6"
echo "[S55] Reg matrix: $REG"

# Basic existence checks
if [ ! -s "$P6" ]; then
    echo "[S55] ERROR: missing or empty $P6" >&2
    exit 1
fi

if [ ! -s "$REG" ]; then
    echo "[S55] ERROR: missing or empty $REG" >&2
    exit 1
fi

python3 << 'PY'
import os
import pathlib
import pandas as pd

BASE = pathlib.Path(os.environ["BASE"])
OUTD = BASE / "PhaseS" / "out"

p6_path = OUTD / "p6_folio_tokens.tsv"
reg_path = OUTD / "s50_folio_register_matrix.tsv"

out_counts = OUTD / "s55_stem_register_counts.tsv"
out_summary = OUTD / "s55_stem_overlap_summary.tsv"
out_report = OUTD / "s55_stem_overlap_report.txt"

print(f"[S55] Loading tokens from: {p6_path}")
tokens = pd.read_csv(p6_path, sep="\t")

expected_p6_cols = {"token", "folio"}
missing = expected_p6_cols - set(tokens.columns)
if missing:
    raise ValueError(f"[S55] p6_folio_tokens.tsv missing columns: {missing}")

print(f"[S55] Loading register matrix from: {reg_path}")
reg = pd.read_csv(reg_path, sep="\t")

expected_reg_cols = {"folio", "register"}
missing_reg = expected_reg_cols - set(reg.columns)
if missing_reg:
    raise ValueError(f"[S55] s50_folio_register_matrix.tsv missing columns: {missing_reg}")

def clean_folio(val):
    """Normalize folio IDs: take part before '>', strip spaces."""
    if isinstance(val, str):
        return val.split(">")[0].strip()
    return val

# Clean folio IDs in both frames
tokens["folio_clean"] = tokens["folio"].apply(clean_folio)
reg["folio_clean"] = reg["folio"].apply(clean_folio)

# Just to be very explicit, drop any rows with empty folio_clean
tokens = tokens[tokens["folio_clean"] != ""]
reg = reg[reg["folio_clean"] != ""]

# Only folios with REGISTER_A or REGISTER_B
reg_valid = reg[reg["register"].isin(["REGISTER_A", "REGISTER_B"])][["folio_clean", "register"]]

# Debug: unique folios in each and intersection
folios_tokens = set(tokens["folio_clean"].unique())
folios_reg = set(reg_valid["folio_clean"].unique())
intersection = folios_tokens & folios_reg

print(f"[S55] Unique folios in tokens:       {len(folios_tokens)}")
print(f"[S55] Unique folios in reg matrix:   {len(folios_reg)}")
print(f"[S55] Intersection (joinable folios): {len(intersection)}")

if not intersection:
    raise ValueError("[S55] No overlapping folios between tokens and register matrix after cleaning")

# Join tokens with register labels via folio_clean
merged = tokens.merge(reg_valid, on="folio_clean", how="inner")
if merged.empty:
    raise ValueError("[S55] No tokens after joining with register matrix (after folio_clean join)")

print(f"[S55] Joined tokens: {len(merged)} rows")

def reg_to_simple(x: str) -> str:
    if x == "REGISTER_A":
        return "A"
    if x == "REGISTER_B":
        return "B"
    return "Other"

merged["reg_simple"] = merged["register"].map(reg_to_simple)

# Group by token and register
grp = merged.groupby(["token", "reg_simple"]).size().reset_index(name="count")

pivot = grp.pivot_table(index="token", columns="reg_simple", values="count", fill_value=0)

for col in ["A", "B"]:
    if col not in pivot.columns:
        pivot[col] = 0

pivot = pivot[["A", "B"]].copy()
pivot.rename(columns={"A": "count_A", "B": "count_B"}, inplace=True)
pivot["total_count"] = pivot["count_A"] + pivot["count_B"]

def label_pattern(row):
    a = row["count_A"]
    b = row["count_B"]
    if a > 0 and b == 0:
        return "A_only"
    if b > 0 and a == 0:
        return "B_only"
    if a == 0 and b == 0:
        return "None"
    total = a + b
    frac_a = a / total
    # "Balanced" band: 40–60% A
    if 0.4 <= frac_a <= 0.6:
        return "Both_balanced"
    if frac_a > 0.6:
        return "Both_A_dom"
    return "Both_B_dom"

pivot["register_pattern"] = pivot.apply(label_pattern, axis=1)
pivot = pivot.reset_index()  # restore token as column

pivot.to_csv(out_counts, sep="\t", index=False)
print(f"[S55] Wrote stem-register counts: {out_counts}")

n_total = len(pivot)
n_a_only = int((pivot["register_pattern"] == "A_only").sum())
n_b_only = int((pivot["register_pattern"] == "B_only").sum())
n_both = int((pivot["register_pattern"].str.startswith("Both")).sum())

def safe_frac(num: int, den: int) -> float:
    return float(num) / float(den) if den > 0 else float("nan")

summary = pd.DataFrame(
    [
        {
            "n_stems_total": n_total,
            "n_stems_A_only": n_a_only,
            "n_stems_B_only": n_b_only,
            "n_stems_both": n_both,
            "prop_A_only": safe_frac(n_a_only, n_total),
            "prop_B_only": safe_frac(n_b_only, n_total),
            "prop_both": safe_frac(n_both, n_total),
        }
    ]
)
summary.to_csv(out_summary, sep="\t", index=False)
print(f"[S55] Wrote overlap summary: {out_summary}")

both = pivot[pivot["register_pattern"].str.startswith("Both")].copy()

with out_report.open("w", encoding="utf-8") as f:
    f.write("S55 – Cross-register stem overlap (lexical vs register)\n")
    f.write("======================================================\n\n")
    f.write(f"Total stems with at least one occurrence in REGISTER_A/B folios: {n_total}\n")
    f.write(f"Stems only in REGISTER_A: {n_a_only} ({safe_frac(n_a_only, n_total):.3f})\n")
    f.write(f"Stems only in REGISTER_B: {n_b_only} ({safe_frac(n_b_only, n_total):.3f})\n")
    f.write(f"Stems in both registers:  {n_both} ({safe_frac(n_both, n_total):.3f})\n\n")

    f.write("Breakdown of shared stems by pattern:\n")
    if both.empty:
        f.write("  No stems appear in both registers.\n")
    else:
        counts_by_pattern = both["register_pattern"].value_counts().to_dict()
        for pat in ["Both_balanced", "Both_A_dom", "Both_B_dom"]:
            if pat in counts_by_pattern:
                n_pat = counts_by_pattern[pat]
                f.write(f"  {pat}: {n_pat} stems\n")
        f.write("\n")
        both["frac_A"] = both["count_A"] / (both["count_A"] + both["count_B"])
        both["balance_distance"] = (both["frac_A"] - 0.5).abs()
        top_balanced = both.sort_values("balance_distance").head(20)
        f.write("Top 20 most balanced shared stems (by A/B usage):\n")
        f.write("token\tcount_A\tcount_B\ttotal\tfrac_A\n")
        for _, row in top_balanced.iterrows():
            f.write(
                f"{row['token']}\t"
                f"{row['count_A']}\t"
                f"{row['count_B']}\t"
                f"{row['total_count']}\t"
                f"{row['frac_A']:.3f}\n"
            )

    f.write("\nNotes:\n")
    f.write("  * Folio IDs are normalised by stripping anything after '>' and whitespace.\n")
    f.write("  * Only folios with REGISTER_A/REGISTER_B labels are included.\n")
    f.write("  * This phase quantifies lexical overlap; it does not yet test grammatical behaviour.\n")
    f.write("  * Follow-up phases will examine whether shared stems behave differently in A vs B.\n")

print(f"[S55] Wrote human-readable report: {out_report}")
PY

echo "[S55] Done."
