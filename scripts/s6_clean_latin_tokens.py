#!/usr/bin/env python3
import sys
import re

if len(sys.argv) != 3:
    print("Usage: s6_clean_latin_tokens.py <in_tokens.txt> <out_clean_tokens.txt>", file=sys.stderr)
    sys.exit(1)

in_path, out_path = sys.argv[1], sys.argv[2]

# Small set of common Latin function words we always allow
LATIN_FUNCTION = {
    "et", "est", "in", "ad", "de", "cum", "per", "ut", "si", "non",
    "sed", "nec", "aut", "vel", "quo", "quod", "qui", "quam", "hic",
    "haec", "hoc", "ille", "illa", "illud", "idem", "idemque", "ne",
    "nam", "enim", "ideo", "ergo", "ita", "quidem"
}

# Typical Latin endings (very incomplete but conservative)
LATIN_SUFFIXES = (
    "us", "um", "is", "ae", "am", "as", "os", "es", "em",
    "ibus", "orum", "arum",
    "nt", "tur", "tis", "mus", "mur", "ntur",
    "re", "ri", "isse", "erit", "erunt",
    "tas", "tate", "tatem", "tion", "tionem",
    "ior", "iores", "ioris", "ius",
    "alis", "alis", "arum",
    "itas", "itatem", "itate",
)

word_re = re.compile(r"^[a-z]+$")

def is_probably_latin(tok: str) -> bool:
    # pure letters, length 2–20
    if not word_re.match(tok):
        return False
    if len(tok) < 2 or len(tok) > 20:
        return False
    # rule out obvious non-Latin letters (k, w) in most cases
    if any(c in tok for c in "kw"):
        if tok not in LATIN_FUNCTION:
            return False
    # must contain at least one vowel
    if not any(v in tok for v in "aeiou"):
        return False
    # either a known Latin function word or has a Latin-like ending
    if tok in LATIN_FUNCTION:
        return True
    if any(tok.endswith(suf) for suf in LATIN_SUFFIXES):
        return True
    return False

kept = 0
skipped = 0

with open(in_path, "r", encoding="utf-8") as fin, \
     open(out_path, "w", encoding="utf-8") as fout:
    for line in fin:
        tok = line.strip().lower()
        if not tok:
            continue
        if is_probably_latin(tok):
            fout.write(tok + "\n")
            kept += 1
        else:
            skipped += 1

print(f"[CLEAN] Input:  {in_path}")
print(f"[CLEAN] Output: {out_path}")
print(f"[CLEAN] Kept:   {kept}")
print(f"[CLEAN] Skipped:{skipped}")
