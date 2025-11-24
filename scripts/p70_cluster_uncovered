#!/usr/bin/env python3
import collections, csv
INFILE  = "Phase70/out/p70a_token_flags.tsv"
OUTFILE = "Phase70/out/p70b_clusters.tsv"

pref, suff, length = collections.Counter(), collections.Counter(), collections.Counter()
for tok, flag in (line.strip().split("\t") for line in open(INFILE)):
    if flag != "U": continue
    pref[tok[:2]] += 1
    suff[tok[-2:]] += 1
    length[len(tok)] += 1

with open(OUTFILE, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["prefix", "count"])
    for k,v in pref.most_common(30): w.writerow([k,v])
    w.writerow([])
    w.writerow(["suffix", "count"])
    for k,v in suff.most_common(30): w.writerow([k,v])
    w.writerow([])
    w.writerow(["length", "count"])
    for k,v in sorted(length.items()): w.writerow([k,v])

print("[OK] Wrote cluster stats →", OUTFILE)
