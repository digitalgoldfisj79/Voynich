#!/usr/bin/env python3
# p111_cross_corpus_vectors.py — build Latin/Arabic centroids (Unicode-safe, diacritics stripped)
# POSIX/Termux-safe, stdlib only.

import json, unicodedata, io, sys, collections

LATIN_PATH  = "corpora/latin_dante_monarchia.txt"
ARABIC_PATH = "corpora/guide_judeoarabic_ar.txt"   # supports Arabic script OR Judeo-Arabic (Hebrew letters)

def strip_diacritics(s: str) -> str:
    # remove Arabic harakat + Hebrew niqqud + general combining marks
    out = []
    for ch in unicodedata.normalize("NFKD", s):
        cat = unicodedata.category(ch)
        cp  = ord(ch)
        # Combining marks (Mn), Arabic diacritics, Hebrew niqqud ranges handled by Mn removal
        if cat == "Mn":
            continue
        out.append(ch)
    return "".join(out)

def tokenize_any(text: str):
    # keep letters from ANY alphabet; split on non-letters
    toks, buf = [], []
    for ch in text:
        if ch.isalpha():
            buf.append(ch)
        else:
            if buf:
                toks.append("".join(buf).casefold())
                buf = []
    if buf:
        toks.append("".join(buf).casefold())
    return toks

def read_tokens(path):
    with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    txt = strip_diacritics(txt)
    return tokenize_any(txt)

def basic_features(tokens):
    # very simple centroid features: length histogram (1–12, 13+), suffix last-1/2 chars freq, vowel-ish ratio per script
    feat = collections.Counter()
    for t in tokens:
        L = len(t)
        feat[f"len_{min(L,13)}"] += 1
        if L >= 1: feat[f"suf1_{t[-1]}"] += 1
        if L >= 2: feat[f"suf2_{t[-2:]}"] += 1
    n = float(len(tokens)) or 1.0
    # L1 normalize
    for k in list(feat.keys()):
        feat[k] = feat[k] / n
    return dict(feat), len(tokens)

def to_py(obj):
    # cast numpy/pandas dtypes if any accidentally sneak in
    if isinstance(obj, dict):
        return {to_py(k): to_py(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_py(x) for x in obj]
    try:
        import numpy as np  # may not exist; keep defensive
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
    except Exception:
        pass
    return obj

def main():
    latin  = read_tokens(LATIN_PATH)
    arabic = read_tokens(ARABIC_PATH)

    lat_feat, lat_n = basic_features(latin)
    ara_feat, ara_n = basic_features(arabic)

    out = {
        "latin":  {"n_tokens": lat_n, "features": lat_feat},
        "arabic": {"n_tokens": ara_n, "features": ara_feat},
    }
    with io.open("Phase110/out/p111_centroids.json", "w", encoding="utf-8") as w:
        w.write(json.dumps(to_py(out), ensure_ascii=False, indent=2))

    # tiny console report
    sys.stdout.write(f"[INFO] Latin tokens:  {lat_n}\n")
    sys.stdout.write(f"[INFO] Arabic tokens: {ara_n}\n")
    sys.stdout.write("[OK] Wrote centroids → Phase110/out/p111_centroids.json\n")

if __name__ == "__main__":
    main()
