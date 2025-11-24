#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$PWD}"

IN_S40="$BASE/PhaseS/out/s40_clause_valency_overlays.tsv"
OUT_T72="$BASE/PhaseT/out/s72_okar_qotar_argument_frames.tsv"

echo "[s72] BASE:  $BASE"
echo "[s72] IN_S40: $IN_S40"
echo "[s72] OUT:   $OUT_T72"

if [ ! -f "$IN_S40" ]; then
  echo "[s72] ERROR: input not found: $IN_S40" >&2
  exit 1
fi

mkdir -p "$BASE/PhaseT/out"

python3 - << 'PY' "$IN_S40" "$OUT_T72"
import sys, os
import pandas as pd

in_path, out_path = sys.argv[1], sys.argv[2]

print(f"[s72(py)] Loading s40 from: {in_path}")
df = pd.read_csv(in_path, sep="\t")

required = [
    "family",
    "role_group",
    "template_id",
    "agent_token",
    "process_token",
    "patient_token",
    "count",
    "clause_role_pattern",
    "valency_id",
    "valency_class",
]

missing = [c for c in required if c not in df.columns]
if missing:
    print(f"[s72(py)] ERROR: required columns missing from s40: {missing}")
    print(f"[s72(py)] Available columns: {list(df.columns)}")
    sys.exit(1)

# We only care about the procedural family + our two verbs
stems = ["okar", "qotar"]

sub = df[df["process_token"].isin(stems)].copy()
print(f"[s72(py)] okar/qotar rows in s40: {len(sub)}")

tmp_path = out_path + ".tmp"

if sub.empty:
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write("### S72 okar/qotar Argument Frames (s40)\n")
        f.write("## No rows found for okar/qotar in s40_clause_valency_overlays.tsv\n")
    os.replace(tmp_path, out_path)
    print(f"[s72(py)] Wrote empty summary to {out_path}")
    sys.exit(0)

# ---- Summary per stem ----
summary_rows = []
for stem in stems:
    s = sub[sub["process_token"] == stem]
    if s.empty:
        continue
    total_count = int(s["count"].sum())
    n_valency = s["valency_id"].nunique()
    n_agent_types = s["agent_token"].nunique()
    n_patient_types = s["patient_token"].nunique()
    summary_rows.append(
        (stem, total_count, n_valency, n_agent_types, n_patient_types)
    )

# ---- Frames aggregated by valency pattern ----
group_cols = [
    "process_token",
    "valency_id",
    "valency_class",
    "clause_role_pattern",
    "agent_token",
    "patient_token",
]

agg = (
    sub.groupby(group_cols, dropna=False)["count"]
    .sum()
    .reset_index()
    .rename(columns={"process_token": "stem"})
)

with open(tmp_path, "w", encoding="utf-8") as f:
    f.write("### S72 okar/qotar Argument Frames (s40)\n")

    f.write("## Summary by stem\n")
    f.write(
        "stem\ttotal_count\tn_valency_patterns\tn_agent_types\tn_patient_types\n"
    )
    for stem, total_count, n_valency, n_agent_types, n_patient_types in summary_rows:
        f.write(
            f"{stem}\t{total_count}\t{n_valency}\t"
            f"{n_agent_types}\t{n_patient_types}\n"
        )

    f.write("\n## Frames aggregated by valency pattern\n")
    f.write(
        "stem\tvalency_id\tvalency_class\tclause_role_pattern"
        "\tagent_token\tpatient_token\tcount\n"
    )
    for _, row in agg.iterrows():
        f.write(
            f"{row['stem']}\t{row['valency_id']}\t{row['valency_class']}\t"
            f"{row['clause_role_pattern']}\t{row['agent_token']}\t"
            f"{row['patient_token']}\t{int(row['count'])}\n"
        )

os.replace(tmp_path, out_path)
print(f"[s72(py)] Wrote argument frames to {out_path}")
PY

echo "[s72] Done."
