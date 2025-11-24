#!/usr/bin/env sh
set -eu

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"
T4="$BASE/PhaseT/out/t4_tokens_with_t3.tsv"
CAND="$BASE/PhaseT/out/t3_wave2_candidates.tsv"
OUT="$BASE/tests/out_test5_permutation.tsv"

echo "[*] Test5 – permutation p-values for section bias → $OUT"
mkdir -p "$BASE/tests"

if [ ! -f "$T4" ]; then
  echo "[ERROR][Test5] Missing T4 file: $T4" >&2
  exit 1
fi

if [ ! -f "$CAND" ]; then
  echo "[ERROR][Test5] Missing candidates file: $CAND" >&2
  exit 1
fi

python3 - << "PY"
import os, sys, random
import pandas as pd

BASE = os.environ.get("BASE", os.path.join(os.environ.get("HOME",""), "Voynich", "Voynich_Reproducible_Core"))
t4_path = os.path.join(BASE, "PhaseT/out/t4_tokens_with_t3.tsv")
cand_path = os.path.join(BASE, "PhaseT/out/t3_wave2_candidates.tsv")
out_path = os.path.join(BASE, "tests/out_test5_permutation.tsv")

print(f"[Test5(py)] BASE: {BASE}", file=sys.stderr)
print(f"[Test5(py)] T4:   {t4_path}", file=sys.stderr)
print(f"[Test5(py)] CAND: {cand_path}", file=sys.stderr)

df = pd.read_csv(t4_path, sep="\t")
cand = pd.read_csv(cand_path, sep="\t")

stems = cand["stem"].tolist()

df = df[df["stem"].isin(stems)].copy()
df = df[["stem","section"]].dropna()

if df.empty:
    print("[Test5(py)] No rows for candidate stems – nothing to test.", file=sys.stderr)
    with open(out_path,"w") as f:
        f.write("stem\tobs_purity\tperm_p_value\tn_tokens\n")
    sys.exit(0)

sections_all = df["section"].tolist()
n_all = len(sections_all)
print(f"[Test5(py)] Candidate tokens: {n_all}", file=sys.stderr)

rows = []
n_perm = 2000  # decent compromise for Termux

for stem in stems:
    sub = df[df["stem"] == stem]
    n = len(sub)
    if n == 0:
        rows.append((stem, 0.0, 1.0, 0))
        continue

    # observed purity (dominant section fraction)
    counts = sub["section"].value_counts()
    dom_count = counts.iloc[0]
    obs_purity = dom_count / n

    # permutation: draw n random sections from global pool
    worse_or_equal = 0
    for _ in range(n_perm):
        sample = random.choices(sections_all, k=n)
        s_counts = {}
        for sec in sample:
            s_counts[sec] = s_counts.get(sec, 0) + 1
        max_sample = max(s_counts.values())
        perm_purity = max_sample / n
        if perm_purity >= obs_purity:
            worse_or_equal += 1

    p_value = (worse_or_equal + 1) / (n_perm + 1)
    rows.append((stem, obs_purity, p_value, n))

out = pd.DataFrame(rows, columns=["stem","obs_purity","perm_p_value","n_tokens"])
out.to_csv(out_path, sep="\t", index=False)
print(f"[Test5(py)] Wrote {len(out)} rows to {out_path}", file=sys.stderr)
PY

echo "[✓] Test5 complete → $OUT"
