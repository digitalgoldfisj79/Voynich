#!/usr/bin/env python3
import csv
import argparse
from collections import defaultdict

def load_slot_suffixes(path):
    """
    Load (family, token, position) -> suffix from s29_slot_profiles_with_suffix.tsv.
    Skip junk/NA rows.
    """
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            family = (row.get("family") or "").strip()
            token = (row.get("token") or "").strip()
            pos   = (row.get("position") or "").strip()
            suffix = (row.get("suffix") or "").strip()
            if not family or not token or not pos:
                continue
            if suffix == "" or suffix.upper() == "NA":
                suffix = "NA"
            mapping[(family, token, pos)] = suffix
    return mapping

def parse_int(val, default=0):
    if val is None:
        return default
    s = str(val).strip()
    if not s:
        return default
    try:
        return int(s)
    except ValueError:
        # Handle things like "3AGENT..." that crept in
        digits = ""
        for ch in s:
            if ch.isdigit():
                digits += ch
            else:
                break
        if digits:
            try:
                return int(digits)
            except ValueError:
                return default
        return default

def parse_float(val, default=0.0):
    if val is None:
        return default
    s = str(val).strip()
    if not s:
        return default
    try:
        return float(s)
    except ValueError:
        return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", required=True, help="s29_slot_profiles_with_suffix.tsv")
    ap.add_argument("--catalogue", required=True, help="s36_clause_role_catalogue.tsv")
    ap.add_argument("--out-pairs", required=True, help="output TSV with agent/patient pairs")
    ap.add_argument("--out-suffix", required=True, help="output TSV with suffix pair aggregates")
    ap.add_argument("--out-txt", required=True, help="human-readable summary")
    args = ap.parse_args()

    # 1) Load suffix map from s29
    suffix_map = load_slot_suffixes(args.slots)

    # 2) Scan s36 catalogue and collect agent–patient clauses
    pair_rows = []
    suffix_stats = defaultdict(lambda: {
        "n_templates": 0,
        "total_count": 0,
        "family_total_instances": 0,
    })

    with open(args.catalogue, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            family = (row.get("family") or "").strip()
            role_group = (row.get("role_group") or "").strip()
            template_id = (row.get("template_id") or "").strip()
            pattern = (row.get("pattern") or "").strip()
            role_pattern = (row.get("clause_role_pattern") or "").strip()
            count = parse_int(row.get("count"), 0)
            fam_total = parse_int(row.get("family_total_instances"), 0)
            coverage = parse_float(row.get("coverage_frac"), 0.0)

            if not family or not pattern:
                continue
            if count <= 0:
                continue
            if role_pattern != "AGENT_CAND-AMBIGUOUS-PATIENT_CAND":
                continue

            parts = pattern.split("|")
            if len(parts) != 3:
                continue
            L_tok, C_tok, R_tok = [p.strip() for p in parts]

            # Lookup suffixes from s29 (AGENT=L, PATIENT=R)
            agent_suffix = suffix_map.get((family, L_tok, "L"), "NA")
            patient_suffix = suffix_map.get((family, R_tok, "R"), "NA")

            pair_rows.append({
                "family": family,
                "role_group": role_group,
                "template_id": template_id,
                "agent_token": L_tok,
                "process_token": C_tok,
                "patient_token": R_tok,
                "agent_suffix": agent_suffix,
                "patient_suffix": patient_suffix,
                "count": count,
                "family_total_instances": fam_total,
                "coverage_frac": coverage,
                "clause_role_pattern": role_pattern,
            })

            key = (family, agent_suffix, patient_suffix)
            suffix_stats[key]["n_templates"] += 1
            suffix_stats[key]["total_count"] += count
            # Assume fam_total consistent per family; last seen wins
            suffix_stats[key]["family_total_instances"] = fam_total

    # 3) Write pairs TSV (atomic via .tmp)
    pairs_tmp = args.out_pairs + ".tmp"
    with open(pairs_tmp, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "family",
            "role_group",
            "template_id",
            "agent_token",
            "process_token",
            "patient_token",
            "agent_suffix",
            "patient_suffix",
            "count",
            "family_total_instances",
            "coverage_frac",
            "clause_role_pattern",
        ]
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in pair_rows:
            writer.writerow(row)

    # 4) Write suffix aggregates TSV
    suffix_tmp = args.out_suffix + ".tmp"
    with open(suffix_tmp, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "family",
            "agent_suffix",
            "patient_suffix",
            "n_templates",
            "total_clause_count",
            "mean_count_per_template",
            "family_total_instances",
            "approx_coverage",
        ]
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for (family, a_suf, p_suf), stats in suffix_stats.items():
            n_t = stats["n_templates"]
            total_c = stats["total_count"]
            fam_total = stats["family_total_instances"] or 1
            mean_c = total_c / n_t if n_t > 0 else 0.0
            approx_cov = total_c / float(fam_total) if fam_total > 0 else 0.0
            writer.writerow({
                "family": family,
                "agent_suffix": a_suf,
                "patient_suffix": p_suf,
                "n_templates": n_t,
                "total_clause_count": total_c,
                "mean_count_per_template": f"{mean_c:.4f}",
                "family_total_instances": fam_total,
                "approx_coverage": f"{approx_cov:.6f}",
            })

    # 5) Write a short human summary
    # Sort suffix pairs by approx_coverage descending
    sorted_pairs = sorted(
        suffix_stats.items(),
        key=lambda kv: (kv[1]["total_count"] / float(kv[1]["family_total_instances"] or 1)),
        reverse=True,
    )

    with open(args.out_txt, "w", encoding="utf-8") as f:
        f.write("S37 agent–patient suffix pairs summary\n")
        f.write("=====================================\n\n")
        f.write(f"Total agent–patient templates: {len(pair_rows)}\n")
        f.write(f"Total suffix pairs: {len(sorted_pairs)}\n\n")

        f.write("Top 20 suffix pairs by approx coverage:\n")
        f.write("--------------------------------------\n")
        for i, ((family, a_suf, p_suf), stats) in enumerate(sorted_pairs[:20], start=1):
            fam_total = stats["family_total_instances"] or 1
            approx_cov = stats["total_count"] / float(fam_total)
            f.write(
                f"{i:2d}. {family}  "
                f"agent_suffix={a_suf:>5}  patient_suffix={p_suf:>5}  "
                f"n_templates={stats['n_templates']:3d}  "
                f"total_count={stats['total_count']:3d}  "
                f"approx_coverage={approx_cov:.5f}\n"
            )

    # 6) Move tmp -> final (atomic-ish)
    import os
    os.replace(pairs_tmp, args.out_pairs)
    os.replace(suffix_tmp, args.out_suffix)

if __name__ == "__main__":
    main()
