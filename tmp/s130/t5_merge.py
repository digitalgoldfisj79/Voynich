import pandas as pd
import sys, os

t4, t3lex, out = sys.argv[1:4]

print(f"[t5] Loading T4={t4}")
df = pd.read_csv(t4, sep="\t", dtype=str, keep_default_na=False)

print(f"[t5] Loading T3LEX={t3lex}")
lex = pd.read_csv(t3lex, sep="\t", dtype=str, keep_default_na=False)

# --- Guardrails: ensure merge key exists on both sides ---
if "stem" not in df.columns:
    raise SystemExit("[t5] ERROR: T4 missing required column 'stem'.")

if "stem" not in lex.columns:
    # try salvage: rename first col to stem
    first = lex.columns[0]
    lex = lex.rename(columns={first: "stem"})
    if "stem" not in lex.columns:
        raise SystemExit("[t5] ERROR: T3LEX missing required column 'stem'.")

# --- Drop duplicate columns from lexicon BUT NEVER drop the merge key ---
dupes = set(df.columns).intersection(set(lex.columns))
dupes.discard("stem")

if dupes:
    print(f"[t5] Dropping duplicate columns from T3LEX (keeping stem): {sorted(dupes)}")
    lex = lex.drop(columns=list(dupes))

print("[t5] Merging T4 + T3LEX on stem...")
merged = df.merge(lex, on="stem", how="left", suffixes=("", "_t3lex"))

# --- If any _t3lex columns remain, use them to fill empties then drop ---
for col in list(merged.columns):
    if col.endswith("_t3lex"):
        base = col[:-6]
        if base in merged.columns:
            merged[base] = merged[base].where(merged[base] != "", merged[col])
        else:
            merged[base] = merged[col]
        merged.drop(columns=[col], inplace=True)

# =========================================================
# FULL T5 CASCADE (Option C)
# =========================================================

# Ensure expected cols exist
for c in ["english_token","english_phrase","pos_tag","gloss_stemlex","gloss_en","lemma_latin","pos_t3"]:
    if c not in merged.columns:
        merged[c] = ""

def make_english_token(row):
    ge = row.get("gloss_en","")
    if ge:
        return ge
    et = row.get("english_token","")
    if et and not et.startswith("X"):
        return et
    gs = row.get("gloss_stemlex","")
    if gs:
        return gs
    return row.get("token","")

merged["english_token"] = merged.apply(make_english_token, axis=1)

# pos_tag: prefer pos_t3 if present
merged["pos_tag"] = merged["pos_t3"].where(merged["pos_t3"]!="", merged["pos_tag"])

# english_phrase: rebuild per folio_norm+line if possible
if "folio_norm" in merged.columns and "line" in merged.columns:
    merged["english_phrase"] = (
        merged.groupby(["folio_norm","line"])["english_token"]
              .transform(lambda s: " ".join([x for x in s if x!=""]))
    )

print(f"[t5] Wrote T5 → {out} (rows={len(merged)})")
merged.to_csv(out, sep="\t", index=False)
