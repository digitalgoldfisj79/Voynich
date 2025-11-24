#!/usr/bin/env python3
"""
Corrected: All paths now point to:
  ~/Voynich/Voynich_Reproducible_Core/Phase70/{in,out}
"""

import os
import sys
from collections import Counter

# Correct and explicit BASE
BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")

TOKENS_PATH = os.path.join(BASE, "corpora", "p6_voynich_tokens.txt")
IN_DIR      = os.path.join(BASE, "Phase70", "in")
OUT_DIR     = os.path.join(BASE, "Phase70", "out")
PREF_PATH   = os.path.join(IN_DIR, "p70_prefixes.txt")
SUFF_PATH   = os.path.join(IN_DIR, "p70_suffixes.txt")

def load_list(path):
    items = []
    if not os.path.exists(path):
        return items
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            item = line.strip()
            if item:
                items.append(item)
    items.sort(key=lambda x: (-len(x), x))   # longest first, then lexicographically
    return items

def segment_token(token, prefixes, suffixes):
    n = len(token)
    if n < 2:
        return ("", token, "")

    # prefix selection
    prefix = ""
    for p in prefixes:
        if len(p) < n and token.startswith(p):
            prefix = p
            break

    # suffix selection
    remaining = n - len(prefix)
    suffix = ""
    for s in suffixes:
        if len(s) < remaining and token.endswith(s):
            suffix = s
            break

    start = len(prefix)
    end   = n - len(suffix)
    stem  = token[start:end]

    if stem == "":
        return ("", token, "")

    return (prefix, stem, suffix)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    prefixes = load_list(PREF_PATH)
    suffixes = load_list(SUFF_PATH)

    if not prefixes and not suffixes:
        print("[WARN] No affixes loaded — every token will be treated as bare stem.")

    token_segments = []
    type_counter   = Counter()

    with open(TOKENS_PATH, "r", encoding="utf-8") as f:
        for tok_id, line in enumerate(f, start=1):
            token = line.strip()
            if not token:
                continue
            pfx, stem, sfx = segment_token(token, prefixes, suffixes)
            token_segments.append((tok_id, token, pfx, stem, sfx))
            type_counter[(pfx, stem, sfx)] += 1

    # write token-level file
    tok_out = os.path.join(OUT_DIR, "p71_schemeC_tokens.tsv")
    with open(tok_out, "w", encoding="utf-8") as f:
        f.write("tok_id\ttoken\tprefix\tstem\tsuffix\n")
        for (tok_id, token, pfx, stem, sfx) in token_segments:
            f.write(f"{tok_id}\t{token}\t{pfx}\t{stem}\t{sfx}\n")

    # write type-level file
    types_out = os.path.join(OUT_DIR, "p71_schemeC_types.tsv")
    with open(types_out, "w", encoding="utf-8") as f:
        f.write("stem_id\tprefix\tstem\tsuffix\tcount\n")
        for stem_id, ((pfx, stem, sfx), cnt) in enumerate(
                sorted(type_counter.items(), key=lambda x: (-x[1], x[0])),
                start=1):
            f.write(f"{stem_id}\t{pfx}\t{stem}\t{sfx}\t{cnt}\n")

    print(f"[OK] Wrote token segments → {tok_out}")
    print(f"[OK] Wrote type segments  → {types_out}")

if __name__ == "__main__":
    main()
