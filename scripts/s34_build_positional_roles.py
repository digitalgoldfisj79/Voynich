#!/usr/bin/env python3
"""
S34: Positional role profiles from slot bootstrap.

Input:
  - s31_slot_bootstrap.tsv (from PhaseS/out):
      family, token, position, hits, token_total_hits,
      position_share, family_total_instances, coverage_frac,
      boot_mean_share, boot_ci_lower, boot_ci_upper, n_boot

Output TSV: s34_positional_roles.tsv
  Columns:
    family
    role_group
    token
    best_position
    best_share
    best_ci_lower
    best_ci_upper
    strongly_locked
    role_label
    total_hits
    family_total_instances
    coverage_frac

Output TXT: s34_positional_roles.txt
  Human-readable summary by family and role_label.
"""

import argparse
import csv
from collections import defaultdict

ROLE_MAP = {
    "L": "AGENT_CAND",
    "C": "PROCESS_CAND",
    "R": "PATIENT_CAND",
}

def guess_role_group(family: str) -> str:
    if family.startswith("F_BIO"):
        return "BIO"
    if family.startswith("F_BOT"):
        return "BOT"
    if family.startswith("F_PROC"):
        return "PROC"
    return "UNKNOWN"

def load_bootstrap(path):
    """
    Return:
      per_token[(family, token)] = {
          "family_total_instances": int,
          "coverage_frac": float,
          "positions": {
              "L": {"share": float, "ci_low": float, "ci_up": float, "hits": int},
              "C": {...},
              "R": {...}
          }
      }
    """
    per_token = {}
    positions = defaultdict(dict)

    with open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            family = row.get("family", "").strip()
            token = row.get("token", "").strip()
            pos = row.get("position", "").strip()

            # Skip junk/empty lines
            if not family or not token or not pos:
                continue
            if family == "family" or token == "token":
                continue

            try:
                hits = int(float(row.get("hits", "0")))
            except ValueError:
                hits = 0
            try:
                share = float(row.get("position_share", "0.0"))
            except ValueError:
                share = 0.0
            try:
                ci_low = float(row.get("boot_ci_lower", "0.0"))
            except ValueError:
                ci_low = 0.0
            try:
                ci_up = float(row.get("boot_ci_upper", "0.0"))
            except ValueError:
                ci_up = 0.0
            try:
                fam_total = int(float(row.get("family_total_instances", "0")))
            except ValueError:
                fam_total = 0
            try:
                cov = float(row.get("coverage_frac", "0.0"))
            except ValueError:
                cov = 0.0

            key = (family, token)
            if key not in per_token:
                per_token[key] = {
                    "family_total_instances": fam_total,
                    "coverage_frac": cov,
                    "positions": {},
                }

            per_token[key]["positions"][pos] = {
                "share": share,
                "ci_low": ci_low,
                "ci_up": ci_up,
                "hits": hits,
            }

    return per_token

def assign_roles(per_token):
    """
    For each (family, token) choose best_position by highest share.
    Strongly-locked if ci_low >= 0.7 at best_position.
    """
    out_rows = []

    for (family, token), info in per_token.items():
        positions = info["positions"]
        if not positions:
            continue

        # Total hits
        total_hits = sum(p.get("hits", 0) for p in positions.values())
        if total_hits <= 0:
            total_hits = 0

        # Choose best position by share (tie broken by L,C,R order)
        best_pos = None
        best_share = -1.0
        best_ci_low = 0.0
        best_ci_up = 0.0

        for pos in ("L", "C", "R"):
            pinfo = positions.get(pos)
            if not pinfo:
                continue
            share = pinfo.get("share", 0.0)
            if share > best_share:
                best_share = share
                best_pos = pos
                best_ci_low = pinfo.get("ci_low", 0.0)
                best_ci_up = pinfo.get("ci_up", 0.0)

        if best_pos is None:
            # shouldn't happen, but guard anyway
            best_pos = "NA"
            strongly_locked = "NO"
            role_label = "AMBIGUOUS"
        else:
            strongly_locked = "YES" if best_ci_low >= 0.7 else "NO"
            if strongly_locked == "YES" and best_pos in ROLE_MAP:
                role_label = ROLE_MAP[best_pos]
            else:
                role_label = "AMBIGUOUS"

        role_group = guess_role_group(family)

        out_rows.append({
            "family": family,
            "role_group": role_group,
            "token": token,
            "best_position": best_pos,
            "best_share": f"{best_share:.6f}",
            "best_ci_lower": f"{best_ci_low:.6f}",
            "best_ci_upper": f"{best_ci_up:.6f}",
            "strongly_locked": strongly_locked,
            "role_label": role_label,
            "total_hits": str(total_hits),
            "family_total_instances": str(info["family_total_instances"]),
            "coverage_frac": f"{info['coverage_frac']:.6f}",
        })

    return out_rows

def write_tsv(path, rows):
    fieldnames = [
        "family",
        "role_group",
        "token",
        "best_position",
        "best_share",
        "best_ci_lower",
        "best_ci_upper",
        "strongly_locked",
        "role_label",
        "total_hits",
        "family_total_instances",
        "coverage_frac",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

def write_txt(path, rows):
    # Aggregate by family and role_label
    per_family = defaultdict(lambda: defaultdict(int))
    for r in rows:
        fam = r["family"]
        role = r["role_label"]
        per_family[fam][role] += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write("S34 positional role profiles\n")
        f.write("========================================\n\n")
        for fam in sorted(per_family.keys()):
            fam_roles = per_family[fam]
            total_tokens = sum(fam_roles.values())
            rg = guess_role_group(fam)
            f.write(f"Family: {fam} ({rg})\n")
            f.write(f"  Tokens with role profile: {total_tokens}\n")
            for role in sorted(fam_roles.keys()):
                count = fam_roles[role]
                frac = count / total_tokens if total_tokens else 0.0
                f.write(f"    - {role}: {count} ({frac:.3f})\n")
            f.write("\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots-bootstrap", required=True, help="Path to s31_slot_bootstrap.tsv")
    ap.add_argument("--out-tsv", required=True)
    ap.add_argument("--out-txt", required=True)
    args = ap.parse_args()

    per_token = load_bootstrap(args.slots_bootstrap)
    rows = assign_roles(per_token)
    write_tsv(args.out_tsv, rows)
    write_txt(args.out_txt, rows)

if __name__ == "__main__":
    main()
