#!/usr/bin/env bash
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/PhaseS/out"
FRAMES_PATH="$OUTD/s21_family_frames.tsv"
OUT_TSV="$OUTD/s25_frame_overlap.tsv"
OUT_TXT="$OUTD/s25_frame_overlap.txt"

echo "[S25] BASE        = $BASE"
echo "[S25] FRAMES_PATH = $FRAMES_PATH"
echo "[S25] OUT_TSV     = $OUT_TSV"
echo "[S25] OUT_TXT     = $OUT_TXT"

if [ ! -f "$FRAMES_PATH" ]; then
  echo "[S25][ERR] Frames file not found: $FRAMES_PATH" >&2
  exit 1
fi

mkdir -p "$OUTD"

python3 - << 'PY'
import csv, os

base = os.environ.get("BASE", os.path.join(os.environ["HOME"], "Voynich", "Voynich_Reproducible_Core"))
outd = os.path.join(base, "PhaseS", "out")
frames_path = os.path.join(outd, "s21_family_frames.tsv")
out_tsv = os.path.join(outd, "s25_frame_overlap.tsv")
out_txt = os.path.join(outd, "s25_frame_overlap.txt")

# pattern -> set(families)
pattern_fams = {}

with open(frames_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    required = ["family", "pattern"]
    for c in required:
        if c not in reader.fieldnames:
            raise RuntimeError(f"[S25] Missing required column in s21 file: {c}")
    for row in reader:
        fam = row["family"].strip()
        pat = row["pattern"].strip()
        if not pat:
            continue
        pattern_fams.setdefault(pat, set()).add(fam)

families = sorted({fam for fams in pattern_fams.values() for fam in fams})

# Count overlaps
unique_counts = {fam: 0 for fam in families}
shared2 = 0
shared3 = 0

for pat, fams in pattern_fams.items():
    if len(fams) == 1:
        fam = next(iter(fams))
        unique_counts[fam] += 1
    elif len(fams) == 2:
        shared2 += 1
    elif len(fams) >= 3:
        shared3 += 1

total_patterns = len(pattern_fams)

with open(out_tsv, "w", encoding="utf-8", newline="") as f_out:
    w = csv.writer(f_out, delimiter="\t")
    w.writerow(["metric", "value", "notes"])
    w.writerow(["total_distinct_patterns", total_patterns, "all families combined"])
    for fam in families:
        w.writerow([f"unique_patterns_{fam}", unique_counts[fam], "patterns only in this family"])
    w.writerow(["shared_patterns_in_2_families", shared2, "patterns appearing in exactly 2 families"])
    w.writerow(["shared_patterns_in_3plus_families", shared3, "patterns appearing in all 3 families"])

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("S25 cross-family frame overlap\n")
    f.write("========================================\n\n")
    f.write(f"Total distinct frame patterns: {total_patterns}\n\n")
    for fam in families:
        f.write(f"Family {fam}:\n")
        f.write(f"  Unique patterns (only here): {unique_counts[fam]}\n")
    f.write("\n")
    f.write(f"Patterns shared by exactly 2 families: {shared2}\n")
    f.write(f"Patterns shared by all 3 families   : {shared3}\n")
PY

echo "[S25] Done."
