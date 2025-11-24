#!/usr/bin/env python3
import sys
import re

if len(sys.argv) != 3:
    print("Usage: s6_tokenize_latin_raw.py <in_raw.txt> <out_tokens.txt>", file=sys.stderr)
    sys.exit(1)

in_path, out_path = sys.argv[1], sys.argv[2]

token_re = re.compile(r"[a-zA-Z]+")

kept = 0

with open(in_path, "r", encoding="utf-8", errors="ignore") as fin, \
     open(out_path, "w", encoding="utf-8") as fout:
    for line in fin:
        for m in token_re.finditer(line):
            tok = m.group(0).lower()
            if not tok:
                continue
            fout.write(tok + "\n")
            kept += 1

print(f"[TOKENIZE] Input:  {in_path}")
print(f"[TOKENIZE] Output: {out_path}")
print(f"[TOKENIZE] Tokens written: {kept}")
