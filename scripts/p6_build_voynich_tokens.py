#!/usr/bin/env python3
import re, os
from p6_config import VOYNICH_TRANS, VOYNICH_TOKENS

def clean_line(line):
    if ">" in line:
        line = line.split(">")[-1]
    line = re.sub(r"<[^>]*>", " ", line)
    return line

def main():
    if not os.path.isfile(VOYNICH_TRANS):
        raise SystemExit(f"[ERR] Missing transliteration: {VOYNICH_TRANS}")

    tokens = []
    with open(VOYNICH_TRANS, encoding="utf-8") as f:
        for raw in f:
            line = clean_line(raw.strip())
            if not line or line.startswith("#"): continue
            for part in re.split(r"[.\s]+", line):
                t = re.sub(r"[^A-Za-z]", "", part)
                if t:
                    tokens.append(t)

    with open(VOYNICH_TOKENS, "w", encoding="utf-8") as out:
        out.write("\n".join(tokens))
    print(f"[ok] Wrote {len(tokens):,} tokens to {VOYNICH_TOKENS}")

if __name__ == "__main__":
    main()
