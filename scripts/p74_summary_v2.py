#!/usr/bin/env python3
import os
import csv
from collections import Counter, defaultdict
from statistics import mean, pstdev

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))

TOKENS_TXT = os.path.join(BASE, "p6_voynich_tokens.txt")
TOKENS_CORP = os.path.join(BASE, "corpora", "p6_voynich_tokens.txt")

HITS_TSV = os.path.join(BASE, "Phase70", "out", "p70_token_hits.tsv")
FAMS_TSV = os.path.join(BASE, "Phase71", "out", "p71_token_families.tsv")
PMI_TSV  = os.path.join(BASE, "Phase73", "out", "p73_rule_pmi.tsv")

OUTDIR   = os.path.join(BASE, "Phase74", "out")
OUTFILE  = os.path.join(OUTDIR, "p74_summary.txt")

os.makedirs(OUTDIR, exist_ok=True)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def load_tokens():
    path = TOKENS_TXT if os.path.isfile(TOKENS_TXT) else TOKENS_CORP
    if not os.path.isfile(path):
        print(f"[WARN] No token file found at {TOKENS_TXT} or {TOKENS_CORP}")
        return [], path
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                tokens.append(t)
    return tokens, path

def read_tsv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows

# ---------------------------------------------------------
# 1. Tokens
# ---------------------------------------------------------
tokens, tok_path = load_tokens()
n_tokens = len(tokens)
n_types = len(set(tokens))

# ---------------------------------------------------------
# 2. Phase 69 chargram hits (Phase70)
# ---------------------------------------------------------
hits_info = {}
covered_token_count = 0
covered_type_set = set()
rule_counter = Counter()

if os.path.isfile(HITS_TSV):
    rows = read_tsv(HITS_TSV)
    for row in rows:
        token = row.get("token", "").strip()
        hits = row.get("hits", "").strip()
        rules = row.get("rules", "").strip()
        try:
            n_hits = int(hits) if hits != "" else 0
        except ValueError:
            n_hits = 0

        has_hit = n_hits > 0 or (rules not in ("", "[]"))
        if token:
            if has_hit:
                covered_token_count += 1
                covered_type_set.add(token)
            # optional: count rule usage if "rules" is a delimited list
            if rules and rules not in ("[]",):
                # assume comma-separated or space-separated labels
                for r in rules.replace("[","").replace("]","").replace("'", "").split(","):
                    r = r.strip()
                    if r:
                        rule_counter[r] += 1

    n_hits_rows = len(rows)
else:
    n_hits_rows = 0
    print(f"[WARN] Missing Phase70 hits file: {HITS_TSV}")

# ---------------------------------------------------------
# 3. Token families (Phase71)
# ---------------------------------------------------------
family_counts = Counter()
family_example = {}
family_rows = 0

if os.path.isfile(FAMS_TSV):
    rows = read_tsv(FAMS_TSV)
    family_rows = len(rows)
    for row in rows:
        fam = row.get("family_key") or row.get("family") or ""
        tok = row.get("token") or row.get("example") or ""
        fam = fam.strip()
        tok = tok.strip()
        if fam:
            family_counts[fam] += 1
            if fam not in family_example and tok:
                family_example[fam] = tok
else:
    print(f"[WARN] Missing Phase71 families file: {FAMS_TSV}")

n_families = len(family_counts)
nontrivial_fams = sum(1 for c in family_counts.values() if c > 1)

# ---------------------------------------------------------
# 4. PMI network (Phase73)
# ---------------------------------------------------------
pmi_edges = []
pmi_vals = []

if os.path.isfile(PMI_TSV):
    with open(PMI_TSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                pmi = float(row.get("PMI_bits", ""))
            except ValueError:
                continue
            rule_i = (row.get("rule_i") or "").strip()
            rule_j = (row.get("rule_j") or "").strip()
            if rule_i and rule_j:
                pmi_edges.append((rule_i, rule_j, pmi))
                pmi_vals.append(pmi)
else:
    print(f"[WARN] Missing Phase73 PMI file: {PMI_TSV}")

n_edges = len(pmi_edges)
if pmi_vals:
    mean_pmi = mean(pmi_vals)
    med_pmi = sorted(pmi_vals)[len(pmi_vals)//2]
    max_pmi = max(pmi_vals)
    sd_pmi = pstdev(pmi_vals) if len(pmi_vals) > 1 else 0.0
else:
    mean_pmi = med_pmi = max_pmi = sd_pmi = 0.0

# crude node count:
nodes = set()
for a,b,_ in pmi_edges:
    nodes.add(a); nodes.add(b)
n_nodes = len(nodes)

# ---------------------------------------------------------
# 5. Write summary
# ---------------------------------------------------------
lines = []

lines.append("=== Phase 74: Structural Summary ===")
lines.append("")
lines.append(f"[TOKENS] Source file: {tok_path}")
lines.append(f"[TOKENS] Total tokens: {n_tokens}")
lines.append(f"[TOKENS] Total types:  {n_types}")
lines.append("")

if n_hits_rows > 0:
    cov_types = len(covered_type_set)
    cov_tokens = covered_token_count
    pct_types = 100.0 * cov_types / n_types if n_types else 0.0
    pct_tokens = 100.0 * cov_tokens / n_tokens if n_tokens else 0.0
    lines.append("[PHASE70] Chargram tagging (based on p69 rules)")
    lines.append(f"  Rows in p70_token_hits.tsv: {n_hits_rows}")
    lines.append(f"  Types with ≥1 hit:          {cov_types} / {n_types} ({pct_types:.2f} %)")
    lines.append(f"  Tokens with ≥1 hit:         {cov_tokens} / {n_tokens} ({pct_tokens:.2f} %)")
    if rule_counter:
        lines.append("  Top 10 rule labels by hits:")
        for r, c in rule_counter.most_common(10):
            lines.append(f"    {r:20s} {c}")
    lines.append("")
else:
    lines.append("[PHASE70] No coverage stats (missing p70_token_hits.tsv)")
    lines.append("")

if family_rows > 0:
    lines.append("[PHASE71] Token families")
    lines.append(f"  Rows read:                  {family_rows}")
    lines.append(f"  Distinct families:          {n_families}")
    lines.append(f"  Non-trivial families (>1):  {nontrivial_fams}")
    # Show a few example families
    if family_example:
        lines.append("  Example families:")
        for fam, ex in list(family_example.items())[:5]:
            lines.append(f"    {fam:20s} e.g. {ex}")
    lines.append("")
else:
    lines.append("[PHASE71] No family stats (missing p71_token_families.tsv)")
    lines.append("")

if n_edges > 0:
    lines.append("[PHASE73] Rule–rule PMI network")
    lines.append(f"  Nodes (rules with edges):   {n_nodes}")
    lines.append(f"  Edges:                      {n_edges}")
    lines.append(f"  Mean PMI_bits:              {mean_pmi:.3f}")
    lines.append(f"  Median PMI_bits:            {med_pmi:.3f}")
    lines.append(f"  Max PMI_bits:               {max_pmi:.3f}")
    lines.append(f"  Stdev PMI_bits:             {sd_pmi:.3f}")
    # A few strongest links
    top_edges = sorted(pmi_edges, key=lambda x: x[2], reverse=True)[:5]
    lines.append("  Strongest PMI edges:")
    for a,b,p in top_edges:
        lines.append(f"    {a}  –  {b}    ({p:.3f} bits)")
    lines.append("")
else:
    lines.append("[PHASE73] No PMI stats (missing p73_rule_pmi.tsv)")
    lines.append("")

summary = "\n".join(lines)
print(summary)

with open(OUTFILE, "w", encoding="utf-8") as f:
    f.write(summary + "\n")

print(f"[OK] Summary written to {OUTFILE}")
