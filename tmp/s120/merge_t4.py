import pandas as pd
import sys

t03, t3lex, out = sys.argv[1], sys.argv[2], sys.argv[3]

print(f"[s120] Loading T03={t03}")
df = pd.read_csv(t03, sep="\t", dtype=str)

print(f"[s120] Loading T3LEX={t3lex}")
lex = pd.read_csv(t3lex, sep="\t", dtype=str)

# Drop duplicate columns
dupes = set(df.columns).intersection(set(lex.columns))
if dupes:
    print(f"[s120] Dropping duplicate columns from t3lex: {dupes}")
    lex = lex.drop(columns=list(dupes))

print("[s120] Merging …")
merged = df.merge(lex, on=["stem"], how="left", suffixes=("", "_t3lex"))

print(f"[s120] Rows merged: {len(merged)}")
merged.to_csv(out, sep="\t", index=False)
print(f"[s120] Wrote merged file → {out}")
