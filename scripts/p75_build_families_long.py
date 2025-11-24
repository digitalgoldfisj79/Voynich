#!/usr/bin/env python3
import os
import sys
import json
import csv

BASE = os.path.dirname(__file__)
TOK_FILE = os.path.join(BASE, "..", "p6_voynich_tokens.txt")
RULEBOOK = os.path.join(BASE, "..", "Phase69", "out", "p69_rules_final.json")
OUT_DIR = os.path.join(BASE, "..", "Phase75", "out")
OUT_FILE = os.path.join(OUT_DIR, "p75_families_long.tsv")

def load_tokens(path):
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t and not t.startswith("#"):
                tokens.append(t)
    return tokens

def load_chargram_patterns(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support both {"rules":[...]} and bare list
    rules = data.get("rules", data if isinstance(data, list) else [])
    patterns = set()
    for r in rules:
        if not isinstance(r, dict):
            continue
        if r.get("kind") == "chargram":
            pat = r.get("pattern", "").strip()
            if pat:
                patterns.add(pat)
    return sorted(patterns, key=len, reverse=True)

def main():
    print("=== p75_build_families_long ===")

    if not os.path.isfile(TOK_FILE):
        print(f"[ERR] Tokens file not found: {TOK_FILE}")
        sys.exit(1)
    if not os.path.isfile(RULEBOOK):
        print(f"[ERR] Rulebook not found: {RULEBOOK}")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    tokens = load_tokens(TOK_FILE)
    print(f"[INFO] Loaded {len(tokens)} tokens from {TOK_FILE}")

    patterns = load_chargram_patterns(RULEBOOK)
    if not patterns:
        print("[ERR] No chargram patterns found in rulebook.")
        sys.exit(1)

    print(f"[INFO] Loaded {len(patterns)} chargram patterns: {patterns}")

    # Build families
    rows = []
    no_hit = 0

    for tok in tokens:
        hits = set()
        for pat in patterns:
            if pat in tok:
                hits.add(pat)
        if not hits:
            no_hit += 1
            continue
        family = "-".join(sorted(hits))
        rows.append((family, tok))

    if not rows:
        print("[ERR] No tokens matched any chargram patterns.")
        sys.exit(1)

    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["family", "token"])
        for fam, tok in rows:
            w.writerow([fam, tok])

    print(f"[INFO] Tokens with ≥1 chargram hit: {len(rows)}")
    print(f"[INFO] Tokens with no chargram hit: {no_hit}")
    print(f"[OK] Wrote long-format families → {OUT_FILE}")
    print("=== done ===")

if __name__ == "__main__":
    main()
