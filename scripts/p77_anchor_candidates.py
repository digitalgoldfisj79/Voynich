#!/usr/bin/env python3
import os
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFILE = os.path.join(BASE, "Phase76", "out", "p76_token_communities.tsv")
OUTDIR = os.path.join(BASE, "Phase77", "out")
os.makedirs(OUTDIR, exist_ok=True)
OUTFILE = os.path.join(OUTDIR, "p77_anchor_candidates.tsv")

com2tok = defaultdict(list)

with open(INFILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip() or line.startswith("idx"):
            continue
        idx, tok, comms = line.strip().split("\t")
        for c in comms.split(","):
            com2tok[c].append(tok)

with open(OUTFILE, "w", encoding="utf-8") as out:
    out.write("community\ttoken\tcount\n")
    for com in sorted(com2tok.keys()):
        cnts = Counter(com2tok[com])
        for tok, c in cnts.most_common(50):
            if c < 3:
                continue
            out.write(f"{com}\t{tok}\t{c}\n")

print(f"[OK] Wrote candidate anchors → {OUTFILE}")
