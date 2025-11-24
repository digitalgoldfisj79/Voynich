#!/usr/bin/env python3
# p112_bootstrap_attribution.py — attribute families vs Latin/Arabic centroids with bootstrap
# POSIX/Termux-safe, stdlib only.

import json, io, random, math, unicodedata

CENTROIDS = "Phase110/out/p111_centroids.json"
FAMILY_FEATS = "Phase110/out/p110_family_features.tsv"

def to_py(obj):
    if isinstance(obj, dict):
        return {to_py(k): to_py(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_py(x) for x in obj]
    try:
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
    except Exception:
        pass
    return obj

def load_centroids():
    with io.open(CENTROIDS, "r", encoding="utf-8") as f:
        C = json.load(f)
    return C["latin"]["features"], C["arabic"]["features"]

def read_family_vectors(path):
    # expect TSV: family \t feature \t value  (long mode) OR a wide .tsv with header
    # We'll accept your current long-mode from p110 and aggregate.
    import csv, collections
    feats = collections.defaultdict(lambda: {})
    # auto-detect long vs wide
    with io.open(path, "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
    if header[:3] == ["family","feature","value"]:
        with io.open(path, "r", encoding="utf-8") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                feats[row["family"]][row["feature"]] = float(row["value"])
    else:
        # wide
        with io.open(path, "r", encoding="utf-8") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                fam = row["family"]
                for k,v in row.items():
                    if k=="family": continue
                    try: feats[fam][k] = float(v)
                    except: pass
    return feats

def cosine(a, b):
    num = 0.0; da=0.0; db=0.0
    keys = set(a.keys()) | set(b.keys())
    for k in keys:
        av = a.get(k, 0.0); bv = b.get(k, 0.0)
        num += av*bv; da += av*av; db += bv*bv
    if da == 0.0 or db == 0.0: return 0.0
    return num / (da**0.5 * db**0.5)

def main():
    latC, araC = load_centroids()
    fam = read_family_vectors(FAMILY_FEATS)
    rows = []
    for name, vec in fam.items():
        sL = cosine(vec, latC)
        sA = cosine(vec, araC)
        delta = sL - sA
        rows.append((name, sL, sA, delta))

    # write attribution table
    with io.open("Phase110/out/p112_attribution.tsv", "w", encoding="utf-8") as w:
        w.write("family\tsim_latin\tsim_arabic\tdelta\tlabel\n")
        for name, sL, sA, d in sorted(rows, key=lambda x: x[3], reverse=True):
            lab = "Latin-like" if d >= 0 else "Arabic-like"
            w.write(f"{name}\t{round(sL,6)}\t{round(sA,6)}\t{round(d,6)}\t{lab}\n")

    # cheap bootstrap: resample feature keys within each family vector
    # (structure-preserving; gives stability sense without big deps)
    random.seed(1337)
    B = 500
    agree = 0
    for _ in range(B):
        # perturb centroids by resampling features with replacement
        # (keeps mass but introduces variance)
        def resample_centroid(C):
            keys = list(C.keys())
            if not keys: return {}
            out = {}
            for _i in range(len(keys)):
                k = random.choice(keys)
                out[k] = out.get(k, 0.0) + C[k]
            # L1 renormalize
            s = sum(out.values()) or 1.0
            for k in list(out.keys()): out[k] /= s
            return out
        latR = resample_centroid(latC)
        araR = resample_centroid(araC)
        # attribute again and compare sign of delta
        local_agree = 0; total = 0
        for name, vec in fam.items():
            d0 = [r for r in rows if r[0]==name][0][3]
            d1 = cosine(vec, latR) - cosine(vec, araR)
            if (d0>=0 and d1>=0) or (d0<0 and d1<0):
                local_agree += 1
            total += 1
        agree += (local_agree/float(total)) if total else 0.0

    summary = {
        "bootstrap_B": B,
        "mean_sign_agreement": agree/float(B) if B else None,
        "families": len(fam),
    }
    with io.open("Phase110/out/p112_bootstrap_summary.json", "w", encoding="utf-8") as w:
        w.write(json.dumps(to_py(summary), ensure_ascii=False, indent=2))

    print("[OK] Wrote attribution map → Phase110/out/p112_attribution.tsv")
    print("[OK] Wrote bootstrap summary → Phase110/out/p112_bootstrap_summary.json")

if __name__ == "__main__":
    main()
