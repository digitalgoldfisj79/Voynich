#!/usr/bin/env python3
import re
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TRANS = BASE / "corpora" / "voynich_transliteration.txt"
TOKFILE = BASE / "p6_voynich_tokens.txt"
HITS = BASE / "Phase70" / "out" / "p70_token_hits.tsv"
ANCH = BASE / "Phase77" / "out" / "p77_anchor_families.tsv"
OUT_DIR = BASE / "Phase81" / "out"
OUT_MAP = OUT_DIR / "p81_anchor_token_map.tsv"
OUT_STATS = OUT_DIR / "p81_anchor_stats.txt"

OUT_DIR.mkdir(parents=True, exist_ok=True)

folio_tag = re.compile(r"<\s*(f\d{1,3}[rv])(?:\.[^>]*)?\s*>", re.I)

def clean_line_phase6_style(line: str) -> str:
    # identical semantics to p6_build_voynich_tokens.py
    if ">" in line:
        line = line.split(">")[-1]
    line = re.sub(r"<[^>]*>", " ", line)
    return line

def load_canonical_tokens():
    tokens = []
    with TOKFILE.open(encoding="utf-8") as f:
        for t in f:
            t = t.strip()
            if t:
                tokens.append(t)
    return tokens

def rebuild_tokens_with_folios():
    tokens = []
    folios = []
    cur_fol = "Unknown"

    with TRANS.open(encoding="utf-8") as f:
        for raw in f:
            raw = raw.rstrip("\n")
            if not raw or raw.lstrip().startswith("#"):
                continue

            # update current folio if any <f..> tag present
            m = folio_tag.search(raw)
            if m:
                cur_fol = m.group(1).lower()

            line = clean_line_phase6_style(raw.strip())
            if not line:
                continue

            parts = re.split(r"[.\s]+", line)
            for part in parts:
                t = re.sub(r"[^A-Za-z]", "", part)
                if t:
                    tokens.append(t)
                    folios.append(cur_fol)

    return tokens, folios

def load_hits():
    hits = {}
    if not HITS.is_file():
        return hits
    with HITS.open(encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            idx = int(row.get("idx", "-1"))
            fam = row.get("family") or row.get("label") or ""
            if idx >= 0 and fam:
                hits.setdefault(idx, set()).add(fam)
    return hits

def load_anchor_families():
    anchors = set()
    if not ANCH.is_file():
        return anchors
    with ANCH.open(encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            fam = (row.get("family") or "").strip()
            if fam:
                anchors.add(fam)
    return anchors

def main():
    print("=== Phase 81: Anchor token mapping (canonical) ===")
    if not TRANS.is_file():
        raise SystemExit(f"[ERR] Missing transliteration: {TRANS}")
    if not TOKFILE.is_file():
        raise SystemExit(f"[ERR] Missing canonical tokens: {TOKFILE}")

    canon = load_canonical_tokens()
    print(f"[INFO] Loaded {len(canon):,} canonical tokens from {TOKFILE}")

    rebuilt, folios = rebuild_tokens_with_folios()
    print(f"[INFO] Rebuilt {len(rebuilt):,} tokens from transliteration with folio labels")

    if len(rebuilt) != len(canon):
        print(f"[ERR] Token count mismatch: canon={len(canon)} vs rebuilt={len(rebuilt)}")
        # Hard fail: if this happens, nothing downstream is trustworthy
        raise SystemExit(1)

    mismatches = sum(1 for a, b in zip(canon, rebuilt) if a != b)
    if mismatches:
        print(f"[ERR] {mismatches} token mismatches between canonical and rebuilt sequences.")
        # Also hard fail; this means divergence from Phase 6 logic
        raise SystemExit(1)

    print("[INFO] Canonical token stream matches transliteration reconstruction 1:1")

    hits = load_hits()
    anchors = load_anchor_families()
    print(f"[INFO] Loaded pattern hits for {len(hits)} token positions")
    print(f"[INFO] Loaded {len(anchors)} anchor families")

    # Build map
    rows = []
    anchor_token_counts = {}
    for idx, (tok, fol) in enumerate(zip(canon, folios)):
        fams = hits.get(idx, set())
        anchor_fams = sorted(fams & anchors)
        if not anchor_fams:
            continue
        for fam in anchor_fams:
            rows.append({
                "idx": idx,
                "folio": fol,
                "token": tok,
                "family": fam,
            })
            anchor_token_counts[fam] = anchor_token_counts.get(fam, 0) + 1

    with OUT_MAP.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx", "folio", "token", "family"], delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with OUT_STATS.open("w", encoding="utf-8") as f:
        f.write("Phase 81: Anchor token stats\n")
        f.write(f"Total tokens: {len(canon)}\n")
        f.write(f"Anchor-mapped tokens: {len(rows)}\n")
        if rows:
            frac = len(rows) / len(canon)
            f.write(f"Fraction of corpus with ≥1 anchor family: {frac:.4f}\n")
        f.write("\nPer-family token counts:\n")
        for fam, c in sorted(anchor_token_counts.items(), key=lambda x: -x[1]):
            f.write(f"{fam}\t{c}\n")

    print(f"[OK] Anchor token map → {OUT_MAP}")
    print(f"[OK] Anchor stats     → {OUT_STATS}")
    print("=== Phase 81 complete ===")

if __name__ == "__main__":
    main()
