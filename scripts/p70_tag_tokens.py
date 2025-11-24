#!/usr/bin/env python3
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_PATH = os.path.join(BASE, "p6_voynich_tokens.txt")
RULEBOOK_PATH = os.path.join(BASE, "Phase69", "out", "p69_rules_final.json")
OUT_PATH = os.path.join(BASE, "Phase70", "out", "p70_token_hits.tsv")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

def load_tokens(path):
    return [ln.strip() for ln in open(path) if ln.strip()]

def load_rules(path):
    data = json.load(open(path))
    if isinstance(data, dict) and "rules" in data: data = data["rules"]
    return [r for r in data if r.get("kind")=="chargram" and r.get("pattern")]

def match(tok, rule):
    p, side = rule["pattern"], rule.get("side","any")
    return tok.startswith(p) if side=="left" else tok.endswith(p) if side=="right" else p in tok

tokens, rules = load_tokens(TOKENS_PATH), load_rules(RULEBOOK_PATH)
out = open(OUT_PATH, "w")
out.write("token\trules\n")
for t in tokens:
    hits = [r["pattern"] for r in rules if match(t, r)]
    if hits:
        out.write(f"{t}\t{','.join(hits)}\n")
out.close()
print(f"[OK] Wrote {OUT_PATH}")
