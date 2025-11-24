#!/data/data/com.termux/files/usr/bin/python3
import os
import re

BASE = os.environ.get("BASE", os.path.join(os.environ["HOME"], "Voynich", "Voynich_Reproducible_Core"))

in_path = os.path.join(BASE, "corpora", "voynich_transliteration.txt")
out_dir = os.path.join(BASE, "PhaseS", "out")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "s49_folio_hands.tsv")

folio_meta_re = re.compile(r'^<(?P<folio>f[^>]+)>\s*<!\s*(?P<meta>[^>]*)>')

def parse_meta(meta: str):
    currier = None
    hand = None
    # meta looks like: $Q=A $P=A $F=a $B=1 $I=T $L=A $H=1 $C=1 $X=V
    for part in meta.split():
        if part.startswith("$Q="):
            currier = part[3:]
        elif part.startswith("$H="):
            hand = part[3:]
    return currier, hand

def main():
    if not os.path.exists(in_path):
        raise SystemExit(f"[S49] ERROR: transliteration file not found at {in_path}")

    with open(in_path, "r", encoding="utf-8") as f_in, \
         open(out_path, "w", encoding="utf-8") as f_out:
        f_out.write("folio\thand\tcurrier\n")
        for line in f_in:
            m = folio_meta_re.match(line)
            if not m:
                continue
            folio = m.group("folio")
            meta = m.group("meta")
            currier, hand = parse_meta(meta)
            if hand is None:
                # skip folios without hand assignment
                continue
            if currier is None:
                currier = ""
            f_out.write(f"{folio}\t{hand}\t{currier}\n")

    print(f"[S49] Wrote folio→hand map to: {out_path}")

if __name__ == "__main__":
    main()
