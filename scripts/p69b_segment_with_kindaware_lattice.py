#!/usr/bin/env python3
"""
p69b_segment_with_kindaware_lattice.py
Conservative Phase 69(b) segmenter — kind-aware and rulebook-faithful.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULEBOOK_PATH = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
DEFAULT_TOKENS_PATH = os.path.join(ROOT, "p6_voynich_tokens.txt")
SEGMENTED_OUT = os.path.join(ROOT, "corpora", "voynich_segmented_p69b.tsv")
MIN_STEM_LEN = 1

def load_tokens():
    tokens_path = None
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import p6_config  # type: ignore
        tokens_path = getattr(p6_config, "VOYNICH_TOKENS", None)
    except Exception:
        pass
    if not tokens_path:
        tokens_path = DEFAULT_TOKENS_PATH
    if not os.path.isfile(tokens_path):
        sys.exit(f"[ERR] Tokens file not found: {tokens_path}")
    with open(tokens_path, "r", encoding="utf-8") as f:
        tokens = [l.strip() for l in f if l.strip()]
    print(f"[INFO] Loaded {len(tokens):6d} tokens from {tokens_path}")
    return tokens

def load_rulebook_json(path):
    if not os.path.isfile(path):
        sys.exit(f"[ERR] Rulebook not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit("[ERR] Expected rulebook JSON to be a list of rule objects.")
    return data

def build_prefix_suffix_tables(rules):
    prefix, suffix = {}, {}
    for r in rules:
        kind = r.get("kind", "").lower()
        pat = r.get("pattern", "")
        w = float(r.get("base_weight", 0.0) or 0.0)
        if not pat or not isinstance(pat, str): continue
        if kind == "prefix":
            if w > prefix.get(pat, 0.0): prefix[pat] = w
        elif kind == "suffix":
            if w > suffix.get(pat, 0.0): suffix[pat] = w
    print(f"[INFO] Loaded {len(prefix)} prefix and {len(suffix)} suffix patterns")
    return prefix, suffix

def best_segmentation(tok, pre, suf):
    L = len(tok)
    if L < MIN_STEM_LEN: return ("", tok, "")
    best, best_score = ("", tok, ""), 0.0
    for p, pw in list(pre.items()) + [("", 0.0)]:
        if p and not tok.startswith(p): continue
        for s, sw in list(suf.items()) + [("", 0.0)]:
            if s and not tok.endswith(s): continue
            start, end = len(p), L - len(s)
            if end <= start: continue
            stem = tok[start:end]
            if len(stem) < MIN_STEM_LEN: continue
            score = pw + sw
            if score > best_score:
                best_score, best = score, (p, stem, s)
    return best

def main():
    print("[INFO] Phase69b kind-aware segmentation starting…")
    toks = load_tokens()
    rules = load_rulebook_json(RULEBOOK_PATH)
    pre, suf = build_prefix_suffix_tables(rules)
    os.makedirs(os.path.dirname(SEGMENTED_OUT), exist_ok=True)
    n_seg = 0
    with open(SEGMENTED_OUT, "w", encoding="utf-8") as out:
        for t in toks:
            p, m, s = best_segmentation(t, pre, suf)
            if p or s: n_seg += 1
            out.write(f"{t}\t{p}\t{m}\t{s}\n")
    print(f"[OK] Wrote → {SEGMENTED_OUT}")
    print(f"[STATS] Tokens with prefix/suffix: {n_seg}/{len(toks)} ({n_seg/len(toks)*100:.2f}%)")

if __name__ == "__main__":
    main()
