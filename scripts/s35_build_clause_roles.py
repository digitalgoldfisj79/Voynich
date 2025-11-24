#!/usr/bin/env python3
"""
S35: Clause role patterns from skeletons + positional roles.

Inputs:
  - s28_clause_skeletons.tsv (PhaseS/out)
      family, role_group, template_id, pattern,
      count, family_total_instances, coverage_frac,
      skeleton_families, skeleton_roles, n_core_tokens, has_cross_family

  - s34_positional_roles.tsv (PhaseS/out)
      family, role_group, token, best_position, best_share,
      best_ci_lower, best_ci_upper, strongly_locked,
      role_label, total_hits, family_total_instances, coverage_frac

Output TSV: s35_clause_roles.tsv
  Columns:
    family
    role_group
    template_id
    pattern
    count
    family_total_instances
    coverage_frac
    L_token
    C_token
    R_token
    L_role
    C_role
    R_role
    clause_role_pattern

Output TXT: s35_clause_roles_summary.txt
  Summary by family and clause_role_pattern.
"""

import argparse
import csv
from collections import defaultdict

def load_roles(path):
    """
    Map (family, token) -> role_label
    """
    roles = {}
    with open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            fam = row.get("family", "").strip()
            tok = row.get("token", "").strip()
            role = row.get("role_label", "").strip()
            if not fam or not tok:
                continue
            if fam == "family" or tok == "token":
                continue
            roles[(fam, tok)] = role if role else "AMBIGUOUS"
    return roles

def load_skeletons(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            fam = row.get("family", "").strip()
            if not fam or fam == "family":
                continue
            rows.append(row)
    return rows

def split_pattern(pattern):
    parts = pattern.split("|")
    if len(parts) != 3:
        # pad or truncate defensively
        if len(parts) < 3:
            parts = (parts + ["NA", "NA", "NA"])[:3]
        else:
            parts = parts[:3]
    return parts[0], parts[1], parts[2]

def build_clause_roles(skeleton_rows, roles_map):
    out_rows = []

    for row in skeleton_rows:
        fam = row.get("family", "").strip()
        role_group = row.get("role_group", "").strip()
        template_id = row.get("template_id", "").strip()
        pattern = row.get("pattern", "").strip()

        L_tok, C_tok, R_tok = split_pattern(pattern)

        L_role = roles_map.get((fam, L_tok), "UNKNOWN")
        C_role = roles_map.get((fam, C_tok), "UNKNOWN")
        R_role = roles_map.get((fam, R_tok), "UNKNOWN")

        clause_role_pattern = f"{L_role}-{C_role}-{R_role}"

        out_rows.append({
            "family": fam,
            "role_group": role_group,
            "template_id": template_id,
            "pattern": pattern,
            "count": row.get("count", ""),
            "family_total_instances": row.get("family_total_instances", ""),
            "coverage_frac": row.get("coverage_frac", ""),
            "L_token": L_tok,
            "C_token": C_tok,
            "R_token": R_tok,
            "L_role": L_role,
            "C_role": C_role,
            "R_role": R_role,
            "clause_role_pattern": clause_role_pattern,
        })

    return out_rows

def write_tsv(path, rows):
    fieldnames = [
        "family",
        "role_group",
        "template_id",
        "pattern",
        "count",
        "family_total_instances",
        "coverage_frac",
        "L_token",
        "C_token",
        "R_token",
        "L_role",
        "C_role",
        "R_role",
        "clause_role_pattern",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

def write_txt(path, rows):
    per_family = defaultdict(lambda: defaultdict(int))
    per_family_cov = defaultdict(lambda: defaultdict(float))

    for r in rows:
        fam = r["family"]
        crp = r["clause_role_pattern"]
        per_family[fam][crp] += 1
        try:
            cov = float(r.get("coverage_frac", "0.0"))
        except ValueError:
            cov = 0.0
        per_family_cov[fam][crp] += cov

    with open(path, "w", encoding="utf-8") as f:
        f.write("S35 clause role patterns\n")
        f.write("========================================\n\n")
        for fam in sorted(per_family.keys()):
            f.write(f"Family: {fam}\n")
            total_templates = sum(per_family[fam].values())
            f.write(f"  Templates with role pattern: {total_templates}\n")
            sorted_patterns = sorted(
                per_family[fam].items(),
                key=lambda kv: (-per_family_cov[fam][kv[0]], -kv[1])
            )
            for pattern, count in sorted_patterns:
                cov = per_family_cov[fam][pattern]
                freq = count / total_templates if total_templates else 0.0
                f.write(
                    f"    - {pattern}: n_templates={count}, "
                    f"freq={freq:.3f}, coverage≈{cov:.4f}\n"
                )
            f.write("\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skeletons", required=True, help="Path to s28_clause_skeletons.tsv")
    ap.add_argument("--roles", required=True, help="Path to s34_positional_roles.tsv")
    ap.add_argument("--out-tsv", required=True)
    ap.add_argument("--out-txt", required=True)
    args = ap.parse_args()

    roles_map = load_roles(args.roles)
    skeleton_rows = load_skeletons(args.skeletons)
    out_rows = build_clause_roles(skeleton_rows, roles_map)
    write_tsv(args.out_tsv, out_rows)
    write_txt(args.out_txt, out_rows)

if __name__ == "__main__":
    main()
