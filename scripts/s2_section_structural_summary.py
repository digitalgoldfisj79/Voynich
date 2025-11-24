#!/usr/bin/env python3
# (script content begins)

import os, sys, csv, math
from collections import defaultdict

BASE = os.path.expanduser(os.environ.get("BASE", "~/Voynich/Voynich_Reproducible_Core"))

IN_PATH = os.environ.get(
    "IN_PATH",
    os.path.join(BASE, "PhaseS", "out", "s1_folio_structural_vectors.tsv"),
)

OUT_SUMMARY = os.environ.get(
    "OUT_SUMMARY",
    os.path.join(BASE, "PhaseS", "out", "s2_section_structural_summary.tsv"),
)

OUT_DISTS = os.environ.get(
    "OUT_DISTS",
    os.path.join(BASE, "PhaseS", "out", "s2_section_centroid_distances.tsv"),
)

def load_rows():
    if not os.path.exists(IN_PATH):
        sys.stderr.write(f"[ERR] Input not found: {IN_PATH}\n")
        sys.exit(1)

    out = []
    with open(IN_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            try:
                out.append(
                    {
                        "folio": r["folio"],
                        "section": r["section"] or "Unknown",
                        "total_tokens": float(r["total_tokens"]),
                        "total_types": float(r["total_types"]),
                        "avg_left_frac": float(r["avg_left_frac"]),
                        "avg_right_frac": float(r["avg_right_frac"]),
                        "avg_unknown_frac": float(r["avg_unknown_frac"]),
                        "avg_left_score": float(r["avg_left_score"]),
                        "avg_right_score": float(r["avg_right_score"]),
                        "avg_rule_hits": float(r["avg_rule_hits"]),
                        "avg_axis_diff": float(r["avg_axis_diff"]),
                    }
                )
            except:
                pass
    return out

def summarise(rows):
    sums = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)
    keys = [
        "total_tokens","total_types",
        "avg_left_frac","avg_right_frac","avg_unknown_frac",
        "avg_left_score","avg_right_score",
        "avg_rule_hits","avg_axis_diff"
    ]

    for r in rows:
        s = r["section"]
        counts[s] += 1
        for k in keys:
            sums[s][k] += r[k]

    out = []
    for s in sorted(counts.keys()):
        n = counts[s]

        def m(key): return sums[s][key] / n if n else 0.0

        out.append(
            {
                "section": s,
                "n_folios": n,
                **{f"mean_{k}": m(k) for k in keys}
            }
        )
    return out

def euclid(a, b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def centroid_dist(summary):
    keys = [
        "mean_avg_left_frac","mean_avg_right_frac","mean_avg_unknown_frac",
        "mean_avg_left_score","mean_avg_right_score",
        "mean_avg_rule_hits","mean_avg_axis_diff"
    ]

    secs = [row["section"] for row in summary]
    vecs = {row["section"]: [row[k] for k in keys] for row in summary}

    dmat = {s1: {s2: euclid(vecs[s1], vecs[s2]) for s2 in secs} for s1 in secs}
    return secs, dmat

def write_summary(path, summary):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        headers = [
            "section","n_folios",
            "mean_total_tokens","mean_total_types",
            "mean_avg_left_frac","mean_avg_right_frac","mean_avg_unknown_frac",
            "mean_avg_left_score","mean_avg_right_score",
            "mean_avg_rule_hits","mean_avg_axis_diff"
        ]
        w.writerow(headers)
        for row in summary:
            w.writerow([row[h] for h in headers])
    os.replace(tmp, path)

def write_dists(path, secs, dmat):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path+".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["section"] + secs)
        for s1 in secs:
            w.writerow([s1] + [f"{dmat[s1][s2]:.6f}" for s2 in secs])
    os.replace(tmp, path)

def main():
    rows = load_rows()
    sys.stderr.write(f"[INFO] Loaded {len(rows)} folio vectors\n")
    summary = summarise(rows)
    write_summary(OUT_SUMMARY, summary)
    secs, dmat = centroid_dist(summary)
    write_dists(OUT_DISTS, secs, dmat)
    sys.stderr.write("[OK] Completed S2\n")

if __name__ == "__main__":
    main()

