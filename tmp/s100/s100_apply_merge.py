import pandas as pd
import sys

t03 = sys.argv[1]
t3lex = sys.argv[2]
out = sys.argv[3]

print(f"[s100] Loading T03={t03}")
print(f"[s100] Loading T3LEX={t3lex}")

df = pd.read_csv(t03, sep='\t', dtype=str)
lex = pd.read_csv(t3lex, sep='\t', dtype=str)

# -----------------------------------------
# 1. Find the real stem column in t3lex
# -----------------------------------------
lex_cols = set(lex.columns)

possible_stem_cols = [c for c in lex.columns
                      if c.strip().lower() in ("stem", "stemlex", "stem_id", "stem_root")]

if "stem" not in lex_cols:
    if possible_stem_cols:
        detected = possible_stem_cols[0]
        print(f"[s100] Detected stem column in t3lex: '{detected}' → renamed to 'stem'")
        lex = lex.rename(columns={detected: "stem"})
    else:
        print(f"[s100:ERROR] No stem-like column found in lexicon! Columns={lex.columns}")
        sys.exit(1)

# -----------------------------------------
# 2. Drop duplicate columns safely
# -----------------------------------------
dupes = set(df.columns).intersection(set(lex.columns)) - {"stem"}

if dupes:
    print(f"[s100] Dropping duplicate columns from t3lex: {dupes}")
    lex = lex.drop(columns=list(dupes))

# -----------------------------------------
# 3. Merge
# -----------------------------------------
print("[s100] Merging …")
merged = df.merge(
    lex,
    on=["stem"],
    how="left",
    suffixes=('', '_t3lex')
)

print(f"[s100] Rows merged: {len(merged)}")
merged.to_csv(out, sep="\t", index=False)
print(f"[s100] Wrote merged file → {out}")
