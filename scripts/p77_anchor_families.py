#!/usr/bin/env python3
import os
import pandas as pd

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
FAM = os.path.join(BASE, "Phase75/out/p75_families.tsv")
ENR = os.path.join(BASE, "Phase76/out/p76_section_enrichment.tsv")
OUT_DIR = os.path.join(BASE, "Phase77/out")
ANCHORS_TSV = os.path.join(OUT_DIR, "p77_anchor_families.tsv")
SUMMARY_TXT = os.path.join(OUT_DIR, "p77_anchor_summary.txt")

# Anchor thresholds (tunable, but keep them explicit in paper)
MIN_FRACTION = 0.55
MIN_COUNT = 5

os.makedirs(OUT_DIR, exist_ok=True)

print("=== Phase 77: Anchor families ===")

# 1. Load families
if not os.path.isfile(FAM):
    raise SystemExit(f"[ERR] Families file not found: {FAM}")
fam_df = pd.read_csv(FAM, sep="\t")
if "family_signature" not in fam_df.columns:
    raise SystemExit("[ERR] p75_families.tsv missing 'family_signature' column")
families = set(fam_df["family_signature"].astype(str))

print(f"[INFO] Loaded {len(families)} families from p75_families.tsv")

# 2. Load section enrichment
if not os.path.isfile(ENR):
    raise SystemExit(f"[ERR] Enrichment file not found: {ENR}")
enr_df = pd.read_csv(ENR, sep="\t")

required_cols = {"family", "section", "count", "fraction"}
if not required_cols.issubset(enr_df.columns):
    raise SystemExit(f"[ERR] p76_section_enrichment.tsv missing columns: {required_cols - set(enr_df.columns)}")

print(f"[INFO] Loaded {len(enr_df)} enrichment rows from p76_section_enrichment.tsv")

# 3. Filter to real families only (defensive)
enr_df["family"] = enr_df["family"].astype(str)
enr_df = enr_df[enr_df["family"].isin(families)].copy()

if enr_df.empty:
    raise SystemExit("[ERR] No overlap between families and enrichment table.")

# 4. Apply anchor criteria
anchors = enr_df[
    (enr_df["fraction"] >= MIN_FRACTION) &
    (enr_df["count"] >= MIN_COUNT)
].copy()

anchors = anchors.sort_values(["section", "fraction", "count"], ascending=[True, False, False])

if anchors.empty:
    print("[WARN] No families met anchor criteria; consider lowering thresholds.")
else:
    print(f"[INFO] Anchor families found: {len(anchors)}")

# 5. Write anchor TSV
anchors.to_csv(ANCHORS_TSV, sep="\t", index=False)
print(f"[OK] Anchor families written → {ANCHORS_TSV}")

# 6. Human-readable summary
with open(SUMMARY_TXT, "w", encoding="utf-8") as out:
    out.write("Phase 77: Anchor families summary\n")
    out.write(f"Thresholds: MIN_FRACTION={MIN_FRACTION}, MIN_COUNT={MIN_COUNT}\n")
    out.write(f"Total families considered: {len(families)}\n")
    out.write(f"Anchor families identified: {len(anchors)}\n\n")

    if not anchors.empty:
        out.write("Per-section anchors:\n")
        for sec in sorted(anchors["section"].unique()):
            sub = anchors[anchors["section"] == sec]
            out.write(f"\n[{sec}]\n")
            for _, row in sub.iterrows():
                fam = row["family"]
                cnt = int(row["count"])
                frac = row["fraction"]
                # Get a few example tokens for this family
                ex = fam_df[fam_df["family_signature"] == fam]
                ex_tokens = []
                if "examples" in ex.columns and not ex.empty:
                    # examples column already contains sample tokens
                    ex_tokens = str(ex.iloc[0]["examples"])
                out.write(f"  {fam:25s}  count={cnt:4d}  frac={frac:0.2f}  examples={ex_tokens}\n")

print(f"[OK] Summary written → {SUMMARY_TXT}")
print("=== Phase 77 complete ===")
