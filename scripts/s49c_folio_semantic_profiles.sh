#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# Hard-pin BASE to the reproducible core
BASE="$HOME/Voynich/Voynich_Reproducible_Core"

P6="$BASE/PhaseS/out/p6_folio_tokens.tsv"
S46="$BASE/PhaseS/out/s46_stem_semantic_envelopes.tsv"
OUT="$BASE/PhaseS/out/s49c_folio_semantic_profiles.tsv"

echo "[S49c] Building folio-level semantic profiles from p6 + s46..."

python3 <<EOF
import pandas as pd

p6_path  = "$P6"
s46_path = "$S46"
out_path = "$OUT"

# Load inputs
p6  = pd.read_csv(p6_path, sep="\t")
s46 = pd.read_csv(s46_path, sep="\t")

# --- NEW: normalize folio to bare ID like "f100r" ---
def normalize_folio(f):
    # string, take up to first '>' if present, strip spaces
    s = str(f)
    if '>' in s:
        s = s.split('>')[0]
    return s.strip()

p6["folio"] = p6["folio"].apply(normalize_folio)
# -----------------------------------------------


# We only need token + role_group from s46
s46_small = s46[["token", "role_group"]].copy()

# Join semantics onto tokens by exact token form
df = p6.merge(s46_small, on="token", how="left")

rows = []
for folio, g in df.groupby("folio"):
    total_tokens = len(g)

    # tokens with any semantic label
    known = g["role_group"].notna().sum()

    proc = (g["role_group"] == "PROC").sum()
    bot  = (g["role_group"] == "BOT").sum()
    bio  = (g["role_group"] == "BIO").sum()
    other = known - (proc + bot + bio)

    # fractions over known tokens (to avoid diluting by Unknowns)
    denom = known if known > 0 else 1
    proc_frac  = proc  / denom
    bot_frac   = bot   / denom
    bio_frac   = bio   / denom
    other_frac = other / denom

    # dominant group label
    if known == 0:
        dom_label = "UNKNOWN"
    else:
        max_val = max(proc, bot, bio)
        # handle ties / mixed cases conservatively
        winners = []
        if proc == max_val: winners.append("PROC")
        if bot  == max_val: winners.append("BOT")
        if bio  == max_val: winners.append("BIO")
        if len(winners) == 1:
            dom_label = winners[0] + "_DOM"
        else:
            dom_label = "MIXED"

    rows.append({
        "folio": folio,
        "total_tokens": total_tokens,
        "known_semantic_tokens": known,
        "proc_tokens": proc,
        "bot_tokens": bot,
        "bio_tokens": bio,
        "other_semantic_tokens": other,
        "proc_frac": proc_frac,
        "bot_frac": bot_frac,
        "bio_frac": bio_frac,
        "other_frac": other_frac,
        "dominant_semantic_register": dom_label,
    })

out_df = pd.DataFrame(rows).sort_values("folio")
out_df.to_csv(out_path, sep="\\t", index=False)
EOF

echo "[S49c] Wrote folio semantic profiles to: $OUT"
