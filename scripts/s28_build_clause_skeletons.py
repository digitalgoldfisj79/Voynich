#!/usr/bin/env python3
import sys, os, csv
from collections import defaultdict

def load_families(path):
    """
    Load stem -> (semantic_family, role_group) mapping from s9b_stem_semantic_families.tsv
    or equivalent. Expects at least columns:
      - token
      - semantic_family
      - role_group   (if missing, falls back to semantic_family)
    """
    families = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = None
        for row in reader:
            if not row:
                continue
            if row[0].startswith("#"):
                continue
            if header is None:
                header = row
                col_idx = {name: i for i, name in enumerate(header)}
                if "token" not in col_idx or "semantic_family" not in col_idx:
                    raise RuntimeError("[S28] Families file missing required columns 'token' and 'semantic_family'")
                has_role_group = "role_group" in col_idx
                continue
            # Data rows
            if len(row) < len(header):
                # Skip malformed line silently
                continue
            token = row[col_idx["token"]]
            sem_fam = row[col_idx["semantic_family"]]
            if not sem_fam:
                sem_fam = "OTHER"
            if has_role_group:
                role = row[col_idx["role_group"]] or "OTHER"
            else:
                role = sem_fam or "OTHER"
            families[token] = (sem_fam, role)
    return families

def load_templates(path):
    """
    Load recurrent templates from s26_recurrent_templates.tsv.
    Expects columns:
      family, role_group, template_id, pattern, count, family_total_instances, coverage_frac
    """
    templates = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = None
        for row in reader:
            if not row:
                continue
            if row[0].startswith("#"):
                continue
            if header is None:
                header = row
                col_idx = {name: i for i, name in enumerate(header)}
                required = ["family", "role_group", "template_id", "pattern",
                            "count", "family_total_instances", "coverage_frac"]
                missing = [c for c in required if c not in col_idx]
                if missing:
                    raise RuntimeError("[S28] Templates file missing columns: " + ", ".join(missing))
                continue
            if len(row) < len(header):
                continue
            fam = row[col_idx["family"]]
            role_group = row[col_idx["role_group"]]
            template_id = row[col_idx["template_id"]]
            pattern = row[col_idx["pattern"]]
            try:
                count = int(row[col_idx["count"]])
            except ValueError:
                continue
            try:
                fam_total = int(row[col_idx["family_total_instances"]])
            except ValueError:
                continue
            try:
                cov = float(row[col_idx["coverage_frac"]])
            except ValueError:
                cov = 0.0
            templates.append({
                "family": fam,
                "role_group": role_group,
                "template_id": template_id,
                "pattern": pattern,
                "count": count,
                "family_total_instances": fam_total,
                "coverage_frac": cov,
            })
    return templates

def build_skeleton(tokens, families_map):
    """
    Build skeleton labels for a pattern token list.
    For each token:
      - family label: semantic_family or 'OTHER'
      - role label: role_group or 'OTHER'
    Returns (skel_families, skel_roles, n_core_tokens, has_cross_family)
    where skel_families and skel_roles are '|' joined strings.
    """
    fam_labels = []
    role_labels = []
    # Centre family (for cross-family check): assume centre = middle token if length odd,
    # else no special centre.
    centre_family = None
    if tokens:
        centre_idx = len(tokens) // 2  # for len=3, this is index 1
    else:
        centre_idx = None

    for idx, tok in enumerate(tokens):
        sem_fam, role = families_map.get(tok, ("OTHER", "OTHER"))
        fam_labels.append(sem_fam if sem_fam else "OTHER")
        role_labels.append(role if role else "OTHER")
        if idx == centre_idx:
            centre_family = sem_fam

    skel_fams = "|".join(fam_labels)
    skel_roles = "|".join(role_labels)

    # n_core_tokens: how many positions are in one of the known core families
    n_core = sum(1 for f in fam_labels if f in ("F_BIO_CORE", "F_BOTANICAL_CORE", "F_PROC_CORE"))

    # has_cross_family: any token whose family differs from centre's family (excluding OTHER)
    has_cross = False
    if centre_family is not None and centre_family != "OTHER":
        for f in fam_labels:
            if f != "OTHER" and f != centre_family:
                has_cross = True
                break

    return skel_fams, skel_roles, n_core, has_cross

def write_tsv(path, header, rows):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
    os.replace(tmp_path, path)

def main():
    if len(sys.argv) != 6:
        sys.stderr.write(
            "[S28] Usage: s28_build_clause_skeletons.py "
            "<templates_tsv> <families_tsv> <out_tsv> <out_summary_tsv> <out_txt>\n"
        )
        sys.exit(1)

    templates_path, families_path, out_tsv, out_summary_tsv, out_txt = sys.argv[1:]

    print(f"[S28] Loading families from {families_path}")
    families_map = load_families(families_path)
    print(f"[S28] Loaded {len(families_map)} stems with family/role labels")

    print(f"[S28] Loading templates from {templates_path}")
    templates = load_templates(templates_path)
    print(f"[S28] Loaded {len(templates)} recurrent templates")

    # Build clause skeletons per template
    out_rows = []
    # For summary aggregation: (family, role_group, skel_fams, skel_roles) -> stats
    summary = defaultdict(lambda: {"n_templates": 0, "total_instances": 0})
    family_totals = {}

    for tpl in templates:
        fam = tpl["family"]
        role_group = tpl["role_group"]
        pattern = tpl["pattern"]
        count = tpl["count"]
        fam_total = tpl["family_total_instances"]
        family_totals[fam] = fam_total

        tokens = pattern.split("|") if pattern else []
        skel_fams, skel_roles, n_core, has_cross = build_skeleton(tokens, families_map)

        out_rows.append([
            fam,
            role_group,
            tpl["template_id"],
            pattern,
            count,
            fam_total,
            "{:.6f}".format(tpl["coverage_frac"]),
            skel_fams,
            skel_roles,
            n_core,
            "YES" if has_cross else "NO",
        ])

        key = (fam, role_group, skel_fams, skel_roles)
        summary[key]["n_templates"] += 1
        summary[key]["total_instances"] += count

    # Write detailed skeleton TSV
    header = [
        "family",
        "role_group",
        "template_id",
        "pattern",
        "count",
        "family_total_instances",
        "coverage_frac",
        "skeleton_families",
        "skeleton_roles",
        "n_core_tokens",
        "has_cross_family",
    ]
    print(f"[S28] Writing clause skeletons to {out_tsv}")
    write_tsv(out_tsv, header, out_rows)

    # Build and write summary TSV
    summary_rows = []
    for (fam, role_group, skel_fams, skel_roles), stats in summary.items():
        fam_total = family_totals.get(fam, 0) or 1
        coverage = stats["total_instances"] / float(fam_total)
        summary_rows.append([
            fam,
            role_group,
            skel_fams,
            skel_roles,
            stats["n_templates"],
            stats["total_instances"],
            "{:.6f}".format(coverage),
        ])

    # Sort summary rows by family then decreasing coverage
    def sort_key(row):
        fam, _, skel_fams, skel_roles, n_templates, total, cov = row
        return (fam, -float(cov), skel_fams, skel_roles)

    summary_rows.sort(key=sort_key)

    summary_header = [
        "family",
        "role_group",
        "skeleton_families",
        "skeleton_roles",
        "n_templates",
        "total_instances",
        "coverage_frac",
    ]
    print(f"[S28] Writing clause skeleton summary to {out_summary_tsv}")
    write_tsv(out_summary_tsv, summary_header, summary_rows)

    # Human-readable TXT summary
    print(f"[S28] Writing clause skeleton summary text to {out_txt}")
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("S28 clause skeleton summary\n")
        f.write("========================================\n\n")

        # Group by family for text
        by_family = defaultdict(list)
        for row in summary_rows:
            fam = row[0]
            by_family[fam].append(row)

        for fam in sorted(by_family.keys()):
            fam_rows = by_family[fam]
            fam_total = family_totals.get(fam, 0)
            f.write(f"Family: {fam}\n")
            f.write(f"  Total frame instances (from S22/S23): {fam_total}\n")
            f.write(f"  Distinct skeleton types: {len(fam_rows)}\n")
            f.write("  Top skeletons (up to 10):\n")
            for i, row in enumerate(fam_rows[:10], start=1):
                _, role_group, skel_fams, skel_roles, n_templates, total_instances, cov = row
                f.write(
                    f"    - {skel_fams}  (roles={skel_roles}, "
                    f"n_templates={n_templates}, count={total_instances}, "
                    f"coverage={cov})\n"
                )
            f.write("\n")

if __name__ == "__main__":
    main()
