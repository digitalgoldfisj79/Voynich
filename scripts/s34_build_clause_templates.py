import csv
import argparse
from collections import defaultdict

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out-tsv", required=True)
    ap.add_argument("--out-txt", required=True)
    return ap.parse_args()

def main():
    args = parse_args()

    templates = defaultdict(lambda: {"count": 0, "examples": []})

    with open(args.frames, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            fam = row.get("family", "")
            pat = row.get("pattern", "")
            count = int(row.get("total", "0"))

            split = pat.split("|")
            if len(split) != 3:
                continue

            L, C, R = split
            key = (fam, L, C, R)
            templates[key]["count"] += count
            templates[key]["examples"].append(pat)

    # write TSV
    with open(args.out_tsv, "w", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["family","template_id","L","C","R","count","pattern"])
        i = 1
        for (fam,L,C,R),info in templates.items():
            tid = f"T_{fam}_{i:04d}"
            w.writerow([fam, tid, L, C, R, info["count"], ";".join(info["examples"])])
            i += 1

    # write TXT summary
    with open(args.out_txt, "w", encoding="utf-8") as f:
        f.write("S34 clause templates\n")
        f.write("=====================================\n\n")
        for (fam,L,C,R),info in templates.items():
            f.write(f"{fam}: {L} | {C} | {R}  (n={info['count']})\n")

if __name__ == "__main__":
    main()
