#!/usr/bin/env python3
import json
import os
import csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULEBOOK_JSON = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
CLUSTERS_TSV = os.path.join(ROOT, "Phase70", "out", "p70b_clusters.tsv")
TOKENS_TXT = os.path.join(ROOT, "p6_voynich_tokens.txt")
OUT_TSV = os.path.join(ROOT, "Phase70", "out", "p70d_candidates.tsv")

MIN_CLUSTER_COUNT = 30
MIN_CORPUS_HITS = 50
MIN_PATTERN_LEN = 2

def load_tokens(path):
    if not os.path.isfile(path):
        raise SystemExit(f"[ERR] Tokens file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

def load_phase69_patterns(path):
    if not os.path.isfile(path):
        raise SystemExit(f"[ERR] Rulebook JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        raise SystemExit("[ERR] Unexpected rulebook JSON structure.")

    pre_set = set()
    suf_set = set()
    pre_suf_pairs = set()

    for r in rules:
        if not isinstance(r, dict):
            continue
        kind = r.get("kind", "")
        pat = r.get("pattern", "")
        if not pat:
            continue

        if kind == "prefix":
            pre_set.add(pat)
            pre_suf_pairs.add((pat, ""))

        elif kind == "suffix":
            suf_set.add(pat)
            pre_suf_pairs.add(("", pat))

        elif kind in ("affix", "boundary"):
            pre = r.get("pre", "")
            suf = r.get("suf", "")
            if pre or suf:
                pre_suf_pairs.add((pre, suf))
                if pre:
                    pre_set.add(pre)
                if suf:
                    suf_set.add(suf)

    print(f"[INFO] Loaded {len(pre_suf_pairs)} existing (pre,suf) combos from Phase69.")
    return pre_set, suf_set, pre_suf_pairs

def load_clusters(path):
    if not os.path.isfile(path):
        print(f"[WARN] Cluster file not found: {path}")
        return []

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for parts in reader:
            if not parts or len(parts) < 5:
                continue
            section, pre, suf, ccount, chits = parts[:5]
            if pre == "pre" and suf == "suf":
                continue
            try:
                ccount = int(ccount)
                chits = int(chits)
            except ValueError:
                continue
            rows.append((section.strip(), pre.strip(), suf.strip(), ccount, chits))

    print(f"[INFO] Loaded {len(rows)} cluster rows from {path}.")
    return rows

def main():
    os.makedirs(os.path.join(ROOT, "Phase70", "out"), exist_ok=True)

    tokens = load_tokens(TOKENS_TXT)
    print(f"[INFO] Loaded {len(tokens)} tokens.")

    pre_set, suf_set, existing_pairs = load_phase69_patterns(RULEBOOK_JSON)
    clusters = load_clusters(CLUSTERS_TSV)

    candidates = []
    for section, pre, suf, ccount, chits in clusters:
        if pre and len(pre) >= MIN_PATTERN_LEN and chits >= MIN_CORPUS_HITS:
            if pre not in pre_set:
                candidates.append(("prefix", pre, "", ccount, chits))
        if suf and len(suf) >= MIN_PATTERN_LEN and chits >= MIN_CORPUS_HITS:
            if suf not in suf_set:
                candidates.append(("suffix", "", suf, ccount, chits))
        if pre and suf and len(pre) >= MIN_PATTERN_LEN and len(suf) >= MIN_PATTERN_LEN:
            if (pre, suf) not in existing_pairs and chits >= MIN_CORPUS_HITS:
                candidates.append(("combo", pre, suf, ccount, chits))

    seen = set()
    uniq = []
    for kind, pre, suf, ccount, chits in candidates:
        key = (kind, pre, suf)
        if key in seen:
            continue
        seen.add(key)
        uniq.append((kind, pre, suf, ccount, chits))

    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("kind\tpre\tsuf\tcluster_count\tcorpus_hits\n")
        for kind, pre, suf, ccount, chits in sorted(
            uniq, key=lambda r: (-r[4], r[0], r[1], r[2])
        ):
            out.write(f"{kind}\t{pre}\t{suf}\t{ccount}\t{chits}\n")

    print(f"[OK] Suggested {len(uniq)} candidate patterns → {OUT_TSV}")

if __name__ == "__main__":
    main()
