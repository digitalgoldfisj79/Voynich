import pandas as pd
import sys

print("[t5] Loading…")
t4_path, t3lex_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

df = pd.read_csv(t4_path, sep="\t", dtype=str)
lex = pd.read_csv(t3lex_path, sep="\t", dtype=str)

# --- STEP 1: normalise column names ---
def clean_cols(cols):
    return [c.strip().replace("\ufeff", "") for c in cols]

df.columns = clean_cols(df.columns)
lex.columns = clean_cols(lex.columns)

# --- STEP 2: find stem column in lexicon ---
stem_col = None
candidates = ["stem", "Stem", "t3_stem"]

for c in lex.columns:
    if c in candidates:
        stem_col = c
        break

# If still not found, detect by matching values
if stem_col is None:
    print("[t5] Auto-detecting stem column…")
    t4_stems = set(df["stem"].dropna().unique())
    for c in lex.columns:
        overlap = t4_stems.intersection(set(lex[c].dropna().unique()))
        if len(overlap) > 50:  # high overlap → correct column
            stem_col = c
            break

if stem_col is None:
    print("[t5] FATAL: No matching stem column found in T3 lexicon.")
    print("[t5] Columns in lexicon:", lex.columns)
    sys.exit(1)

print(f"[t5] Using stem column in T3LEX: {stem_col}")

# --- STEP 3: drop duplicate cols before merge ---
dupes = set(df.columns).intersection(set(lex.columns))
if dupes:
    print("[t5] Dropping duplicate columns:", dupes)
    lex = lex.drop(columns=list(dupes))

# --- STEP 4: do merge ---
print("[t5] Merging on stem →", stem_col)
merged = df.merge(lex, left_on="stem", right_on=stem_col, how="left")

# optional cleanup: drop redundant join column if not named 'stem'
if stem_col != "stem":
    merged = merged.drop(columns=[stem_col])

print(f"[t5] Write → {out_path}")
merged.to_csv(out_path, sep="\t", index=False)

print("[t5] Merge completed.")
