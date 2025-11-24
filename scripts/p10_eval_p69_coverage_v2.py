#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import sys
if len(sys.argv) > 1:
    RULEBOOK_JSON = sys.argv[1]
else:
    RULEBOOK_JSON = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
TOKENS_TXT = os.path.join(BASE, "p6_voynich_tokens.txt")
if not os.path.isfile(TOKENS_TXT):
    # fallback to corpora if needed
    alt = os.path.join(BASE, "corpora", "p6_voynich_tokens.txt")
    if os.path.isfile(alt):
        TOKENS_TXT = alt

def load_tokens(path):
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if not t:
                continue
            # allow for possible "folio token" formats; keep last field as token
            parts = t.split()
            tokens.append(parts[-1])
    return tokens

def load_rulebook(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expect a list of rule-like dicts
    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        raise SystemExit("[ERR] Unexpected JSON structure in p69_rules_final.json")

    parsed = []
    for r in rules:
        # We try to be permissive, because formats shift
        kind = r.get("kind") or r.get("type") or ""
        patt = r.get("pattern") or r.get("value") or ""

        # Some variants may instead store explicit prefix/suffix fields
        prefix = r.get("prefix", "")
        suffix = r.get("suffix", "")
        pair = None

        if kind == "prefix" and patt:
            prefix = patt
        elif kind == "suffix" and patt:
            suffix = patt
        elif kind in ("pair", "prefix+suffix") and patt:
            # e.g. "qo+dy"
            if "+" in patt:
                p, s = patt.split("+", 1)
                prefix, suffix = p, s
            else:
                # fall back: treat as prefix-only if no '+'
                prefix = patt

        if prefix and suffix:
            pair = (prefix, suffix)

        if not (prefix or suffix or pair):
            # no usable pattern, skip
            continue

        parsed.append({
            "kind": kind,
            "prefix": prefix,
            "suffix": suffix,
            "pair": pair,
        })

    if not parsed:
        raise SystemExit("[ERR] No usable rules parsed from rulebook JSON")

    print(f"[INFO] Loaded {len(parsed)} usable rules from p69_rules_final.json")
    return parsed

def token_matches_rule(tok, rule):
    p = rule["prefix"]
    s = rule["suffix"]
    pair = rule["pair"]

    if pair:
        pre, suf = pair
        return tok.startswith(pre) and tok.endswith(suf)
    if p and tok.startswith(p):
        return True
    if s and tok.endswith(s):
        return True
    return False

def main():
    if not os.path.isfile(TOKENS_TXT):
        raise SystemExit(f"[ERR] Tokens file not found: {TOKENS_TXT}")
    if not os.path.isfile(RULEBOOK_JSON):
        raise SystemExit(f"[ERR] Rulebook JSON not found: {RULEBOOK_JSON}")

    tokens = load_tokens(TOKENS_TXT)
    rules = load_rulebook(RULEBOOK_JSON)

    n_tokens = len(tokens)
    type_counts = Counter(tokens)
    types = list(type_counts.keys())
    n_types = len(types)

    covered_tokens = 0
    covered_types = 0

    # per-rule support diagnostics
    rule_support = Counter()

    for t in types:
        matched = False
        for idx, r in enumerate(rules):
            if token_matches_rule(t, r):
                matched = True
                rule_support[idx] += type_counts[t]
        if matched:
            covered_types += 1

    for t in tokens:
        if any(token_matches_rule(t, r) for r in rules):
            covered_tokens += 1

    pct_types = 100.0 * covered_types / max(1, n_types)
    pct_tokens = 100.0 * covered_tokens / max(1, n_tokens)

    print("[RESULT] Phase 69 rulebook coverage (simple pattern hits):")
    print(f"  Types covered by ≥1 rule:   {covered_types} / {n_types}  ({pct_types:.2f} %)")
    print(f"  Tokens covered by ≥1 rule:  {covered_tokens} / {n_tokens}  ({pct_tokens:.2f} %)")

    # optional: show top rules by token support
    top = rule_support.most_common(10)
    if top:
        print("  Top 10 rules by token coverage (index → hits):")
        for idx, cnt in top:
            r = rules[idx]
            desc = []
            if r["pair"]:
                desc.append(f"{r['pair'][0]}+{r['pair'][1]}")
            if r["prefix"] and not r["pair"]:
                desc.append(f"pre={r['prefix']}")
            if r["suffix"] and not r["pair"]:
                desc.append(f"suf={r['suffix']}")
            print(f"    #{idx:03d}: {', '.join(desc)} → {cnt} tokens")


if __name__ == "__main__":
    main()
