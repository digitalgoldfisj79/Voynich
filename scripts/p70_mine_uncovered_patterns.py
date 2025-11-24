#!/usr/bin/env python3
import os, json
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(ROOT, "p6_voynich_tokens.txt")
RULEBOOK = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
OUT_DIR = os.path.join(ROOT, "Phase70", "out")
os.makedirs(OUT_DIR, exist_ok=True)

OUT_UNCOVERED = os.path.join(OUT_DIR, "p70_uncovered_tokens.txt")
OUT_STATS = os.path.join(OUT_DIR, "p70_uncovered_patterns.tsv")

MIN_FREQ = 30          # minimum frequency to report a pattern
MAX_LEN = 3            # max prefix/suffix length to test

def load_tokens(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

def load_rulebook_pairs(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        raise SystemExit("[ERR] Unexpected rulebook JSON structure")

    prefixes = set()
    suffixes = set()
    pairs = set()

    for r in rules:
        if not isinstance(r, dict):
            continue
        pre = r.get("pre", "") or r.get("prefix", "") or ""
        suf = r.get("suf", "") or r.get("suffix", "") or ""
        kind = r.get("kind", "").lower()

        if pre:
            prefixes.add(pre)
        if suf:
            suffixes.add(suf)
        if pre or suf:
            pairs.add((pre, suf))

        # if pattern-only rules present
        pat = r.get("pattern", "")
        if kind == "prefix" and pat:
            prefixes.add(pat)
            pairs.add((pat, ""))
        if kind == "suffix" and pat:
            suffixes.add(pat)
            pairs.add(("", pat))

    print(f"[INFO] Loaded {len(prefixes)} prefixes, {len(suffixes)} suffixes, {len(pairs)} (pre,suf) combos from Phase69")
    return prefixes, suffixes, pairs

def covered_by_rulebook(token, prefixes, suffixes, pairs):
    # Any known prefix?
    has_pre = any(token.startswith(p) for p in prefixes)
    # Any known suffix?
    has_suf = any(token.endswith(s) for s in suffixes)
    # Any known (pre,suf) combo?
    if pairs:
        for pre, suf in pairs:
            if pre and suf:
                if token.startswith(pre) and token.endswith(suf):
                    return True
            elif pre and token.startswith(pre):
                return True
            elif suf and token.endswith(suf):
                return True
    # Fallback: if either side hits, count as covered
    return has_pre or has_suf

def main():
    tokens = load_tokens(TOKENS)
    prefixes, suffixes, pairs = load_rulebook_pairs(RULEBOOK)

    uncovered = []
    for t in tokens:
        if not covered_by_rulebook(t, prefixes, suffixes, pairs):
            uncovered.append(t)

    total = len(tokens)
    u_total = len(uncovered)
    u_types = len(set(uncovered))

    print(f"[RESULT] Uncovered tokens: {u_total} / {total} ({u_total/total:.2%})")
    print(f"[RESULT] Uncovered types:  {u_types}")

    with open(OUT_UNCOVERED, "w", encoding="utf-8") as f:
        for t in uncovered:
            f.write(t + "\n")

    # Now mine frequent prefixes/suffixes among uncovered
    pre_counts = Counter()
    suf_counts = Counter()

    for t in uncovered:
        L = len(t)
        if L < 2:
            continue
        for k in range(1, min(MAX_LEN, L) + 1):
            pre_counts[t[:k]] += 1
            suf_counts[t[-k:]] += 1

    # Filter & sort
    pre_items = [(p, c) for p, c in pre_counts.items() if c >= MIN_FREQ]
    suf_items = [(s, c) for s, c in suf_counts.items() if c >= MIN_FREQ]

    pre_items.sort(key=lambda x: -x[1])
    suf_items.sort(key=lambda x: -x[1])

    with open(OUT_STATS, "w", encoding="utf-8") as out:
        out.write("#pattern_type\tpattern\tcount\n")
        for p, c in pre_items:
            out.write(f"prefix\t{p}\t{c}\n")
        for s, c in suf_items:
            out.write(f"suffix\t{s}\t{c}\n")

    print(f"[OK] Wrote uncovered token list → {OUT_UNCOVERED}")
    print(f"[OK] Wrote frequent patterns → {OUT_STATS}")
    print("[NOTE] Next step: manually inspect these patterns and, if plausible, promote to Phase70 rules.")

if __name__ == "__main__":
    main()
