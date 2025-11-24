#!/usr/bin/env python3
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKRULE = os.path.join(BASE, "Phase74", "out", "p74_token_rules.tsv")
RULECOM = os.path.join(BASE, "Phase75", "out", "p75_rule_communities.tsv")
OUTDIR  = os.path.join(BASE, "Phase76", "out")
os.makedirs(OUTDIR, exist_ok=True)
OUTFILE = os.path.join(OUTDIR, "p76_token_communities.tsv")

# load rule communities
rule2com = {}
with open(RULECOM, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip() or line.startswith("rule_label"):
            continue
        lab, com = line.strip().split("\t")
        rule2com[lab] = com

def norm_rule_id(rid):
    # in p74 we used numeric rule ids; in p72 we used string labels.
    # if your p72 uses label form "chargram:..", adjust here.
    # For now assume p74 uses same labels as p72; if not, we just skip.
    return rid

with open(TOKRULE, "r", encoding="utf-8") as fin, \
     open(OUTFILE, "w", encoding="utf-8") as out:
    out.write("idx\ttoken\tcommunities\n")
    for line in fin:
        if not line.strip() or line.startswith("idx"):
            continue
        idx, tok, rules = line.strip().split("\t")
        comms = set()
        for rid in rules.split(","):
            lab = norm_rule_id(rid)
            if lab in rule2com:
                comms.add(rule2com[lab])
        if comms:
            out.write(f"{idx}\t{tok}\t{','.join(sorted(comms))}\n")

print(f"[OK] Wrote token community profiles → {OUTFILE}")
