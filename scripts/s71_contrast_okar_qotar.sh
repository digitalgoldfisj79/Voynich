#!/data/data/com.termux/files/usr/bin/sh
# POSIX–strict, Termux-safe
# S71 – Cross-folio contrast analysis for stems okar vs qotar

set -eu

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
IN_T03="$BASE/PhaseT/out/t03_enriched_translations.tsv"
OUT_DIR="$BASE/PhaseT/out"
OUT_TMP="$OUT_DIR/s71_okar_qotar_contrast.tsv.tmp"

printf "[s71] BASE:   %s\n" "$BASE"
printf "[s71] IN_T03: %s\n" "$IN_T03"

# Python core inlined safely
python3 << 'EOF'
import pandas as pd
import os

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
IN_T03 = f"{BASE}/PhaseT/out/t03_enriched_translations.tsv"
OUT = f"{BASE}/PhaseT/out/s71_okar_qotar_contrast.tsv.tmp"

df = pd.read_csv(IN_T03, sep="\t", dtype=str)

# Required columns
need = ["folio_norm", "stem", "semantic_family", "role_group",
        "register", "section"]
missing = [c for c in need if c not in df.columns]
if missing:
    print("[s71(py)] ERROR: missing columns:", missing)
else:
    print("[s71(py)] Columns OK:", need)

# Filter relevant rows
mask = df["stem"].isin(["okar", "qotar"])
sub = df[mask].copy()

print(f"[s71(py)] Found {len(sub)} occurrences of okar/qotar across all folios")

# Pivot counts per folio
pivot = (
    sub.groupby(["folio_norm", "stem"])
       .size()
       .reset_index(name="count")
)

# Semantic distribution
sem = (
    sub.groupby(["stem", "semantic_family"])
       .size()
       .reset_index(name="count")
)

# Role-group distribution
roles = (
    sub.groupby(["stem", "role_group"])
       .size()
       .reset_index(name="count")
)

# Register distribution
regs = (
    sub.groupby(["stem", "register"])
       .size()
       .reset_index(name="count")
)

# Section distribution
secs = (
    sub.groupby(["stem", "section"])
       .size()
       .reset_index(name="count")
)

with open(OUT, "w") as f:
    f.write("### S71 okar/qotar Contrast Analysis (ALL folios)\n\n")

    f.write("## Raw counts by folio\n")
    pivot.to_csv(f, sep="\t", index=False)
    f.write("\n\n## Semantic families\n")
    sem.to_csv(f, sep="\t", index=False)
    f.write("\n\n## Role-groups\n")
    roles.to_csv(f, sep="\t", index=False)
    f.write("\n\n## Registers\n")
    regs.to_csv(f, sep="\t", index=False)
    f.write("\n\n## Sections\n")
    secs.to_csv(f, sep="\t", index=False)

print(f"[s71(py)] Wrote contrast file to {OUT}")
EOF

printf "[s71] Done.\n"
