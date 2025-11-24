#!/usr/bin/env bash
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseS/out"
FRAMES_PATH="$OUTD/s21_family_frames.tsv"
OUT_TSV="$OUTD/s23_frame_stats.tsv"
OUT_TXT="$OUTD/s23_frame_stats.txt"

echo "[S23] BASE        = $BASE"
echo "[S23] FRAMES_PATH = $FRAMES_PATH"
echo "[S23] OUT_TSV     = $OUT_TSV"
echo "[S23] OUT_TXT     = $OUT_TXT"

if [ ! -f "$FRAMES_PATH" ]; then
  echo "[S23][ERR] Frames file not found: $FRAMES_PATH" >&2
  exit 1
fi

mkdir -p "$OUTD"

python3 - << 'PY'
import csv, math, os

base = os.environ.get("BASE", os.path.join(os.environ["HOME"], "Voynich", "Voynich_Reproducible_Core"))
outd = os.path.join(base, "PhaseS", "out")
frames_path = os.path.join(outd, "s21_family_frames.tsv")
out_tsv = os.path.join(outd, "s23_frame_stats.tsv")
out_txt = os.path.join(outd, "s23_frame_stats.txt")

def load_frames(path):
    families = {}  # family -> pattern -> count
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = ["family", "pattern", "count"]
        for c in required:
            if c not in reader.fieldnames:
                raise RuntimeError(f"[S23] Missing required column in s21 file: {c}")
        for row in reader:
            fam = row["family"].strip()
            pattern = row["pattern"].strip()
            try:
                cnt = int(row["count"])
            except ValueError:
                continue
            if fam not in families:
                families[fam] = {}
            families[fam][pattern] = families[fam].get(pattern, 0) + cnt
    return families

def stats_for_family(pattern_counts):
    distinct = len(pattern_counts)
    total = sum(pattern_counts.values())
    if total == 0 or distinct == 0:
        return distinct, total, 0, 0, 0.0, 0.0, 0.0
    recurrent_ge2 = sum(1 for c in pattern_counts.values() if c >= 2)
    recurrent_ge5 = sum(1 for c in pattern_counts.values() if c >= 5)
    # entropy in bits
    entropy = 0.0
    for c in pattern_counts.values():
        p = c / total
        entropy -= p * math.log(p, 2)
    # top-k coverage
    sorted_counts = sorted(pattern_counts.values(), reverse=True)
    top10 = sum(sorted_counts[:10])
    top50 = sum(sorted_counts[:50])
    top10_cov = top10 / total
    top50_cov = top50 / total
    return distinct, total, recurrent_ge2, recurrent_ge5, entropy, top10_cov, top50_cov

families = load_frames(frames_path)

# Write TSV
with open(out_tsv, "w", encoding="utf-8", newline="") as f_out:
    w = csv.writer(f_out, delimiter="\t")
    w.writerow([
        "family",
        "distinct_patterns",
        "total_instances",
        "recurrent_ge2",
        "recurrent_ge5",
        "entropy_bits",
        "top10_coverage",
        "top50_coverage",
    ])
    for fam in sorted(families.keys()):
        st = stats_for_family(families[fam])
        w.writerow([fam] + list(st))

# Write TXT summary
with open(out_txt, "w", encoding="utf-8") as f:
    f.write("S23 frame statistics by family\n")
    f.write("========================================\n\n")
    for fam in sorted(families.keys()):
        distinct, total, r2, r5, ent, cov10, cov50 = stats_for_family(families[fam])
        f.write(f"Family: {fam}\n")
        f.write(f"  Distinct patterns      : {distinct}\n")
        f.write(f"  Total frame instances  : {total}\n")
        f.write(f"  Recurrent patterns ≥2  : {r2}\n")
        f.write(f"  Recurrent patterns ≥5  : {r5}\n")
        f.write(f"  Entropy (bits)         : {ent:.4f}\n")
        f.write(f"  Top-10 coverage        : {cov10:.4%}\n")
        f.write(f"  Top-50 coverage        : {cov50:.4%}\n")
        f.write("\n")
PY

echo "[S23] Done."
