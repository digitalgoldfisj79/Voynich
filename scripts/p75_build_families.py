#!/usr/bin/env python3
import json, os, re
from collections import defaultdict

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
TOKENS = os.path.join(BASE, "p6_voynich_tokens.txt")
RULEBOOK = os.path.join(BASE, "Phase69/out/p69_rules_final.json")
OUTFILE = os.path.join(BASE, "Phase75/out/p75_families.tsv")

os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)

# --- Load tokens
tokens = []
with open(TOKENS) as f:
    for line in f:
        w = line.strip()
        if w and not w.startswith("#"):
            tokens.append(w)

# --- Load and filter rules
# --- Load and filter rules
with open(RULEBOOK) as f:
    raw = json.load(f)

# Handle both {"rules": [...]} and [...] formats
if isinstance(raw, dict) and "rules" in raw:
    raw = raw["rules"]

rules = []
for r in raw:
    if isinstance(r, dict):
        pat = r.get("pattern") or r.get("pre") or ""
        if pat and len(pat) >= 1:   # keep single-char too for completeness
            rules.append(pat)

rules = sorted(set(rules))
print(f"[INFO] Loaded {len(rules)} concrete patterns from rulebook.")
# --- Detect which rules each token matches
fam_counts = defaultdict(int)
fam_examples = defaultdict(list)

for w in tokens:
    matched = sorted([r for r in rules if r in w])
    if not matched: 
        continue
    key = "-".join(matched)
    fam_counts[key] += 1
    if len(fam_examples[key]) < 5:
        fam_examples[key].append(w)

# --- Filter to families with ≥10 tokens
filtered = [(k,v) for k,v in fam_counts.items() if v >= 10]
filtered.sort(key=lambda x: x[1], reverse=True)

# --- Write output
with open(OUTFILE, "w") as out:
    out.write("family_signature\tcount\texamples\n")
    for k,v in filtered:
        ex = ", ".join(fam_examples[k])
        out.write(f"{k}\t{v}\t{ex}\n")

print(f"[OK] Wrote {len(filtered)} families → {OUTFILE}")
