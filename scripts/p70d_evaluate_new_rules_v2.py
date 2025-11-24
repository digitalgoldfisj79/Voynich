#!/usr/bin/env python3
import json
import os
import csv
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_FILE = os.path.join(BASE, "p6_voynich_tokens.txt")
RULEBOOK_JSON = os.path.join(BASE, "Phase69", "out", "p69_rules_final.json")
CLUSTERS_TSV = os.path.join(BASE, "Phase70", "out", "p70b_clusters.tsv")
OUT_TSV = os.path.join(BASE, "Phase70", "out", "p70d_candidates.tsv")

MIN_CLUSTER_COUNT = 30       # how big a cluster must be to consider
MIN_HITS_IN_CORPUS = 50      # how often pattern must appear in full tokens
MIN_PATTERN_LEN = 2          # avoid 1-char junk

def load_tokens(path):
    counts = Counter()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                counts[t] += 1
    return counts

def load_existing_presufs(path):
    if not os.path.isfile(path):
        print(f"[WARN] No rulebook JSON at {path}")
        return set()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    combos = set()
    # p69_rules_final can be dict or list depending on how it was written
    if isinstance(data, dict):
        iterable = data.values()
    elif isinstance(data, list):
        iterable = data
    else:
        print("[WARN] Unexpected JSON structure in rulebook.")
        return set()

    for r in iterable:
        if not isinstance(r, dict):
            continue
        pre = r.get("pre", "")
        suf = r.get("suf", "")
        if pre or suf:
            combos.add((pre, suf))
    return combos

def load_clusters(path):
    rows = []
    if not os.path.isfile(path):
        print(f"[ERR] Missing cluster file: {path}")
        return rows

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header_skipped = False
        for parts in reader:
            # Skip empty/malformed rows
            if not parts or all(p.strip() == "" for p in parts):
                continue

            # Try to detect and skip header
            if not header_skipped:
                lower = [p.lower() for p in parts]
                if ("section" in lower and
                    ("pattern" in lower or "pre" in lower or "suf" in lower)):
                    header_skipped = True
                    continue
                # If it's not a header, fall through and parse it as data

            # We expect: section, pattern, cluster_count, corpus_hits
            if len(parts) < 4:
                # Some earlier scripts printed wonky lines; skip them
                continue

            section = parts[0].strip()
            pattern = parts[1].strip()
            try:
                cluster_count = int(parts[2])
                corpus_hits = int(parts[3])
            except ValueError:
                # Non-numeric row (probably another header), skip
                continue

            if section not in ("prefix", "suffix"):
                # If section label missing or weird, try to infer:
                # Heuristic: treat as prefix if near start of token space
                # but to stay conservative, skip ambiguous.
                continue

            rows.append((section, pattern, cluster_count, corpus_hits))
    return rows

def main():
    os.makedirs(os.path.join(BASE, "Phase70", "out"), exist_ok=True)

    print(f"[INFO] Loading tokens from {TOKENS_FILE}")
    token_counts = load_tokens(TOKENS_FILE)
    total_tokens = sum(token_counts.values())
    print(f"[INFO] Loaded {total_tokens} tokens.")

    print(f"[INFO] Loading existing (pre,suf) combos from {RULEBOOK_JSON}")
    existing = load_existing_presufs(RULEBOOK_JSON)
    print(f"[INFO] Found {len(existing)} existing (pre,suf) combinations in Phase69.")

    print(f"[INFO] Loading uncovered clusters from {CLUSTERS_TSV}")
    clusters = load_clusters(CLUSTERS_TSV)
    print(f"[INFO] Loaded {len(clusters)} cluster rows.")

    candidates = []
    for section, pattern, cl_count, corp_hits in clusters:
        if len(pattern) < MIN_PATTERN_LEN:
            continue
        if cl_count < MIN_CLUSTER_COUNT:
            continue
        if corp_hits < MIN_HITS_IN_CORPUS:
            continue

        # Map to a (pre,suf) proposal depending on section
        if section == "prefix":
            combo = (pattern, "")
        elif section == "suffix":
            combo = ("", pattern)
        else:
            continue

        if combo in existing:
            continue

        candidates.append({
            "section": section,
            "pattern": pattern,
            "cluster_count": cl_count,
            "corpus_hits": corp_hits
        })

    # Sort for readability
    candidates.sort(key=lambda r: (-r["corpus_hits"], -r["cluster_count"], r["pattern"]))

    # Write out
    with open(OUT_TSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["section", "pattern", "cluster_count", "corpus_hits"])
        for r in candidates:
            w.writerow([r["section"], r["pattern"], r["cluster_count"], r["corpus_hits"]])

    print(f"[OK] Suggested {len(candidates)} candidate patterns → {OUT_TSV}")
    if candidates:
        print("[INFO] Top 10 candidates:")
        for r in candidates[:10]:
            print(f"  {r['section']:6s} {r['pattern']:8s} "
                  f"cluster={r['cluster_count']:5d} corpus_hits={r['corpus_hits']:5d}")

if __name__ == "__main__":
    main()
