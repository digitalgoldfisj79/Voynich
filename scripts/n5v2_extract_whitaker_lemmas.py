#!/usr/bin/env python3
"""
Extract lemmas from Whitaker's Words (Latin morphology engine)
Works directly on WORDS/*.LAT lexical files.
"""

from pathlib import Path
import re

BASE = Path.home()/"Voynich"/"Voynich_Reproducible_Core"
W = BASE/"corpora/latin_raw/whitaker"/"WORDS"
OUT = BASE/"corpora/latin_vocab/whitaker_lemmas.tsv"

if not W.exists():
    raise SystemExit(f"[ERROR] Whitaker directory not found: {W}")

lemmas = []

# Pattern for Whitaker lexical lines:
# e.g. "AMO    V    1    to love"
pat = re.compile(r"^([A-Z]+)\s+([A-Z]{1,4})\s+\d+\s+(.*)$")

for fp in W.glob("*.LAT"):
    try:
        txt = fp.read_text(errors="ignore")
    except:
        continue

    for line in txt.splitlines():
        m = pat.match(line.strip())
        if m:
            lemma = m.group(1).lower()
            pos = m.group(2)
            gloss = m.group(3).strip()
            lemmas.append((lemma, pos, gloss, fp.name))

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w") as f:
    f.write("lemma\tpos\tgloss\tsource\n")
    for lemma, pos, gloss, src in sorted(lemmas):
        f.write(f"{lemma}\t{pos}\t{gloss}\t{src}\n")

print(f"[n5v2] Extracted {len(lemmas)} lemmas into {OUT}")
