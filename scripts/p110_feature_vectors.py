#!/usr/bin/env python3
# p110_feature_vectors.py — build family feature vectors aligned with p111 (len_*, suf1_*, suf2_*)
# POSIX/Termux-safe, stdlib only.

import io, csv, collections, sys

FAMILIES_LONG = "Phase75/out/p75_families_long.tsv"   # expected cols: family,token (plus anything else ignored)
CORPUS_TOKENS = "p6_voynich_tokens.txt"               # one token per line OR whitespace-separated; we'll split on whitespace per line
OUT_LONG       = "Phase110/out/p110_family_features.tsv"

def load_family_members(path):
    members = collections.defaultdict(set)
    with io.open(path, "r", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
    # find best-effort columns
    fam_ix = None; tok_ix = None
    for i,h in enumerate(hdr):
        hL = h.strip().lower()
        if hL == "family": fam_ix = i
        if hL == "token":  tok_ix = i
    if fam_ix is None or tok_ix is None:
        # fall back to a DictReader if header names differ
        with io.open(path, "r", encoding="utf-8") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                members[row["family"]].add(row["token"])
        return members

    with io.open(path, "r", encoding="utf-8") as f:
        # re-read from top using indices
        f.seek(0)
        for i, line in enumerate(f):
            if i == 0: continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= max(fam_ix, tok_ix): continue
            fam = parts[fam_ix].strip()
            tok = parts[tok_ix].strip()
            if fam and tok:
                members[fam].add(tok)
    return members

def iter_corpus_tokens(path):
    with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # allow either one-token-per-line or space-separated
            for t in line.strip().split():
                if t:
                    yield t

def cap_len(L):
    return 13 if L >= 13 else L

def build_vectors(members, corpus_iter):
    # reverse index token -> families (a token may belong to multiple families)
    tok2fams = collections.defaultdict(list)
    for fam, toks in members.items():
        for t in toks:
            tok2fams[t].append(fam)

    # counters per family
    feat = collections.defaultdict(lambda: collections.Counter())
    counts = collections.Counter()

    # pass over corpus and accumulate features into each token’s family(ies)
    for t in corpus_iter:
        fams = tok2fams.get(t)
        if not fams:
            continue
        L = len(t)
        lkey = f"len_{cap_len(L)}"
        s1   = f"suf1_{t[-1]}" if L >= 1 else None
        s2   = f"suf2_{t[-2:]}" if L >= 2 else None
        for fam in fams:
            feat[fam][lkey] += 1
            if s1: feat[fam][s1] += 1
            if s2: feat[fam][s2] += 1
            counts[fam] += 1

    # L1-normalise
    for fam, ctr in feat.items():
        total = float(counts[fam]) or 1.0
        for k in list(ctr.keys()):
            ctr[k] = ctr[k] / total

    return feat, counts

def write_long(out_path, feat, counts):
    # long format: family,feature,value plus a meta row for n_obs
    with io.open(out_path, "w", encoding="utf-8") as w:
        w.write("family\tfeature\tvalue\n")
        for fam in sorted(feat.keys()):
            # write observed count as a meta feature (can be inspected downstream if you want to filter)
            w.write(f"{fam}\tn_obs\t{counts[fam]}\n")
            for k,v in sorted(feat[fam].items()):
                # keep reasonable precision
                w.write(f"{fam}\t{k}\t{('{:.9f}'.format(v)).rstrip('0').rstrip('.')}\n")

def main():
    members = load_family_members(FAMILIES_LONG)
    feat, counts = build_vectors(members, iter_corpus_tokens(CORPUS_TOKENS))
    # ensure output dir exists
    import os
    os.makedirs("Phase110/out", exist_ok=True)
    write_long(OUT_LONG, feat, counts)
    # console report
    fam_with_obs = sum(1 for f in counts if counts[f] > 0)
    sys.stdout.write("=== p110: family feature vectors (len/suf1/suf2) ===\n")
    sys.stdout.write(f"[INFO] Families (any members): {len(members)}\n")
    sys.stdout.write(f"[INFO] Families with corpus observations: {fam_with_obs}\n")
    sys.stdout.write(f"[OK] Wrote long-format vectors → {OUT_LONG}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
