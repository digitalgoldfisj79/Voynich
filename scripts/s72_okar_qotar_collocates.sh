#!/usr/bin/env bash
# S72: Collocate analysis for okar vs qotar across all folios
# - Uses PhaseT/out/t03_enriched_translations.tsv
# - Only relies on: folio_norm, stem, semantic_family, role_group, register, section
# - Output: PhaseT/out/s72_okar_qotar_collocates.tsv (atomic write)

set -euo pipefail

# Resolve BASE as repo root (same pattern as s71)
this_dir="$(cd "$(dirname "$0")" && pwd)"
BASE="${BASE:-$(cd "${this_dir}/.." && pwd)}"

IN_T03="${BASE}/PhaseT/out/t03_enriched_translations.tsv"
OUT_DIR="${BASE}/PhaseT/out"
TMP_OUT="${OUT_DIR}/s72_okar_qotar_collocates.tsv.tmp"
OUT_TSV="${OUT_DIR}/s72_okar_qotar_collocates.tsv"

echo "[s72] BASE:   ${BASE}"
echo "[s72] IN_T03: ${IN_T03}"
echo "[s72] OUT:    ${OUT_TSV}"

# Sanity checks
if [ ! -f "${IN_T03}" ]; then
  echo "[s72] ERROR: input file not found: ${IN_T03}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

python3 - << 'PY'
import sys
import pandas as pd
from pathlib import Path

in_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

print(f"[s72(py)] Loading t03 from: {in_path}")

df = pd.read_csv(in_path, sep="\t", dtype=str)

required = ["folio_norm", "stem", "semantic_family", "role_group", "register", "section"]
missing = [c for c in required if c not in df.columns]
if missing:
    print(f"[s72(py)] ERROR: missing required columns: {missing}", file=sys.stderr)
    sys.exit(1)

# Clean up and restrict to usable rows
df = df[required].copy()
df = df.dropna(subset=["folio_norm", "stem"])
df["folio_norm"] = df["folio_norm"].astype(str)
df["stem"] = df["stem"].astype(str)

targets = ["okar", "qotar"]

# Precompute folio sets per stem (for all stems)
print("[s72(py)] Building folio sets per stem...")
folios_by_stem = (
    df.groupby("stem")["folio_norm"]
      .apply(lambda s: set(s.unique()))
      .to_dict()
)

# Folios where targets appear
folios_for_target = {
    t: folios_by_stem.get(t, set()) for t in targets
}
print(f"[s72(py)] Folios with okar:  {len(folios_for_target['okar'])}")
print(f"[s72(py)] Folios with qotar: {len(folios_for_target['qotar'])}")

# Restrict to folios that contain at least one of the targets
all_target_folios = set().union(*folios_for_target.values())
df_sub = df[df["folio_norm"].isin(all_target_folios)].copy()

# Build mapping folio -> set of stems in that folio
folio_to_stems = (
    df_sub.groupby("folio_norm")["stem"]
          .apply(lambda s: set(s))
          .to_dict()
)

# Precompute n_folios per stem (within the restricted sub-corpus)
stem_folio_counts = {}
for stem, folios in folios_by_stem.items():
    # Only count folios that are in the all_target_folios universe,
    # so we don't mix in sections where neither okar nor qotar occur.
    stem_folio_counts[stem] = len(folios & all_target_folios)

rows = []

for t in targets:
    tf_folios = folios_for_target[t]
    n_fol_t = len(tf_folios)
    if n_fol_t == 0:
        print(f"[s72(py)] WARNING: no folios found for target {t}", file=sys.stderr)
        continue

    colloc_counts = {}  # stem -> n_folios_with_both

    for folio, stems in folio_to_stems.items():
        if folio not in tf_folios:
            continue
        if t not in stems:
            continue
        for s in stems:
            if s == t:
                continue
            colloc_counts[s] = colloc_counts.get(s, 0) + 1

    # Turn into rows with Jaccard
    for s, n_both in colloc_counts.items():
        n_fol_s = stem_folio_counts.get(s, 0)
        denom = n_fol_t + n_fol_s - n_both
        jaccard = n_both / denom if denom > 0 else 0.0

        rows.append({
            "target_stem": t,
            "collocate_stem": s,
            "n_folios_with_both": n_both,
            "n_folios_with_target": n_fol_t,
            "n_folios_with_collocate": n_fol_s,
            "jaccard_folio": f"{jaccard:.3f}",
        })

if not rows:
    print("[s72(py)] WARNING: no collocates found for okar/qotar", file=sys.stderr)

out_df = pd.DataFrame(rows)

# Sort: by target, then descending n_folios_with_both, then collocate
if not out_df.empty:
    out_df = out_df.sort_values(
        by=["target_stem", "n_folios_with_both", "collocate_stem"],
        ascending=[True, False, True],
        kind="mergesort",
    )

    # Add a rank within each target for convenience
    out_df["rank_within_target"] = (
        out_df.groupby("target_stem")["n_folios_with_both"]
              .rank(method="dense", ascending=False)
              .astype(int)
    )

# Write with a small header block, like s71
with out_path.open("w", encoding="utf-8") as f:
    f.write("### S72 okar/qotar Collocate Analysis (folio-based)\n")
    f.write("## Columns: target_stem, collocate_stem, n_folios_with_both, n_folios_with_target, n_folios_with_collocate, jaccard_folio, rank_within_target\n")
    if not out_df.empty:
        out_df.to_csv(f, sep="\t", index=False)
    else:
        f.write("# (no data)\n")

print(f"[s72(py)] Wrote collocate table to {out_path}")
PY
PY
# end python

