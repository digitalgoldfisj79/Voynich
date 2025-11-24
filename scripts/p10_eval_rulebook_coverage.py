#!/usr/bin/env python3
import sys, os, json
from collections import Counter

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VOYNICH_TOKENS = os.path.join(BASE_DIR, "p6_voynich_tokens.txt")
DEFAULT_RULEBOOK = os.path.join(BASE_DIR, "Phase69", "out", "p69_rules_final.json")

VERBOSE_TOP = 20  # show more, so we can inspect real patterns

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_tokens(path):
    if not os.path.isfile(path):
        sys.exit(f"[ERR] Tokens file not found: {path}")
    toks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                toks.append(t)
    if not toks:
        sys.exit(f"[ERR] No tokens read from {path}")
    return toks

def normalize_rulebook_data(data):
    """
    Accept either:
      - [ {rule}, {rule}, ... ]
      - { "rules": [ {rule}, ... ] }

    Filter to rules that have at least one non-empty structural cue:
      pre or suf or mid.
    Discard fully empty/wildcard rows that would match everything.
    """
    if isinstance(data, dict) and isinstance(data.get("rules"), list):
        rows = data["rules"]
    elif isinstance(data, list):
        rows = data
    else:
        raise SystemExit("[ERR] Unexpected rulebook format; expected list or {rules:[...]}.")

    rules = []
    dropped_empty = 0

    for r in rows:
        if not isinstance(r, dict):
            continue
        pre = (r.get("pre") or "").strip()
        suf = (r.get("suf") or "").strip()
        mid = (r.get("mid") or "").strip()

        # drop rows with no structural info at all
        if not pre and not suf and not mid:
            dropped_empty += 1
            continue

        label = (r.get("label")
                 or r.get("id")
                 or r.get("name")
                 or f"pre={pre}|mid={mid}|suf={suf}")

        rules.append({
            "pre": pre,
            "mid": mid,
            "suf": suf,
            "label": label
        })

    if dropped_empty:
        print(f"[INFO] Dropped {dropped_empty} empty/wildcard rows from rulebook.")

    if not rules:
        raise SystemExit("[ERR] No usable rules after filtering (all were empty?).")

    return rules

def load_rulebook(path):
    if not os.path.isfile(path):
        raise SystemExit(f"[ERR] Rulebook JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return normalize_rulebook_data(data)

def match_token(token, rule):
    """
    Phase69-style structural match:
      - if pre given: must start with pre
      - if suf given: must end with suf
      - if mid given: must occur somewhere inside (anywhere)
    Empty fields are simply not enforced.
    """
    pre = rule["pre"]
    suf = rule["suf"]
    mid = rule["mid"]

    if pre and not token.startswith(pre):
        return False
    if suf and not token.endswith(suf):
        return False
    if mid and mid not in token:
        return False
    return True

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    rulebook_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RULEBOOK

    print("=== Rulebook coverage evaluation (fixed) ===")
    print(f"[INFO] Tokens file:   {VOYNICH_TOKENS}")
    print(f"[INFO] Rulebook JSON: {rulebook_path}")

    tokens = load_tokens(VOYNICH_TOKENS)
    rules = load_rulebook(rulebook_path)

    print(f"[INFO] Loaded {len(tokens)} tokens.")
    type_counts = Counter(tokens)
    types = list(type_counts.keys())
    print(f"[INFO] Unique types: {len(types)}")
    print(f"[INFO] Usable rules after filtering: {len(rules)}")

    token_hits = 0
    type_hits = 0
    rule_hit_counts = Counter()

    for t in types:
        covered = False
        for ridx, rule in enumerate(rules):
            if match_token(t, rule):
                rule_hit_counts[ridx] += type_counts[t]
                covered = True
        if covered:
            type_hits += 1
            token_hits += type_counts[t]

    total_types = len(types)
    total_tokens = len(tokens)

    cov_types = 100.0 * type_hits / total_types if total_types else 0.0
    cov_tokens = 100.0 * token_hits / total_tokens if total_tokens else 0.0

    print(f"[RESULT] Types covered by ≥1 rule:   {type_hits} / {total_types}  ({cov_types:.2f} %)")
    print(f"[RESULT] Tokens covered by ≥1 rule:  {token_hits} / {total_tokens}  ({cov_tokens:.2f} %)")

    if not rule_hit_counts:
        print("[WARN] No tokens matched any rule. Check rule definitions.")
    else:
        print("[RESULT] Top patterns by token coverage:")
        for ridx, hits in rule_hit_counts.most_common(VERBOSE_TOP):
            r = rules[ridx]
            print(
                f"  {r['label']:<24s} "
                f"pre='{r['pre']}' mid='{r['mid']}' suf='{r['suf']}'  → {hits} tokens"
            )

    print("=== Done ===")

if __name__ == "__main__":
    main()
