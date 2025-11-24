#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# t04_line_translations.sh
# Build line-level translations from t03_enriched_translations.tsv
# Usage:
#   ./scripts/t04_line_translations.sh           # all folios
#   ./scripts/t04_line_translations.sh f103r     # single folio

BASE="${BASE:-$PWD}"
IN_ENRICHED="$BASE/PhaseT/out/t03_enriched_translations.tsv"
OUT_LINES="$BASE/PhaseT/out/t04_line_translations.tsv"
FOLIO_FILTER="${1:-}"

mkdir -p "$BASE/PhaseT/out"

echo "[t04] BASE:        $BASE"
echo "[t04] IN_ENRICHED: $IN_ENRICHED"
echo "[t04] OUT_LINES:   $OUT_LINES"
if [ -n "$FOLIO_FILTER" ]; then
  echo "[t04] Folio filter: $FOLIO_FILTER"
fi

python3 - "$IN_ENRICHED" "$OUT_LINES" "$FOLIO_FILTER" "$BASE" << 'PYEOF'
import sys
import os
import pandas as pd

in_path, out_path, folio_filter, base = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

print(f"[t04(py)] Loading enriched translations from {in_path}")

if not os.path.exists(in_path):
    raise SystemExit(f"[t04(py)] ERROR: missing {in_path} – run t03_apply_lexicons.sh first.")

# ---- Load t03_enriched_translations.tsv ----
df = pd.read_csv(in_path, sep="\t", dtype=str).fillna("")

required_cols = [
    "folio_norm", "folio", "line", "section", "register",
    "pos", "token", "stem", "suffix",
    "semantic_family", "role_group"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise SystemExit(f"[t04(py)] ERROR: t03 is missing required columns: {missing}")

df["pos_order"] = pd.to_numeric(df["pos"], errors="coerce")

# ---- Optional folio filter ----
if folio_filter:
    before = len(df)
    df = df[(df["folio_norm"] == folio_filter) | (df["folio"] == folio_filter)]
    after = len(df)
    print(f"[t04(py)] Folio filter {folio_filter}: {before} -> {after} rows")
    if after == 0:
        print(f"[t04(py)] WARNING: no rows for folio {folio_filter}")

# ---- Load T2 functional lexicon (if present) ----
t2_path = os.path.join(base, "metadata", "t2_stem_functional_lexicon.tsv")
t2_map = {}

if os.path.exists(t2_path):
    try:
        t2_df = pd.read_csv(t2_path, sep="\t", dtype=str).fillna("")
        if "stem" not in t2_df.columns or "functional_label" not in t2_df.columns:
            print(f"[t04(py)] WARNING: {t2_path} missing 'stem' or 'functional_label' – ignoring T2 lexicon.")
        else:
            for _, r in t2_df.iterrows():
                stem = (r.get("stem") or "").strip()
                label = (r.get("functional_label") or "").strip()
                if stem and label:
                    t2_map[stem] = label
            print(f"[t04(py)] Loaded {len(t2_map)} T2 stem→functional_label mappings from {t2_path}")
    except Exception as e:
        print(f"[t04(py)] WARNING: failed to load T2 lexicon {t2_path}: {e}")
        t2_map = {}
else:
    print(f"[t04(py)] No T2 lexicon found at {t2_path} – english_T2_line will mirror T1 where no mapping exists.")

if df.empty:
    out_cols = [
        "folio_norm", "folio", "line", "section", "register",
        "n_tokens", "eva_line", "english_T1_line", "english_T2_line",
        "has_proc_family", "has_bot_family"
    ]
    pd.DataFrame(columns=out_cols).to_csv(out_path, sep="\t", index=False)
    print(f"[t04(py)] No data – wrote empty {out_path}")
    raise SystemExit(0)

group_cols = ["folio_norm", "folio", "line", "section", "register"]

rows = []

def build_base(row):
    """Base stem+suffix chunk, identical for T1 and T2."""
    stem = row.get("stem", "") or ""
    suffix = row.get("suffix", "") or ""
    token = row.get("token", "") or ""

    if stem and suffix:
        return f"{stem}[?]-{suffix}"
    elif stem:
        return f"{stem}[?]"
    elif suffix:
        return f"{token}[?]-{suffix}"
    else:
        return f"{token}[?]"

def build_tags(row, include_func=False):
    """Collect structural tags; optionally add functional_label from T2 lexicon."""
    tags = []

    semfam = row.get("semantic_family", "")
    if semfam:
        tags.append(semfam)

    roleg = row.get("role_group", "")
    if roleg:
        tags.append(roleg)

    reg = row.get("register", "")
    if reg:
        tags.append(reg)

    if include_func:
        stem = row.get("stem", "") or ""
        func = t2_map.get(stem)
        if func:
            tags.append(func)

    return tags

def build_t1_piece(row):
    base = build_base(row)
    tags = build_tags(row, include_func=False)
    if tags:
        return f"{base}[{'|'.join(tags)}]"
    else:
        return base

def build_t2_piece(row):
    # If no T2 mappings at all, just mirror T1 to keep behaviour stable
    if not t2_map:
        return build_t1_piece(row)

    base = build_base(row)
    tags = build_tags(row, include_func=True)
    if tags:
        return f"{base}[{'|'.join(tags)}]"
    else:
        return base

for (folio_norm, folio, line, section, register), g in df.groupby(group_cols, sort=False):
    g_sorted = g.sort_values("pos_order", kind="mergesort")

    eva_tokens = g_sorted["token"].tolist()
    eva_line = " ".join(eva_tokens)
    n_tokens = len(eva_tokens)

    # T1: structural tags only (1:1 with EVA)
    t1_tokens = [build_t1_piece(r) for _, r in g_sorted.iterrows()]
    english_T1_line = " ".join(t1_tokens)

    # T2: structural + functional label (if present for stem)
    t2_tokens = [build_t2_piece(r) for _, r in g_sorted.iterrows()]
    english_T2_line = " ".join(t2_tokens)

    has_proc_family = g_sorted["semantic_family"].eq("F_PROC_CORE").any()
    has_bot_family  = g_sorted["semantic_family"].eq("F_BOTANICAL_CORE").any()

    rows.append({
        "folio_norm": folio_norm,
        "folio": folio,
        "line": line,
        "section": section,
        "register": register,
        "n_tokens": n_tokens,
        "eva_line": eva_line,
        "english_T1_line": english_T1_line,
        "english_T2_line": english_T2_line,
        "has_proc_family": bool(has_proc_family),
        "has_bot_family": bool(has_bot_family),
    })

out_df = pd.DataFrame(rows, columns=[
    "folio_norm", "folio", "line", "section", "register",
    "n_tokens", "eva_line", "english_T1_line", "english_T2_line",
    "has_proc_family", "has_bot_family"
])

out_df.to_csv(out_path, sep="\t", index=False)
print(f"[t04(py)] Wrote {len(out_df)} line rows to {out_path}")
PYEOF
