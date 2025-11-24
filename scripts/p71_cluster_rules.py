#!/usr/bin/env python3
import os
import json
from collections import defaultdict

# -------------
# Config
# -------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK_PATHS = [
    os.path.join(ROOT, "corpora", "p6_voynich_tokens.txt"),
    os.path.join(ROOT, "p6_voynich_tokens.txt"),
]
RULEBOOK_JSON = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
OUT_DIR = os.path.join(ROOT, "Phase71", "out")
OUT_PATH = os.path.join(OUT_DIR, "p71_rule_clusters.tsv")

JACCARD_THRESHOLD = 0.20  # can be tuned; keep explicit

# -------------
# Helpers
# -------------

def load_tokens():
    for p in TOK_PATHS:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                toks = [ln.strip() for ln in f if ln.strip()]
            print(f"[INFO] Loaded {len(toks)} tokens from {p}")
            return toks
    raise SystemExit("[ERR] No canonical token file found.")

def load_rulebook():
    if not os.path.isfile(RULEBOOK_JSON):
        raise SystemExit(f"[ERR] Rulebook not found: {RULEBOOK_JSON}")
    with open(RULEBOOK_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Support both wrapped and bare list formats
    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        raise SystemExit("[ERR] Unexpected rulebook JSON format.")
    print(f"[INFO] Loaded {len(rules)} rules from {RULEBOOK_JSON}")
    return rules

def rule_label(r):
    rid = r.get("rule_id", "")
    kind = r.get("kind", "")
    pre = r.get("pre", "")
    suf = r.get("suf", "")
    pat = r.get("pattern", "")
    base = r.get("base_weight", "")
    core = pat or (pre + "*" + suf if (pre or suf) else "")
    return rid or f"{kind}:{core}:{base}"

def match_rule_on_token(r, tok):
    """Deterministic, conservative matching based only on fields we see in p69_rules_final.json."""
    kind = r.get("kind", "")
    pre = r.get("pre", "") or ""
    suf = r.get("suf", "") or ""
    pat = r.get("pattern", "") or ""

    if kind == "prefix" and pre:
        return tok.startswith(pre)
    if kind == "suffix" and suf:
        return tok.endswith(suf)
    if kind == "pair":
        # Seen in file as a combined prefix/suffix condition
        if pre and suf:
            return tok.startswith(pre) and tok.endswith(suf)
        elif pre:
            return tok.startswith(pre)
        elif suf:
            return tok.endswith(suf)
        return False
    if kind == "chargram" and pat:
        # Local pattern; we don't enforce side here
        return pat in tok

    # For any other or malformed kinds, we do nothing.
    return False

def build_rule_hits(tokens, rules):
    rule_hits = {}
    for idx, r in enumerate(rules):
        label = rule_label(r)
        hit_indices = []
        for ti, tok in enumerate(tokens):
            if match_rule_on_token(r, tok):
                hit_indices.append(ti)
        if hit_indices:
            rule_hits[label] = set(hit_indices)
    print(f"[INFO] {len(rule_hits)} / {len(rules)} rules matched at least one token.")
    return rule_hits

def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    union = len(a | b)
    return inter / union

def cluster_rules(rule_hits, threshold):
    labels = list(rule_hits.keys())
    clusters = []
    assigned = set()

    for lbl in labels:
        if lbl in assigned:
            continue
        current = {lbl}
        changed = True
        while changed:
            changed = False
            for other in labels:
                if other in current:
                    continue
                if jaccard(rule_hits[lbl], rule_hits[other]) >= threshold:
                    current.add(other)
                    changed = True
        clusters.append(sorted(list(current)))
        assigned.update(current)

    return clusters

# -------------
# Main
# -------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tokens = load_tokens()
    rules = load_rulebook()
    rule_hits = build_rule_hits(tokens, rules)

    if not rule_hits:
        print("[WARN] No rules fired; nothing to cluster.")
        return

    clusters = cluster_rules(rule_hits, JACCARD_THRESHOLD)

    # Write output
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        out.write("#cluster_id\trule_id\thits\n")
        for ci, cl in enumerate(clusters, start=1):
            for lbl in cl:
                out.write(f"{ci}\t{lbl}\t{len(rule_hits[lbl])}\n")

    print(f"[OK] Wrote {len(clusters)} clusters → {OUT_PATH}")

if __name__ == "__main__":
    main()
