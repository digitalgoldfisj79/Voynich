#!/usr/bin/env python3
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_PATH = os.path.join(BASE, "p6_voynich_tokens.txt")
RULEBOOK_PATH = os.path.join(BASE, "Phase69", "out", "p69_rules_final.json")

def load_tokens(path):
    toks = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            toks.append(ln)
    return toks

def load_rules(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Handle both {"rules":[...]} and [...] just in case
    if isinstance(data, dict) and "rules" in data:
        raw_rules = data["rules"]
    elif isinstance(data, list):
        raw_rules = data
    else:
        raise SystemExit("[ERR] Unexpected rulebook format; expected object with 'rules' or a list]")

    rules = []
    for r in raw_rules:
        if not isinstance(r, dict):
            continue
        if r.get("kind") != "chargram":
            continue
        patt = r.get("pattern", "").strip()
        if not patt:
            continue
        side = r.get("side", "any")
        rules.append({"pattern": patt, "side": side})
    if not rules:
        raise SystemExit("[ERR] No usable chargram rules found in rulebook.")
    return rules

def match(rule, tok):
    p = rule["pattern"]
    side = rule["side"]
    if side == "left":
        return tok.startswith(p)
    elif side == "right":
        return tok.endswith(p)
    else:  # any/unspecified
        return p in tok

def main():
    print("=== Phase 69 chargram coverage (correct) ===")
    print(f"[INFO] Tokens file:   {TOKENS_PATH}")
    print(f"[INFO] Rulebook JSON: {RULEBOOK_PATH}")

    tokens = load_tokens(TOKENS_PATH)
    types = sorted(set(tokens))
    rules = load_rules(RULEBOOK_PATH)

    print(f"[INFO] Loaded {len(tokens)} tokens ({len(types)} types).")
    print(f"[INFO] Loaded {len(rules)} concrete chargram rules.")

    covered_token_flags = [False] * len(tokens)
    covered_types = set()
    hits = [0] * len(rules)

    for i, tok in enumerate(tokens):
        for j, r in enumerate(rules):
            if match(r, tok):
                covered_token_flags[i] = True
                hits[j] += 1
                covered_types.add(tok)

    cov_tokens = sum(covered_token_flags)
    cov_types = len(covered_types)

    print(f"[RESULT] Types with ≥1 rule-hit:   {cov_types} / {len(types)} "
          f"({cov_types / len(types) * 100:.2f}%)")
    print(f"[RESULT] Tokens with ≥1 rule-hit:  {cov_tokens} / {len(tokens)} "
          f"({cov_tokens / len(tokens) * 100:.2f}%)")

    print("[RESULT] Top 15 patterns by token coverage:")
    for j, c in sorted(enumerate(hits), key=lambda x: x[1], reverse=True)[:15]:
        r = rules[j]
        print(f"  pattern={r['pattern']!r:6} side={r['side']:<5} hits={c}")

    print("=== Done ===")

if __name__ == "__main__":
    main()
