#!/usr/bin/env python3
"""
Phase 69b: Conservative lattice-based segmentation

Uses the validated Phase 69 rulebook (p69_rules_final.json)
to segment Voynich tokens with a slightly more tolerant match:

- Start from the original prefix+stem+suffix patterns.
- For each rule, define its canonical full form:
      full = prefix + stem + suffix
- For each token, accept:
      - exact matches to full (edit_distance = 0), or
      - near matches with Levenshtein distance <= 1 to full
        AND length difference <= 1

For a matched token, we emit:
    token, prefix, stem, suffix, rule_id, edit_distance

If multiple rules match, we keep:
    - the one with smallest edit_distance,
    - ties broken by highest rule "support" if available,
      else by rule_id (stable ordering).

This is intentionally conservative:
it does NOT try to guess new stems, does NOT relax arbitrarily,
and is suitable as a basis for the next evaluation phase.

Run from the root of Voynich_Reproducible_Core:

    python3 scripts/p69b_segment_with_lattice.py

Output:

    corpora/voynich_segmented_p69b.tsv

This script has NO external dependencies beyond the standard library
and p6_config.py + p69_rules_final.json.
"""

import os
import sys
import json

# Import canonical paths from existing config
try:
    from p6_config import VOYNICH_TOKENS
except ImportError:
    print("[ERR] Could not import p6_config.py or VOYNICH_TOKENS.", file=sys.stderr)
    sys.exit(1)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULEBOOK_JSON = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
TOKENS_PATH = os.path.join(ROOT, VOYNICH_TOKENS)
OUT_PATH = os.path.join(ROOT, "corpora", "voynich_segmented_p69b.tsv")


def load_tokens(path: str):
    if not os.path.isfile(path):
        print(f"[ERR] Tokens file not found: {path}", file=sys.stderr)
        sys.exit(1)
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if not t:
                continue
            # Allow either "token" or "id token" formats; keep token as last field
            parts = t.split()
            tokens.append(parts[-1])
    if not tokens:
        print("[ERR] No tokens loaded.", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] Loaded {len(tokens):6d} tokens from {path}")
    return tokens


def load_rulebook(path: str):
    if not os.path.isfile(path):
        print(f"[ERR] Rulebook not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = []

    # We support two likely formats:
    # 1) {"rules": {id: {...}}} or {"rules": [...]} etc.
    # 2) {id: {...}} directly.
    def normalize_rule(rule_id, r):
        pref = r.get("prefix", "")
        stem = r.get("stem", "")
        suff = r.get("suffix", "")
        full = f"{pref}{stem}{suff}"
        if not full:
            return None
        support = r.get("support", 0)
        acc = r.get("accuracy", r.get("acc", 0.0))
        return {
            "id": str(rule_id),
            "prefix": pref,
            "stem": stem,
            "suffix": suff,
            "full": full,
            "support": support,
            "accuracy": acc,
        }

    # Try to interpret structure
    if isinstance(data, dict) and "rules" in data:
        raw = data["rules"]
        if isinstance(raw, dict):
            for rid, r in raw.items():
                nr = normalize_rule(rid, r)
                if nr:
                    rules.append(nr)
        elif isinstance(raw, list):
            for i, r in enumerate(raw):
                rid = r.get("id", i)
                nr = normalize_rule(rid, r)
                if nr:
                    rules.append(nr)
    elif isinstance(data, dict):
        # assume dict of id -> rule
        for rid, r in data.items():
            if isinstance(r, dict):
                nr = normalize_rule(rid, r)
                if nr:
                    rules.append(nr)
    elif isinstance(data, list):
        for i, r in enumerate(data):
            if isinstance(r, dict):
                rid = r.get("id", i)
                nr = normalize_rule(rid, r)
                if nr:
                    rules.append(nr)

    if not rules:
        print("[ERR] No usable rules found in rulebook JSON.", file=sys.stderr)
        sys.exit(1)

    # Sort for stable tie-breaking: more support first, then id
    rules.sort(key=lambda r: (-r["support"], r["id"]))
    print(f"[INFO] Loaded {len(rules)} Phase69 rules from {path}")
    return rules


def edit_distance_leq1(a: str, b: str) -> int:
    """
    Return edit distance if <=1, else return a value >1 quickly.

    Optimized for small differences:
    - If identical: 0
    - If lengths differ by >1: treat as >1
    - Check single insert/delete/substitution cases.
    """
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return 2  # >1

    # Case 1: same length -> allow up to one substitution
    if la == lb:
        diff = 0
        for ca, cb in zip(a, b):
            if ca != cb:
                diff += 1
                if diff > 1:
                    return 2
        return diff  # 1 if exactly one mismatch

    # Case 2: length differs by exactly 1 -> one insert/delete
    # Ensure a is the longer
    if la < lb:
        a, b = b, a
        la, lb = lb, la

    # Now la = lb + 1; try to align with one deletion in a
    i = j = 0
    diff = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            diff += 1
            if diff > 1:
                return 2
            i += 1  # skip one char in longer string
    # If we exited with at most one extra char, it's fine
    return diff if diff <= 1 else 2


def best_rule_match(token: str, rules):
    """
    For a given token, find the best matching rule based on:
    - minimal edit distance to full form (<=1),
    - then higher support,
    - then rule_id (due to sorted input).
    Returns (rule, dist) or (None, None).
    """
    best = None
    best_dist = 2  # >1 means reject
    for r in rules:
        full = r["full"]
        # quick length filter
        if abs(len(token) - len(full)) > 1:
            continue
        d = edit_distance_leq1(token, full)
        if d < best_dist:
            best = r
            best_dist = d
            if d == 0:
                break  # exact match, cannot improve
    if best is None or best_dist > 1:
        return None, None
    return best, best_dist


def segment_tokens(tokens, rules):
    """
    Apply lattice matching to all tokens.
    Return list of (token, prefix, stem, suffix, rule_id, dist) for matches,
    and count of unmatched.
    """
    out = []
    unmatched = 0
    for t in tokens:
        rule, dist = best_rule_match(t, rules)
        if rule is None:
            unmatched += 1
            continue
        out.append((
            t,
            rule["prefix"],
            rule["stem"],
            rule["suffix"],
            rule["id"],
            dist
        ))
    print(f"[INFO] Matched {len(out):6d} / {len(tokens):6d} tokens "
          f"({len(out)/len(tokens)*100:5.2f}%) with edit_distance <= 1")
    return out, unmatched


def write_output(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("#token\tprefix\tstem\tsuffix\trule_id\tedit_distance\n")
        for t, p, s, suf, rid, d in rows:
            f.write(f"{t}\t{p}\t{s}\t{suf}\t{rid}\t{d}\n")
    print(f"[OK] Wrote {len(rows)} segmentations → {path}")


def main():
    print("[INFO] Phase 69b lattice segmentation starting...")
    tokens = load_tokens(TOKENS_PATH)
    rules = load_rulebook(RULEBOOK_JSON)
    rows, unmatched = segment_tokens(tokens, rules)
    if not rows:
        print("[WARN] No tokens matched even with relaxed lattice (<=1 edit).", file=sys.stderr)
    write_output(OUT_PATH, rows)
    print(f"[INFO] Unmatched tokens: {unmatched}")
    print("[INFO] Done. You can now run a coverage/eval script on voynich_segmented_p69b.tsv.")


if __name__ == "__main__":
    main()
