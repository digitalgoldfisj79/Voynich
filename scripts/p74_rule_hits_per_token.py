#!/usr/bin/env python3
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(BASE, "p6_voynich_tokens.txt")
RULEBOOK = os.path.join(BASE, "Phase69", "out", "p69_rules_final.json")
OUTDIR = os.path.join(BASE, "Phase74", "out")
os.makedirs(OUTDIR, exist_ok=True)
OUTFILE = os.path.join(OUTDIR, "p74_token_rules.tsv")

def load_tokens(path):
    toks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t and not t.startswith("#"):
                toks.append(t)
    return toks

def load_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rules = []
    for idx, r in enumerate(data):
        if not isinstance(r, dict):
            continue
        pat = r.get("pattern") or r.get("regex") or None
        pre = r.get("pre","")
        suf = r.get("suf","")
        if pat:
            try:
                rx = re.compile(pat + r"$")
                rules.append((idx, rx))
            except re.error:
                continue
        elif pre or suf:
            # fallback: simple anchored match
            def mk(pre, suf):
                def f(tok):
                    return tok.startswith(pre) and tok.endswith(suf)
                return f
            rules.append((idx, mk(pre, suf)))
    return rules

tokens = load_tokens(TOKENS)
rules = load_rules(RULEBOOK)

with open(OUTFILE, "w", encoding="utf-8") as out:
    out.write("idx\ttoken\trules\n")
    for i, tok in enumerate(tokens):
        fired = []
        for rid, cond in rules:
            if hasattr(cond, "search"):
                if cond.search(tok):
                    fired.append(str(rid))
            else:
                if cond(tok):
                    fired.append(str(rid))
        if fired:
            out.write(f"{i}\t{tok}\t{','.join(fired)}\n")

print(f"[OK] Wrote token→rules table → {OUTFILE}")
