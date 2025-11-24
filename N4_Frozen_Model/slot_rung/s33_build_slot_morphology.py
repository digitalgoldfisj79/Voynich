#!/usr/bin/env python3
import sys, csv, math, argparse
from collections import defaultdict

def load_slots(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = []
        for row in reader:
            # Skip garbage/partial rows
            if not row:
                continue
            fam = (row.get("family") or "").strip()
            tok = (row.get("token") or "").strip()
            pos = (row.get("position") or "").strip()
            if not fam or not tok or not pos:
                continue
            rows.append(row)
        return rows

def build_suffix_stats(rows):
    # key: (family, role_group, position, suffix)
    stats = {}
    counts = defaultdict(int)
    tokensets = defaultdict(set)
    fam_totals = {}

    for row in rows:
        fam = (row.get("family") or "").strip()
        role = (row.get("role_group") or "").strip()
        pos = (row.get("position") or "").strip()
        suf = (row.get("suffix") or "").strip()
        if not suf:
            suf = "NA"

        try:
            hits = int(row.get("hits", "0"))
        except ValueError:
            try:
                hits = int(float(row.get("hits", "0")))
            except ValueError:
                hits = 0

        try:
            fam_total = int(row.get("family_total_instances", "0"))
        except ValueError:
            try:
                fam_total = int(float(row.get("family_total_instances", "0")))
            except ValueError:
                fam_total = 0

        fam_totals[fam] = fam_total
        key = (fam, role, pos, suf)
        counts[key] += hits
        tokensets[key].add((row.get("token") or "").strip())

    # Build final table
    for key, total_hits in counts.items():
        fam, role, pos, suf = key
        fam_total = fam_totals.get(fam, 0) or 1
        n_tok = len(tokensets[key]) or 1
        mean_hits = total_hits / float(n_tok)
        coverage = total_hits / float(fam_total)
        stats[key] = {
            "family": fam,
            "role_group": role,
            "position": pos,
            "suffix": suf,
            "n_tokens": n_tok,
            "total_hits": total_hits,
            "mean_hits_per_token": mean_hits,
            "family_total_instances": fam_total,
            "coverage_frac": coverage,
        }
    return stats

def write_tsv(path, stats):
    fields = [
        "family","role_group","position","suffix",
        "n_tokens","total_hits","mean_hits_per_token",
        "family_total_instances","coverage_frac",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for key in sorted(stats.keys()):
            row = stats[key]
            w.writerow({
                "family": row["family"],
                "role_group": row["role_group"],
                "position": row["position"],
                "suffix": row["suffix"],
                "n_tokens": row["n_tokens"],
                "total_hits": row["total_hits"],
                "mean_hits_per_token": f"{row['mean_hits_per_token']:.6f}",
                "family_total_instances": row["family_total_instances"],
                "coverage_frac": f"{row['coverage_frac']:.6f}",
            })

def write_summary(path, stats):
    # Summarise per family/position: which suffixes dominate?
    by_fam_pos = defaultdict(list)
    for key, row in stats.items():
        fam, role, pos, suf = key
        by_fam_pos[(fam, role, pos)].append(row)

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("family\trole_group\tposition\tn_suffixes\ttop_suffixes\n")
        for (fam, role, pos), rows in sorted(by_fam_pos.items()):
            rows_sorted = sorted(rows, key=lambda r: r["coverage_frac"], reverse=True)
            top = []
            for r in rows_sorted[:5]:
                top.append(
                    f"{r['suffix']}:n={r['n_tokens']},cov={r['coverage_frac']:.4f}"
                )
            f.write(
                f"{fam}\t{role}\t{pos}\t{len(rows)}\t"
                + "; ".join(top)
                + "\n"
            )

def write_txt(path, stats):
    by_fam_pos = defaultdict(list)
    for key, row in stats.items():
        fam, role, pos, suf = key
        by_fam_pos[(fam, role, pos)].append(row)

    with open(path, "w", encoding="utf-8") as f:
        f.write("S33 slot × suffix morphology summary\n")
        f.write("========================================\n\n")
        for (fam, role, pos), rows in sorted(by_fam_pos.items()):
            rows_sorted = sorted(rows, key=lambda r: r["coverage_frac"], reverse=True)
            f.write(f"Family: {fam} ({role}), position={pos}\n")
            f.write(f"  Distinct suffixes: {len(rows_sorted)}\n")
            f.write(f"  Top suffixes by coverage (up to 10):\n")
            for r in rows_sorted[:10]:
                f.write(
                    f"    - suffix={r['suffix']}, "
                    f"n_tokens={r['n_tokens']}, "
                    f"total_hits={r['total_hits']}, "
                    f"coverage={r['coverage_frac']:.4f}\n"
                )
            f.write("\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", required=True, help="s29_slot_profiles_with_suffix.tsv")
    ap.add_argument("--core", required=False, help="(ignored; kept for CLI compatibility)")
    ap.add_argument("--out-tsv", required=True)
    ap.add_argument("--out-summary-tsv", required=True)
    ap.add_argument("--out-txt", required=True)
    args = ap.parse_args()

    rows = load_slots(args.slots)
    stats = build_suffix_stats(rows)
    write_tsv(args.out_tsv, stats)
    write_summary(args.out_summary_tsv, stats)
    write_txt(args.out_txt, stats)

if __name__ == "__main__":
    main()
