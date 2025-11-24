#!/usr/bin/env bash
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseS/out"
FRAMES_PATH="$OUTD/s21_family_frames.tsv"
OUT_TSV="$OUTD/s24_frame_js.tsv"
OUT_TXT="$OUTD/s24_frame_js.txt"

echo "[S24] BASE        = $BASE"
echo "[S24] FRAMES_PATH = $FRAMES_PATH"
echo "[S24] OUT_TSV     = $OUT_TSV"
echo "[S24] OUT_TXT     = $OUT_TXT"

if [ ! -f "$FRAMES_PATH" ]; then
  echo "[S24][ERR] Frames file not found: $FRAMES_PATH" >&2
  exit 1
fi

mkdir -p "$OUTD"

python3 - << 'PY'
import csv, math, os

base = os.environ.get("BASE", os.path.join(os.environ["HOME"], "Voynich", "Voynich_Reproducible_Core"))
outd = os.path.join(base, "PhaseS", "out")
frames_path = os.path.join(outd, "s21_family_frames.tsv")
out_tsv = os.path.join(outd, "s24_frame_js.tsv")
out_txt = os.path.join(outd, "s24_frame_js.txt")

def load_distributions(path):
    fam_counts = {}  # family -> pattern -> count
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = ["family", "pattern", "count"]
        for c in required:
            if c not in reader.fieldnames:
                raise RuntimeError(f"[S24] Missing required column in s21 file: {c}")
        for row in reader:
            fam = row["family"].strip()
            pattern = row["pattern"].strip()
            try:
                cnt = int(row["count"])
            except ValueError:
                continue
            fam_counts.setdefault(fam, {})
            fam_counts[fam][pattern] = fam_counts[fam].get(pattern, 0) + cnt
    # convert to normalized distributions
    fam_dists = {}
    for fam, pc in fam_counts.items():
        total = float(sum(pc.values()))
        if total == 0:
            fam_dists[fam] = {}
        else:
            fam_dists[fam] = {pat: c / total for pat, c in pc.items()}
    return fam_dists

def kl(p, q, support):
    eps = 1e-15
    s = 0.0
    for x in support:
        px = p.get(x, 0.0)
        qx = q.get(x, 0.0)
        if px <= 0.0:
            continue
        qx = max(qx, eps)
        s += px * math.log(px / qx, 2)
    return s

def js(p, q):
    support = set(p.keys()) | set(q.keys())
    m = {}
    for x in support:
        m[x] = 0.5 * p.get(x, 0.0) + 0.5 * q.get(x, 0.0)
    return 0.5 * kl(p, m, support) + 0.5 * kl(q, m, support)

dists = load_distributions(frames_path)
families = sorted(dists.keys())

# Prepare TSV
with open(out_tsv, "w", encoding="utf-8", newline="") as f_out:
    w = csv.writer(f_out, delimiter="\t")
    w.writerow(["family_i", "family_j", "js_divergence_bits"])
    for i in range(len(families)):
        for j in range(i+1, len(families)):
            fi, fj = families[i], families[j]
            val = js(dists[fi], dists[fj])
            w.writerow([fi, fj, f"{val:.6f}"])

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("S24 Jensen–Shannon divergence between frame distributions\n")
    f.write("=========================================================\n\n")
    for i in range(len(families)):
        for j in range(i+1, len(families)):
            fi, fj = families[i], families[j]
            val = js(dists[fi], dists[fj])
            f.write(f"{fi} vs {fj}: JS = {val:.6f} bits\n")
PY

echo "[S24] Done."
