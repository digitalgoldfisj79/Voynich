#!/data/data/com.termux/files/usr/bin/sh
set -eu

echo "[s73] BASE: $(pwd)"
BASE="$(pwd)"
IN_T03="$BASE/PhaseT/out/t03_enriched_translations.tsv"
OUT="$BASE/PhaseT/out/s73_okar_qotar_suffix_contrast.tsv"

echo "[s73] IN_T03: $IN_T03"
echo "[s73] OUT: $OUT"

python - << PY
import sys
import math
import pandas as pd

in_t03 = r"${IN_T03}"
out_tsv = r"${OUT}"

print(f"[s73(py)] Loading t03 from: {in_t03}", file=sys.stderr)
try:
    df = pd.read_csv(in_t03, sep="\t", dtype=str)
except FileNotFoundError:
    print(f"[s73(py)] ERROR: file not found: {in_t03}", file=sys.stderr)
    sys.exit(1)

required = ["stem", "suffix"]
missing = [c for c in required if c not in df.columns]
if missing:
    print(f"[s73(py)] ERROR: required columns missing in t03: {missing}", file=sys.stderr)
    sys.exit(1)

# Focus only on okar / qotar
mask = df["stem"].isin(["okar", "qotar"])
sub = df.loc[mask, ["stem", "suffix"]].copy()

print(f"[s73(py)] okar/qotar rows in t03: {len(sub)}", file=sys.stderr)
if sub.empty:
    with open(out_tsv, "w", encoding="utf-8") as fh:
        fh.write("### S73 okar/qotar Suffix Contrast (t03)\n")
        fh.write("## No rows found for okar/qotar in t03_enriched_translations.tsv\n")
    print("[s73(py)] Wrote empty summary.", file=sys.stderr)
    sys.exit(0)

# Normalise suffix column
sub["suffix"] = sub["suffix"].fillna("").astype(str)

# Raw counts: 2 x K table
counts = (
    sub.groupby(["stem", "suffix"])
       .size()
       .reset_index(name="count")
)

# Pivot to 2 x K matrix
pivot = counts.pivot(index="stem", columns="suffix", values="count").fillna(0)
pivot = pivot.astype(float)

# Compute chi-square manually (no SciPy)
row_sums = pivot.sum(axis=1).values
col_sums = pivot.sum(axis=0).values
grand = row_sums.sum()

if grand == 0 or pivot.shape[0] < 2 or pivot.shape[1] < 2:
    chi2 = float("nan")
    df_chi = 0
else:
    expected = [[(row_sums[i] * col_sums[j]) / grand
                 for j in range(pivot.shape[1])]
                for i in range(pivot.shape[0])]
    obs = pivot.values
    chi2 = 0.0
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            e = expected[i][j]
            if e > 0:
                chi2 += (obs[i, j] - e) ** 2 / e
    df_chi = (pivot.shape[0] - 1) * (pivot.shape[1] - 1)

# Also compute normalised fractions per stem
frac = pivot.div(pivot.sum(axis=1), axis=0)

with open(out_tsv, "w", encoding="utf-8") as fh:
    fh.write("### S73 okar/qotar Suffix Contrast (t03)\n")

    fh.write("## Raw suffix counts\n")
    fh.write("stem\tsuffix\tcount\n")
    for _, row in counts.sort_values(["stem", "count"], ascending=[True, False]).iterrows():
        fh.write(f"{row['stem']}\t{row['suffix']}\t{int(row['count'])}\n")

    fh.write("## Normalised suffix fractions\n")
    fh.write("stem\tsuffix\tfrac\n")
    for stem in frac.index:
        for suffix in frac.columns:
            value = frac.loc[stem, suffix]
            if value > 0:
                fh.write(f"{stem}\t{suffix}\t{value:.4f}\n")

    fh.write("## Chi-square comparison (2xK; SciPy-free)\n")
    fh.write(f"chi2\t{chi2:.4f}\n")
    fh.write(f"df\t{df_chi}\n")
    fh.write(f"grand_total\t{int(grand)}\n")
    fh.write("note\tNo SciPy: p-value not computed; compare chi2 against critical values (e.g. df=K-1, α=0.05)\n")

print(f"[s73(py)] Wrote suffix contrast to {out_tsv}", file=sys.stderr)
PY

echo "[s73] Done."
