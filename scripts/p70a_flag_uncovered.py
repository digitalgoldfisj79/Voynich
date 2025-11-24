#!/usr/bin/env python3
# POSIX-safe, stdlib-only
import json, re, os

RULEFILE = "Phase69/out/p69_rules_final.json"
TOKENS   = "p6_voynich_tokens.txt"
OUTFILE  = "Phase70/out/p70a_token_flags.tsv"

os.makedirs("Phase70/out", exist_ok=True)

# --- Load rules robustly ---
raw = json.load(open(RULEFILE))
rules = []
for r in raw:
    if isinstance(r, dict):
        rules.append(r)
    elif isinstance(r, str):
        # Try to split tab/colon string formats like "pre=qok\tsuf=dy"
        parts = {}
        for bit in re.split(r"[\t,;]", r):
            if "=" in bit:
                k,v = bit.split("=",1)
                parts[k.strip()] = v.strip()
        if parts:
            rules.append(parts)

print(f"[INFO] Loaded {len(rules)} rules from {RULEFILE}")

# --- Build regex patterns ---
patterns = []
for r in rules:
    pre, suf = r.get("pre",""), r.get("suf","")
    if pre or suf:
        regex = "^" + re.escape(pre) + ".*" + re.escape(suf) + "$"
        patterns.append(re.compile(regex))

print(f"[INFO] Compiled {len(patterns)} prefix/suffix regex patterns")

# --- Process tokens ---
covered = uncovered = 0
with open(OUTFILE, "w") as out:
    for line in open(TOKENS):
        tok = line.strip()
        if not tok:
            continue
        if any(p.match(tok) for p in patterns):
            covered += 1
            flag = "C"
        else:
            uncovered += 1
            flag = "U"
        out.write(f"{tok}\t{flag}\n")

total = covered + uncovered
print(f"[RESULT] Covered={covered}, Uncovered={uncovered}, Coverage={covered/total:.3f}")
print(f"[OK] Wrote {OUTFILE}")
