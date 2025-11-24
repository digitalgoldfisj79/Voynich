#!/usr/bin/env python3
"""
p69b_segment_with_kindaware_lattice.py

Conservative Phase 69(b) segmenter that:
- Reads canonical Voynich tokens from p6_voynich_tokens.txt (as in p6_config.py).
- Reads Phase 69 rulebook from Phase69/out/p69_rules_final.json.
- Uses only REAL fields: kind, pattern, base_weight.
- Only trusts rules with kind == 'prefix' or 'suffix'.
- For each token, considers:
    - no-prefix / no-suffix (whole-token stem)
    - any prefix rule whose pattern matches the start
    - any suffix rule whose pattern matches the end
  and selects the highest scoring (prefix, stem, suffix) candidate.
- If no valid (prefix,suffix) segmentation improves on baseline, emits stem-only.

Output:
- corpora/voynich_segmented_p69b.tsv

Format:
token<TAB>prefix<TAB>stem<TAB>suffix
"""

import json
import os
import sys

# --- Config ------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULEBOOK_PATH = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")

# Fallbacks if p6_config is missing (but it shouldn't be in your core)
DEFAULT_TOKENS_PATH = os.path.join(ROOT, "p6_voynich_tokens.txt")
SEGMENTED_OUT = os.path.join(ROOT, "corpora", "voynich_segmented_p69b.tsv")

MIN_STEM_LEN = 1  # do not allow empty stems


# --- Helpers -----------------------------------------------------------

def load_tokens():
    """Load canonical Voynich tokens as one-per-line."""
    # Try to import p6_config for VOYNICH_TOKENS if available
    tokens_path = None
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import p6_config  # type: ignore
        tokens_path = getattr(p6_config, "VOYNICH_TOKENS", None)
    except Exception:
        tokens_path = None

    if not tokens_path:
        tokens_path = DEFAULT_TOKENS_PATH

    if not os.path.isfile(tokens_path):
        sys.exit(f"[ERR] Tokens file not found: {tokens_path}")

    tokens = []
    with open(tokens_path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                tokens.append(t)

    print(f"[INFO] Loaded {len(tokens):6d} tokens from {tokens_path}")
    return tokens


def load_rulebook_json(path: str):
    """Load Phase69 rulebook as JSON (flat list of rule dicts)."""
    if not os.path.isfile(path):
        sys.exit(f"[ERR] Rulebook not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        sys.exit("[ERR] Expected rulebook JSON to be a list of rule objects.")

    return data


def build_prefix_suffix_tables(rules):
    """
    Build:
      prefix_weights[pattern] = best base_weight for kind=='prefix'
      suffix_weights[pattern] = best base_weight for kind=='suffix'
    Only uses real fields present in your rulebook.
    """
    prefix_weights = {}
    suffix_weights = {}

    for r in rules:
        kind = r.get("kind", "").lower()
        pattern = r.get("pattern", "")
        w = r.get("base_weight", 0.0)

        if not pattern or not isinstance(pattern, str):
            continue
        if not isinstance(w, (int, float)):
            continue

        if kind == "prefix":
            # Keep the strongest weight for this pattern
            if w > prefix_weights.get(pattern, 0.0):
                prefix_weights[pattern] = float(w)
        elif kind == "suffix":
            if w > suffix_weights.get(pattern, 0.0):
                suffix_weights[pattern] = float(w)

    print(f"[INFO] Loaded {len(prefix_weights)} unique prefix patterns")
    print(f"[INFO] Loaded {len(suffix_weights)} unique suffix patterns")
    return prefix_weights, suffix_weights


def best_segmentation(token, prefix_w, suffix_w):
    """
    For a given token, explore candidate (prefix, stem, suffix) where:
      - prefix is "" or any pattern in prefix_w that matches token start
      - suffix is "" or any pattern in suffix_w that matches token end
      - stem is the in-between; len(stem) >= MIN_STEM_LEN
    Score = prefix_weight + suffix_weight
    Baseline = score 0.0 for unsegmented token.
    Only return a segmented form if score > 0.

    Returns (prefix, stem, suffix).
    """
    best = ("", token, "")
    best_score = 0.0

    L = len(token)
    if L < MIN_STEM_LEN:
        return best

    # Candidate prefixes: "" plus any matching literal prefix patterns
    cand_prefixes = [("", 0.0)]
    for p, w in prefix_w.items():
        if token.startswith(p) and len(p) < L:  # leave >=1 char for stem+suffix
            cand_prefixes.append((p, w))

    # Candidate suffixes: "" plus any matching literal suffix patterns
    cand_suffixes = [("", 0.0)]
    for s, w in suffix_w.items():
        if token.endswith(s) and len(s) < L:  # leave >=1 char for prefix+stem
            cand_suffixes.append((s, w))

    # Try all combinations
    for p, pw in cand_prefixes:
        for s, sw in cand_suffixes:
            start = len(p)
            end = L - len(s)
            if end <= start:
                continue
            stem = token[start:end]
            if len(stem) < MIN_STEM_LEN:
                continue

            score = pw + sw
            if score > best_score:
                best_score = score
                best = (p, stem, s)

    return best


# --- Main --------------------------------------------------------------

def main():
    print("[INFO] Phase 69b kind-aware segmentation starting...")

    tokens = load_tokens()
    rules = load_rulebook_json(RULEBOOK_PATH)
    prefix_w, suffix_w = build_prefix_suffix_tables(rules)

    out_path = SEGMENTED_OUT
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    n_seg = 0
    n_any = 0

    with open(out_path, "w", encoding="utf-8") as out:
        for tok in tokens:
            p, stem, s = best_segmentation(tok, prefix_w, suffix_w)
            if p or s:
                n_seg += 1
            if stem:
                n_any += 1
            out.write(f"{tok}\t{p}\t{stem}\t{s}\n")

    print(f"[OK] Wrote segmented tokens → {out_path}")
    print(f"[STATS] Tokens with non-empty prefix or suffix: {n_seg} / {len(tokens)} "
          f"({(n_seg/len(tokens))*100:.2f}%)")
    print(f"[STATS] Tokens with any valid segmentation row: {n_any} / {len(tokens)}")

if __name__ == "__main__":
    main()
