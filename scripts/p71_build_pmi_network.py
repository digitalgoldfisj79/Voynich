#!/usr/bin/env python3
import os
import json
import math
from collections import defaultdict

# -------------
# Config
# -------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK_PATHS = [
    os.path.join(ROOT, "corpora", "p6_voynich_tokens.txt"),
    os.path.join(ROOT, "p6_voynich_tokens.txt"),
]
RULEBOOK_JSON = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
OUT_DIR = os.path.join(ROOT, "Phase72", "out")
OUT_PATH = os.path.join(OUT_DIR, "p72_rule_pmi_network.tsv")

MIN_COOCC = 5
MIN_PMI = 0.5

# -------------
# Shared helpers (same semantics as p71)
# -------------

def load_tokens():
    for p in TOK_PATHS:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                toks = [ln.strip() for ln in f if ln.strip()]
            print(f"[INFO] Loaded {len(toks)} tokens from {p}")
            return toks
    raise SystemExit("[ERR] No canonical token file found.")

def load_rulebook():
    if not os.path.isfile(RULEBOOK_JSON):
        raise SystemExit(f"[ERR] Rulebook not found: {RULEBOOK_JSON}")
    with open(RULEBOOK_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        raise SystemExit("[ERR] Unexpected rulebook JSON format.")
    print(f"[INFO] Loaded {len(rules)} rules from {RULEBOOK_JSON}")
    return rules

def rule_label(r):
    rid = r.get("rule_id", "")
    kind = r.get("kind", "")
    pre = r.get("pre", "") or ""
    suf = r.get("suf", "") or ""
    pat = r.get("pattern", "") or ""
    base = r.get("base_weight", "")
    core = pat or (pre + "*" + suf if (pre or suf) else "")
    return rid or f"{kind}:{core}:{base}"

def match_rule_on_token(r, tok):
    kind = r.get("kind", "")
    pre = r.get("pre", "") or ""
    suf = r.get("suf", "") or ""
    pat = r.get("pattern", "") or ""

    if kind == "prefix" and pre:
        return tok.startswith(pre)
    if kind == "suffix" and suf:
        return tok.endswith(suf)
    if kind == "pair":
        if pre and suf:
            return tok.startswith(pre) and tok.endswith(suf)
        elif pre:
            return tok.startswith(pre)
        elif suf:
            return tok.endswith(suf)
        return False
    if kind == "chargram" and pat:
        return pat in tok

    return False

# -------------
# Main
# -------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tokens = load_tokens()
    rules = load_rulebook()

    # Build rule index and initialize
    labels = []
    rule_defs = []
    for r in rules:
        lbl = rule_label(r)
        labels.append(lbl)
        rule_defs.append(r)

    freq = defaultdict(int)
    cofreq = defaultdict(int)

    N = len(tokens)

    # For each token, find which rules fire; update counts + cooc
    for tok in tokens:
        active = []
        for lbl, r in zip(labels, rule_defs):
            if match_rule_on_token(r, tok):
                active.append(lbl)
        # Update frequencies
        for lbl in active:
            freq[lbl] += 1
        # Update cooccurrence
        if len(active) > 1:
            # unique pairs
            uniq = sorted(set(active))
            for i in range(len(uniq)):
                for j in range(i+1, len(uniq)):
                    cofreq[(uniq[i], uniq[j])] += 1

    used_labels = {lbl for lbl, c in freq.items() if c > 0}
    print(f"[INFO] {len(used_labels)} rules fired at least once.")

    # Compute PMI edges
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        out.write("#rule_i\trule_j\tfreq_i\tfreq_j\tcooc\tPMI_bits\n")
        kept = 0
        for (ri, rj), c in sorted(cofreq.items(), key=lambda x: -x[1]):
            if c < MIN_COOCC:
                continue
            fi = freq[ri]
            fj = freq[rj]
            if fi == 0 or fj == 0:
                continue
            pmi = math.log2((c * N) / (fi * fj))
            if pmi >= MIN_PMI:
                out.write(f"{ri}\t{rj}\t{fi}\t{fj}\t{c}\t{pmi:.4f}\n")
                kept += 1

    print(f"[OK] Wrote {kept} PMI edges → {OUT_PATH}")
    print(f"[INFO] Thresholds: MIN_COOCC={MIN_COOCC}, MIN_PMI={MIN_PMI}")

if __name__ == "__main__":
    main()
