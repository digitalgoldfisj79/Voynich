#!/usr/bin/env python3
import os
import csv
import json

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, ".."))

TOKENS_PATH = os.path.join(ROOT, "p6_voynich_tokens.txt")
RULEBOOK_PATH = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
CLUSTERS_PATH = os.path.join(ROOT, "Phase70", "out", "p70b_clusters.tsv")

# Heuristics for suggesting candidates; adjust if needed
MIN_CLUSTER_COUNT = 30      # how frequent a pattern in uncovered set
MIN_HITS_IN_CORPUS = 50     # how many actual tokens it must match
MIN_PATTERN_LEN = 2         # min total length of pre+suf to avoid single-letter noise


def load_existing_rules(path):
    """Load existing (pre,suf) from Phase69 rulebook so we don't suggest duplicates."""
    existing = set()
    if not os.path.isfile(path):
        print(f"[WARN] Rulebook not found at {path}; treating as empty.")
        return existing

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERR] Could not parse rulebook JSON: {e}")
            return existing

    # Allow for both dict and list-of-dicts structures
    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        rules = []

    for r in rules:
        if not isinstance(r, dict):
            continue
        pre = r.get("pre", "") or r.get("prefix", "")
        suf = r.get("suf", "") or r.get("suffix", "")
        existing.add((pre, suf))

    print(f"[INFO] Loaded {len(existing)} existing (pre,suf) combinations from Phase69.")
    return existing


def load_clusters(path):
    """Load cluster patterns from Phase70/out/p70b_clusters.tsv using header-aware parsing."""
    clusters = []
    if not os.path.isfile(path):
        print(f"[ERR] Cluster file not found: {path}")
        return clusters

    with open(path, "r", encoding="utf-8") as f:
        # auto-detect header; assume tab-separated
        sample = f.readline()
        f.seek(0)
        has_header = any(h in sample.lower() for h in ("section", "prefix", "suffix", "count"))

        if has_header:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                try:
                    count = int(row.get("count", "0"))
                except ValueError:
                    continue
                pre = row.get("pre") or row.get("prefix") or ""
                suf = row.get("suf") or row.get("suffix") or ""
                section = row.get("section", "").strip()
                if not pre and not suf:
                    continue
                clusters.append((section, pre, suf, count))
        else:
            # fallback: no header; assume 4 columns
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 4:
                    continue
                section, pre, suf, count_str = parts
                try:
                    count = int(count_str)
                except ValueError:
                    continue
                clusters.append((section.strip(), pre.strip(), suf.strip(), count))

    print(f"[INFO] Loaded {len(clusters)} cluster rows from {path}.")
    return clusters


def count_hits(tokens_path, pre, suf):
    """Count how many tokens in the canonical corpus match a given (pre,suf) pattern."""
    hits = 0
    total = 0

    if not os.path.isfile(tokens_path):
        print(f"[ERR] Tokens file not found: {tokens_path}")
        return hits, total

    with open(tokens_path, "r", encoding="utf-8") as f:
        for line in f:
            tok = line.strip()
            if not tok:
                continue
            total += 1
            if tok.startswith(pre) and tok.endswith(suf):
                hits += 1

    return hits, total


def main():
    existing = load_existing_rules(RULEBOOK_PATH)
    clusters = load_clusters(CLUSTERS_PATH)

    if not clusters:
        print("[WARN] No clusters loaded; nothing to evaluate.")
        return

    print("[INFO] Evaluating uncovered clusters against canonical tokens…")
    print("[INFO] Heuristics: "
          f"MIN_CLUSTER_COUNT={MIN_CLUSTER_COUNT}, "
          f"MIN_HITS_IN_CORPUS={MIN_HITS_IN_CORPUS}, "
          f"MIN_PATTERN_LEN={MIN_PATTERN_LEN}")
    print()
    print("section\tpre\tsuf\tcluster_count\tcorpus_hits")

    n_suggested = 0
    for section, pre, suf, count in clusters:
        # basic sanity filters
        if count < MIN_CLUSTER_COUNT:
            continue
        if len(pre) + len(suf) < MIN_PATTERN_LEN:
            continue

        key = (pre, suf)
        if key in existing:
            continue  # already covered by Phase69

        hits, total = count_hits(TOKENS_PATH, pre, suf)
        if hits < MIN_HITS_IN_CORPUS:
            continue

        print(f"{section}\t{pre}\t{suf}\t{count}\t{hits}")
        n_suggested += 1

    if n_suggested == 0:
        print("[INFO] No new candidates met the thresholds. "
              "This is actually good: it means the remaining 34% is either "
              "genuinely irregular/low-frequency or needs more sensitive methods.")
    else:
        print(f"[OK] Suggested {n_suggested} candidate (pre,suf) patterns "
              "for potential Phase70 rules (manual vetting required).")


if __name__ == "__main__":
    main()
