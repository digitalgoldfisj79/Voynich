#!/usr/bin/env python3
import json, os, math, itertools
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(ROOT, "p6_voynich_tokens.txt")
RULES  = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")

def load_tokens(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def load_chargrams(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rules = data.get("rules", data)  # support both wrapped & flat
    pats = []
    for r in rules:
        if r.get("kind") == "chargram" and r.get("pattern"):
            pats.append(r["pattern"])
    # deduplicate, longest-first for stability
    return sorted(set(pats), key=len, reverse=True)

def build_signature(token, patterns):
    """Signature = sorted unique patterns contained in token."""
    found = [p for p in patterns if p in token]
    if not found:
        return None
    return "-".join(sorted(set(found)))

def ed1(a, b):
    """True Levenshtein distance == 1 (no libs, explicit)."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False

    # Same length: check exactly one substitution
    if la == lb:
        diff = sum(1 for x, y in zip(a, b) if x != y)
        return diff == 1

    # Length differs by 1: check single insertion/deletion
    # Ensure a is shorter
    if la > lb:
        a, b = b, a
        la, lb = lb, la

    i = j = diff = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            diff += 1
            if diff > 1:
                return False
            j += 1  # skip one char in longer string
    # Account for trailing char
    diff += (lb - j)
    return diff == 1

def main():
    print("=== p75: within-family single-edit analysis (canonical) ===")

    tokens = load_tokens(TOKENS)
    print(f"[INFO] Loaded {len(tokens)} tokens.")

    patterns = load_chargrams(RULES)
    print(f"[INFO] Loaded {len(patterns)} chargram patterns from rulebook: {patterns}")

    # Build families by chargram signature
    fam2tokens = defaultdict(list)
    for tok in tokens:
        sig = build_signature(tok, patterns)
        if sig:
            fam2tokens[sig].append(tok)

    # Filter to non-trivial families (≥ 2 members)
    fam2tokens = {f: sorted(set(toks)) for f, toks in fam2tokens.items() if len(set(toks)) >= 2}
    print(f"[INFO] Non-trivial families: {len(fam2tokens)}")

    total_pairs = 0
    ed1_pairs = 0

    for fam, toks in fam2tokens.items():
        if len(toks) < 2:
            continue
        for a, b in itertools.combinations(toks, 2):
            total_pairs += 1
            if ed1(a, b):
                ed1_pairs += 1

    if total_pairs == 0:
        print("[WARN] No pairs to analyse; check family construction.")
        return

    frac = ed1_pairs / total_pairs * 100.0
    print(f"[RESULT] Pairs at edit-distance 1: {ed1_pairs} / {total_pairs} "
          f"({frac:.2f} %)")
    print("=== done ===")

if __name__ == "__main__":
    main()
