#!/usr/bin/env python3
import os
import json
import sys
from collections import defaultdict, Counter

# -------- config --------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRANS_FILE   = os.path.join(ROOT, "corpora", "voynich_transliteration.txt")
TOK_FILE     = os.path.join(ROOT, "p6_voynich_tokens.txt")
RULEBOOK_JSON = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
ANCHORS_FILE  = os.path.join(ROOT, "Phase77", "out", "p77_anchor_families.tsv")
SECTIONS_MAP  = os.path.join(ROOT, "meta", "sections_map.tsv")

OUT_MAP   = os.path.join(ROOT, "Phase81", "out", "p81_anchor_token_map.tsv")
OUT_STATS = os.path.join(ROOT, "Phase81", "out", "p81_anchor_stats.txt")

os.makedirs(os.path.dirname(OUT_MAP), exist_ok=True)


# -------- helpers --------

def load_sections_map(path):
    if not os.path.isfile(path):
        print(f"[WARN] sections_map.tsv not found at {path}; all folios → 'Unknown'", file=sys.stderr)
        return {}
    m = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            folio, sec = parts[0].strip(), parts[1].strip()
            m[folio] = sec
    return m


def load_tokens(path):
    if not os.path.isfile(path):
        print(f"[ERR] tokens file not found: {path}", file=sys.stderr)
        sys.exit(1)
    toks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                toks.append(t)
    return toks


def load_rulebook_chargrams(path):
    if not os.path.isfile(path):
        print(f"[ERR] rulebook JSON not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = data.get("rules", data)  # handle {"rules":[...]} or bare list
    patterns = []

    for r in rules:
        if not isinstance(r, dict):
            continue
        kind = r.get("kind", "")
        if kind != "chargram":
            continue
        pat = r.get("pattern", "")
        side = r.get("pred_side", "any")
        if not pat:
            continue
        # normalize side
        side = str(side).lower()
        if side not in ("left", "right", "any"):
            side = "any"
        patterns.append((r.get("rule_id", pat), pat, side))

    print(f"[INFO] Loaded {len(patterns)} chargram patterns from rulebook.")
    return patterns


def load_anchor_families(path):
    """
    Expects Phase77/out/p77_anchor_families.tsv with at least:
      family_signature <tab> section
    """
    anchors = {}
    if not os.path.isfile(path):
        print(f"[WARN] Anchor file not found: {path}", file=sys.stderr)
        return anchors
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            fam = parts[0].strip()
            sec = parts[1].strip()
            anchors[fam] = sec
    print(f"[INFO] Loaded {len(anchors)} anchor families.")
    return anchors


def rebuild_folio_token_map(trans_path):
    """
    Parse voynich_transliteration.txt into a flat list of tokens with folio IDs.
    Uses the same basic segmentation logic as p6_build_voynich_tokens.py:
      - ignore metadata lines starting with '<!' etc
      - take lines with <fXXr.N> and split token sequences on spaces/dots
      - drop empty fragments
    Returns: list of (folio, token)
    """
    if not os.path.isfile(trans_path):
        print(f"[ERR] Transliteration file not found: {trans_path}", file=sys.stderr)
        sys.exit(1)

    mapping = []
    current_folio = None

    with open(trans_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue

            # folio line like "<f1r> ..."
            if line.startswith("<f") and ">" in line and ".1" not in line:
                # header line
                tag = line.split(">")[0] + ">"
                folio = tag.split(">")[0].strip("<>")
                # e.g. "f1r"
                if folio.startswith("f") and (folio.endswith("r") or folio.endswith("v")):
                    current_folio = folio
                continue

            # text line like "<f1r.1,@P0>\tfachys.ykal..."
            if line.startswith("<f") and ">" in line:
                before, after = line.split(">", 1)
                folio_tag = before.split(">")[0].strip("<>")
                # normalize folio id from folio_tag
                # folio_tag looks like f1r.1,@P0 ; extract f1r
                base = folio_tag.split(".", 1)[0]
                if base.startswith("f") and (base.endswith("r") or base.endswith("v")):
                    current_folio = base
                text = after.strip()
            else:
                # continuation: text only, assume same folio
                text = line.strip()

            if current_folio is None or not text:
                continue

            # strip any leading <%> or similar markers
            text = text.replace("<%>", "").strip()
            # split on spaces then dots (EVA-style)
            for chunk in text.split():
                for tok in chunk.split("."):
                    tok = tok.strip()
                    if tok and not tok.startswith("<") and not tok.endswith(">"):
                        mapping.append((current_folio, tok))

    print(f"[INFO] Rebuilt folio-token map from transliteration: {len(mapping)} tokens.")
    return mapping


def match_tokens_to_folios(corpus_tokens, folio_tokens):
    """
    Align tokens from p6_voynich_tokens.txt with (folio, tok) sequence
    from transliteration. We assume identical order and content.
    """
    if len(corpus_tokens) != len(folio_tokens):
        print(f"[WARN] Token count mismatch: corpus={len(corpus_tokens)} vs translit={len(folio_tokens)}", file=sys.stderr)
    n = min(len(corpus_tokens), len(folio_tokens))
    mapping = []
    mismatches = 0
    for i in range(n):
        t = corpus_tokens[i]
        folio, t2 = folio_tokens[i]
        if t != t2:
            mismatches += 1
        mapping.append((folio, t))
    if mismatches:
        print(f"[WARN] {mismatches} / {n} token mismatches in alignment (this may reflect minor normalization differences).", file=sys.stderr)
    return mapping


def find_pattern_hits(tokens, patterns):
    """
    For each token, record which chargram rules hit.
    Returns dict: idx -> set(rule_id)
    """
    hits = {}
    for idx, tok in enumerate(tokens):
        tok_hits = []
        for rule_id, pat, side in patterns:
            if side == "left":
                if tok.startswith(pat):
                    tok_hits.append(rule_id)
            elif side == "right":
                if tok.endswith(pat):
                    tok_hits.append(rule_id)
            else:  # any
                if pat in tok:
                    tok_hits.append(rule_id)
        if tok_hits:
            hits[idx] = set(tok_hits)
    return hits


def load_families(path):
    """
    Phase75/out/p75_families.tsv:
      family_signature \t count \t examples
    """
    fams = set()
    if not os.path.isfile(path):
        print(f"[ERR] Families file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            fam = parts[0].strip()
            if fam:
                fams.add(fam)
    return fams


# -------- main --------

def main():
    print("=== Phase 81v2: Anchor token mapping (self-contained) ===")

    # load basics
    sections = load_sections_map(SECTIONS_MAP)
    toks = load_tokens(TOK_FILE)
    print(f"[INFO] Loaded {len(toks)} tokens from {TOK_FILE}")

    folio_tokens = rebuild_folio_token_map(TRANS_FILE)
    folio_map = match_tokens_to_folios(toks, folio_tokens)

    patterns = load_rulebook_chargrams(RULEBOOK_JSON)
    if not patterns:
        print("[ERR] No chargram patterns loaded; aborting.", file=sys.stderr)
        sys.exit(1)

    hits = find_pattern_hits(toks, patterns)
    print(f"[INFO] Tokens with ≥1 rule hit: {len(hits)} ({len(hits)/len(toks):.2%})")

    # load families + anchors
    families = load_families(os.path.join(ROOT, "Phase75", "out", "p75_families.tsv"))
    anchors = load_anchor_families(ANCHORS_FILE)

    # Build mapping: for each token, does its hit-set contain any anchor-family pattern?
    # Here we interpret "anchor family" as a set of rule_ids/morphemes embedded in tokens;
    # given our limited structure, we approximate by: if token contains ANY of the
    # family_signature substrings, we tag it.
    anchor_tokens = []
    fam_counts = Counter()
    sec_counts = Counter()

    # Pre-parse family signatures into lists of glyph-fragments (split by '-')
    fam_parts = {fam: [p for p in fam.split("-") if p] for fam in anchors.keys()}

    for idx, (folio, tok) in enumerate(folio_map):
        tok_rules = hits.get(idx, set())
        if not tok_rules:
            continue
        # very simple: check substrings from family signatures
        matched_fams = []
        for fam, parts in fam_parts.items():
            if all(part in tok for part in parts):
                matched_fams.append(fam)
        if not matched_fams:
            continue

        sec = sections.get(folio, "Unknown")
        for fam in matched_fams:
            anchor_tokens.append((idx, folio, sec, tok, fam))
            fam_counts[fam] += 1
            sec_counts[sec] += 1

    # write map
    with open(OUT_MAP, "w", encoding="utf-8") as f:
        f.write("idx\tfolio\tsection\ttoken\tfamily\n")
        for idx, folio, sec, tok, fam in anchor_tokens:
            f.write(f"{idx}\t{folio}\t{sec}\t{tok}\t{fam}\n")

    # stats
    with open(OUT_STATS, "w", encoding="utf-8") as f:
        f.write("Phase 81v2: Anchor token mapping summary\n")
        f.write(f"Total tokens: {len(toks)}\n")
        f.write(f"Tokens with ≥1 rule hit: {len(hits)} ({len(hits)/len(toks):.2%})\n")
        f.write(f"Anchored token assignments: {len(anchor_tokens)}\n")
        f.write("\nBy section (anchor tokens):\n")
        for sec, c in sec_counts.most_common():
            f.write(f"  {sec:12s} {c}\n")
        f.write("\nTop anchor families by hits:\n")
        for fam, c in fam_counts.most_common(20):
            f.write(f"  {fam:40s} {c}\n")

    print(f"[OK] Anchor token map → {OUT_MAP}")
    print(f"[OK] Anchor stats     → {OUT_STATS}")
    print("=== Phase 81v2 complete ===")


if __name__ == "__main__":
    main()
