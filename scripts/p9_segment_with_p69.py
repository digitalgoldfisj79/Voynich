#!/usr/bin/env python3
"""
p9_segment_with_p69.py

Segment Voynich tokens using the Phase 69 rulebook ONLY.

- Input:
    corpora/voynich_transliteration.txt
    Phase69/out/p69_rules_final.json

- Output:
    corpora/voynich_segmented_p69.txt

Each input token is segmented into glyph units by
longest-match over the glyph inventory derived from
p69_rules_final.json. Output format:

    g1 g2 g3 ...
    g1 g2 ...
    ...

(one segmented token per line, glyphs space-separated)

This keeps Paper 9 consistent with the Phase 69-based
infrastructure used in Papers 1–8, without inventing
new segmentation heuristics.
"""

import os
import sys
import json

# -------- Paths --------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

RULEBOOK_PATH = os.path.join(PROJECT_DIR, "Phase69", "out", "p69_rules_final.json")
INPUT_PATH = os.path.join(PROJECT_DIR, "corpora", "voynich_transliteration.txt")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "corpora", "voynich_segmented_p69.txt")


# -------- Helpers --------

def load_rulebook(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_strings(obj, out_set):
    """
    Recursively collect all string-like values from the rulebook.
    We are conservative: no whitespace; reasonably short; no obvious junk.
    """
    if isinstance(obj, str):
        s = obj.strip()
        if s and (" " not in s) and ("\t" not in s) and len(s) <= 15:
            out_set.add(s)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            collect_strings(k, out_set)
            collect_strings(v, out_set)
    elif isinstance(obj, (list, tuple)):
        for x in obj:
            collect_strings(x, out_set)
    # other types ignored


def build_glyph_inventory(rulebook):
    """
    Build glyph set from rulebook contents.

    Strategy:
      - collect all atomic-looking strings from rulebook
      - keep those that look like plausible EVA/glyph units
      - sort by length (desc) for longest-match segmentation
    """
    raw = set()
    collect_strings(rulebook, raw)

    # Filter: keep alphabetic-ish / bracket-ish EVA-like tokens
    glyphs = set()
    for s in raw:
        # discard if clearly numeric-only or weird
        if all(ch.isdigit() for ch in s):
            continue
        # basic sanity: avoid pure punctuation
        if all(not ch.isalnum() for ch in s):
            continue
        # This is intentionally light-touch; the rulebook
        # already encodes what your system considered valid.
        glyphs.add(s)

    # Also ensure single characters from these are allowed,
    # in case some units are just 'o','y','k',etc.
    for s in list(glyphs):
        if len(s) > 1:
            for ch in s:
                if ch.strip():
                    glyphs.add(ch)

    # Sort longest to shortest for greedy matching
    glyph_list = sorted(glyphs, key=len, reverse=True)
    return glyph_list


def segment_token(token, glyph_list, fallback_single=True):
    """
    Segment a single token via longest-match over glyph_list.

    If no multi-char glyph matches at a position:
      - if fallback_single: take single character as glyph
      - else: take the remaining substring as one glyph
    """
    seg = []
    i = 0
    L = len(token)
    while i < L:
        matched = False
        for g in glyph_list:
            glen = len(g)
            if glen == 0 or glen > (L - i):
                continue
            if token[i:i+glen] == g:
                seg.append(g)
                i += glen
                matched = True
                break
        if not matched:
            if fallback_single:
                seg.append(token[i])
                i += 1
            else:
                seg.append(token[i:])
                break
    return seg


# -------- Main --------

def main():
    # Check inputs
    if not os.path.isfile(RULEBOOK_PATH):
        sys.stderr.write(f"[ERR] Missing rulebook: {RULEBOOK_PATH}\n")
        sys.exit(1)
    if not os.path.isfile(INPUT_PATH):
        sys.stderr.write(f"[ERR] Missing input transliteration: {INPUT_PATH}\n")
        sys.exit(1)

    # Load rulebook and build glyph inventory
    rb = load_rulebook(RULEBOOK_PATH)
    glyph_list = build_glyph_inventory(rb)

    if not glyph_list:
        sys.stderr.write("[ERR] No glyphs extracted from rulebook. Aborting.\n")
        sys.exit(1)

    sys.stderr.write(f"[INFO] Loaded rulebook from {RULEBOOK_PATH}\n")
    sys.stderr.write(f"[INFO] Derived {len(glyph_list)} glyph candidates from Phase69 rulebook.\n")

    # Segment tokens
    n_in = 0
    n_out = 0

    with open(INPUT_PATH, "r", encoding="utf-8", errors="ignore") as f_in, \
         open(OUTPUT_PATH, "w", encoding="utf-8") as f_out:

        for line in f_in:
            line = line.strip()
            if not line:
                continue
            # assume whitespace separates tokens in transliteration
            toks = line.split()
            for tok in toks:
                n_in += 1
                seg = segment_token(tok, glyph_list, fallback_single=True)
                if not seg:
                    # if something goes very wrong, just echo token
                    seg = [tok]
                f_out.write(" ".join(seg) + "\n")
                n_out += 1

    sys.stderr.write(f"[OK] Segmented {n_in} tokens → {n_out} lines\n")
    sys.stderr.write(f"[OK] Wrote segmented tokens to {OUTPUT_PATH}\n")


if __name__ == "__main__":
    main()
