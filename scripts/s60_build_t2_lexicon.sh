#!/usr/bin/env sh
# Build T2 functional lexicon from t03_enriched_translations.tsv
# Uses semantic_family + role_group deployment to assign:
#   PROC_VERB / BOT_ENTITY / BIO_STATE
# with confidence tiers based on role-group agreement.

set -eu

BASE=${BASE:-"$PWD"}

IN_T03="$BASE/PhaseT/out/t03_enriched_translations.tsv"
OUT_META="$BASE/metadata"
OUT_FILE="$OUT_META/t2_stem_functional_lexicon.tsv"

echo "[s60] BASE:   $BASE"
echo "[s60] IN_T03: $IN_T03"
echo "[s60] OUT:    $OUT_FILE"

if [ ! -f "$IN_T03" ]; then
  echo "[s60] ERROR: missing input file: $IN_T03" >&2
  exit 1
fi

mkdir -p "$OUT_META"

# Run the classifier in Python so we can use pandas safely
T03_PATH="$IN_T03" OUT_PATH="$OUT_FILE" python3 << 'PY'
import os
import math
import pandas as pd
from collections import Counter, defaultdict

t03_path = os.environ["T03_PATH"]
out_path = os.environ["OUT_PATH"]

print(f"[s60(py)] Loading t03 from: {t03_path}")

df = pd.read_csv(t03_path, sep="\t", dtype=str, keep_default_na=False)

# Required columns
required = ["stem", "semantic_family", "role_group"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise SystemExit(f"[s60(py)] ERROR: missing columns in t03: {missing}")

# Filter non-empty stems
df = df[df["stem"].str.len() > 0].copy()
print(f"[s60(py)] Rows with non-empty stem: {len(df)}")

# Normalise role_group to core categories only
def normalise_rg(x: str) -> str:
    x = (x or "").strip().upper()
    if x in ("PROC", "BOT", "BIO"):
        return x
    return ""

df["role_group_norm"] = df["role_group"].apply(normalise_rg)

# Hyperparameters
FAMILY_MIN_FRAC = 0.80   # semantic dominance threshold (unchanged)
# Role-group agreement → confidence tiers
HIGH_THR = 0.80
MED_THR  = 0.60
LOW_THR  = 0.40

def assign_conf(target_rg_frac: float):
    """Map target_rg_frac → confidence label or None."""
    if math.isnan(target_rg_frac):
        return None
    if target_rg_frac >= HIGH_THR:
        return "HIGH"
    if target_rg_frac >= MED_THR:
        return "MEDIUM"
    if target_rg_frac >= LOW_THR:
        return "LOW"
    return None

# Map semantic families to target functional category
family_to_cat = {
    "F_PROC_CORE": "PROC",
    "F_BOTANICAL_CORE": "BOT",
    "F_BIO_CORE": "BIO",
}

# Map functional category → label + rule_id
cat_to_func = {
    "PROC": ("PROC_VERB",  "R_PROC_VERB"),
    "BOT":  ("BOT_ENTITY", "R_BOT_ENTITY"),
    "BIO":  ("BIO_STATE",  "R_BIO_STATE"),
}

records = []

for stem, g in df.groupby("stem", sort=True):
    n_tokens = len(g)

    # --- Semantic-family dominance ---
    fam_counts = Counter(g["semantic_family"])
    # Ignore empty families
    fam_counts = Counter({k: v for k, v in fam_counts.items() if k})
    if not fam_counts:
        continue

    dom_family, dom_count = fam_counts.most_common(1)[0]
    dom_family_frac = dom_count / float(n_tokens)

    # Only consider stems with clear family dominance
    if dom_family_frac < FAMILY_MIN_FRAC:
        continue

    target_cat = family_to_cat.get(dom_family)
    if not target_cat:
        # Not a PROC/BOT/BIO core — skip for T2
        continue

    # --- Role-group deployment ---
    rg_counts = Counter(g["role_group_norm"])
    # Exclude empty role_group for denominator
    total_rg = sum(v for k, v in rg_counts.items() if k)

    if total_rg == 0:
        # No usable role_group info — stay at T1
        continue

    target_rg_count = rg_counts.get(target_cat, 0)
    target_rg_frac = target_rg_count / float(total_rg)

    confidence = assign_conf(target_rg_frac)
    if confidence is None:
        # Too mixed/uncertain — no T2 label
        continue

    func_label, rule_id = cat_to_func[target_cat]

    evidence = "T03,S46,S56,S59 (semantic+role_group)"
    notes = (
        f"dom_family={dom_family}; "
        f"dom_family_frac={dom_family_frac:.3f}; "
        f"n_tokens={n_tokens}; "
        f"target_cat={target_cat}; "
        f"target_rg_frac={target_rg_frac:.3f}; "
        f"rg_counts={dict(rg_counts)}"
    )

    records.append({
        "stem": stem,
        "functional_label": func_label,
        "confidence": confidence,
        "rule_id": rule_id,
        "evidence": evidence,
        "notes": notes,
    })

out_df = pd.DataFrame(records, columns=[
    "stem",
    "functional_label",
    "confidence",
    "rule_id",
    "evidence",
    "notes",
])

# Sort by stem for stability
out_df = out_df.sort_values("stem", kind="mergesort")

out_df.to_csv(out_path, sep="\t", index=False)
print(f"[s60(py)] Wrote {len(out_df)} stem mappings to {out_path}")
PY

echo "[s60] Done."
