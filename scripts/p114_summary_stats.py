#!/usr/bin/env python3
# p114_summary_stats.py — collate p110/p111/p112/p113 artefacts
import io, json, os, csv

ROOT = "Phase110/out"
FILES = {
    "family_features": f"{ROOT}/p110_family_features.tsv",
    "centroids":       f"{ROOT}/p111_centroids.json",
    "attribution":     f"{ROOT}/p112_attribution.tsv",
    "bootstrap":       f"{ROOT}/p112_bootstrap_summary.json",
    "permutation":     f"{ROOT}/p113_permutation_summary.json",
}
def exists(p): return os.path.exists(p)

def main():
    report = {}
    # centroids
    if exists(FILES["centroids"]):
        with io.open(FILES["centroids"], "r", encoding="utf-8") as f:
            C = json.load(f)
        report["latin_tokens"]  = C.get("latin",{}).get("n_tokens")
        report["arabic_tokens"] = C.get("arabic",{}).get("n_tokens")
    # attribution lines
    if exists(FILES["attribution"]):
        n_attr = sum(1 for _ in io.open(FILES["attribution"], "r", encoding="utf-8")) - 1
        report["n_attributed_families"] = max(n_attr, 0)
    # bootstrap + permutation
    for k in ("bootstrap","permutation"):
        if exists(FILES[k]):
            with io.open(FILES[k], "r", encoding="utf-8") as f:
                report[k] = json.load(f)
        else:
            report[k] = None

    with io.open(f"{ROOT}/p114_run_summary.txt", "w", encoding="utf-8") as w:
        for k,v in report.items():
            w.write(f"{k}: {v}\n")
    print(f"[OK] Summary → {ROOT}/p114_run_summary.txt")

if __name__ == "__main__":
    main()
