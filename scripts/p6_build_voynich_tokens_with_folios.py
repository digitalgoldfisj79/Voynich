#!/usr/bin/env python3
import os, re

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
SRC  = os.path.join(BASE, "corpora/voynich_transliteration.txt")
OUT  = os.path.join(BASE, "p6_voynich_tokens.txt")

tokens = []
with open(SRC) as f:
    for line in f:
        # only lines that actually contain folio + tokens
        if not re.match(r"^<f\d+[rv]\.", line):
            continue
        m = re.match(r"^<f(\d+[rv])\.(\d+)[^>]*>\s+(.*)$", line.strip())
        if not m:
            continue
        folio, lineno, seq = m.groups()
        for tok in seq.split("."):
            tok = tok.strip()
            if not tok or tok.startswith("<") or tok.endswith(">"):
                continue
            tokens.append(f"<f{folio}.{lineno}> {tok}")

with open(OUT, "w") as out:
    out.write("\n".join(tokens))

print(f"[OK] Wrote {len(tokens)} tokens with folio markers → {OUT}")
