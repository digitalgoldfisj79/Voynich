import sys
import re

base = "/data/data/com.termux/files/home/Voynich/Voynich_Reproducible_Core"
in_path = base + "/corpora/tacuinum_raw.txt"
out_path = base + "/corpora/latin_tokens_tac.txt"

WORD_RE = re.compile(r"[A-Za-z]+")

def main():
    n_raw = 0
    n_tok = 0
    with open(in_path, "r", encoding="utf-8", errors="ignore") as f_in, \
         open(out_path, "w", encoding="utf-8") as f_out:
        for line in f_in:
            n_raw += 1
            for m in WORD_RE.finditer(line.lower()):
                tok = m.group(0)
                f_out.write(tok + "\n")
                n_tok += 1

    sys.stderr.write(f"[TOK] Read {n_raw} raw lines, wrote {n_tok} tokens → {out_path}\n")

if __name__ == "__main__":
    main()
