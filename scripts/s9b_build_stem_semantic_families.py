#!/usr/bin/env python3
import sys
import csv

def load_mv_table(path):
    """
    Load the materia–dante–voynich suffix2 table.

    Expected columns:
      suffix2, materia_total, materia_frac, dante_total, dante_frac,
      vm_total, vm_frac, abs_diff_m_d, abs_diff_m_v, abs_diff_d_v
    """
    mv = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            s2 = row["suffix2"]
            try:
                mf = float(row.get("materia_frac", "0") or 0.0)
                df = float(row.get("dante_frac", "0") or 0.0)
                vf = float(row.get("vm_frac", "0") or 0.0)
            except ValueError:
                mf = df = vf = 0.0
            mv[s2] = {
                "materia_frac": mf,
                "dante_frac": df,
                "vm_frac": vf,
            }
    return mv

def get_suffix2(token: str) -> str:
    if len(token) >= 2:
        return token[-2:]
    return token

def classify_family(row, mv_info):
    """
    Decide semantic_family, role_group, reason and attach
    materia/dante/voynich suffix fractions.

    Inputs: one row from s8_stem_semantic_candidates.tsv + mv_info dict.
    Returns:
      semantic_family, role_group, family_reason, materia_frac, dante_frac, vm_frac
    """
    token = row["token"]
    total_count = int(row["total_count"])
    n_folios = int(row["n_folios"])
    struct_class = row["structural_class"]

    proc_share = float(row["proc_share"])
    bot_share = float(row["bot_share"])
    bio_share = float(row["bio_share"])

    # section fractions (may be useful)
    frac_astro = float(row["frac_astro"])
    frac_bio   = float(row["frac_bio"])
    frac_herbal= float(row["frac_herbal"])
    frac_pharm = float(row["frac_pharm"])
    frac_rec   = float(row["frac_recipes"])

    # default suffix stats
    s2 = get_suffix2(token)
    mv = mv_info.get(s2, None)
    if mv is None:
        materia_frac = 0.0
        dante_frac   = 0.0
        vm_frac      = 0.0
    else:
        materia_frac = mv["materia_frac"]
        dante_frac   = mv["dante_frac"]
        vm_frac      = mv["vm_frac"]

    # ---- base family by count / spread ----
    # Low count / local noise
    if total_count < 5 or n_folios < 3:
        semantic_family = "F_LOW_COUNT"
        role_group = "OTHER"
        reason = "low_count_or_local"
    else:
        # Main structural groups
        if struct_class == "CL_BOTANICAL" or bot_share >= 0.5 or frac_herbal >= 0.4:
            semantic_family = "F_BOTANICAL_CORE"
            role_group = "BOT"
            reason = "herbal_or_botanical_dominant"
        elif struct_class in ("CL_PROC_LEFT", "CL_PROC_RIGHT", "CL_PROC_MIXED") or proc_share >= 0.5 or frac_rec >= 0.4:
            semantic_family = "F_PROC_CORE"
            role_group = "PROC"
            reason = "procedural_or_recipes_dominant"
        elif struct_class == "CL_BIO" or bio_share >= 0.5 or frac_bio >= 0.4:
            semantic_family = "F_BIO_CORE"
            role_group = "BIO"
            reason = "biological_section_dominant"
        else:
            semantic_family = "F_OTHER_CONTENT"
            role_group = "OTHER"
            reason = "no_strong_family_rule"

    # ---- suffix-based enrichment (non-destructive) ----
    # We *annotate* but don't change core family; keeps bundles comparable.
    # "Materia tilt" = suffix more characteristic of De materia than Dante,
    # with non-trivial voynich presence.
    delta_md = materia_frac - dante_frac
    if vm_frac > 0.0 and materia_frac > 0.0 and delta_md > 0.01:
        reason += ";materia_tilt_suffix"

    return semantic_family, role_group, reason, materia_frac, dante_frac, vm_frac

def main():
    if len(sys.argv) != 4:
        sys.stderr.write(
            "Usage: s9b_build_stem_semantic_families.py "
            "<s8_candidates.tsv> <materia_dante_voynich_suffix2.tsv> <out.tsv>\n"
        )
        sys.exit(1)

    in_path = sys.argv[1]
    mv_table = sys.argv[2]
    out_path = sys.argv[3]

    mv_info = load_mv_table(mv_table)
    sys.stderr.write(f"[S9b] Loaded {len(mv_info)} suffix2 rows from MV table\n")

    with open(in_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8", newline="") as fout:

        reader = csv.DictReader(fin, delimiter="\t")
        fieldnames = reader.fieldnames + [
            "semantic_family",
            "role_group",
            "family_reason",
            "materia_frac",
            "dante_frac",
            "vm_frac",
        ]
        writer = csv.DictWriter(fout, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        n_rows = 0
        for row in reader:
            (
                semantic_family,
                role_group,
                family_reason,
                materia_frac,
                dante_frac,
                vm_frac,
            ) = classify_family(row, mv_info)

            row_out = dict(row)
            row_out["semantic_family"] = semantic_family
            row_out["role_group"] = role_group
            row_out["family_reason"] = family_reason
            row_out["materia_frac"] = f"{materia_frac:.8f}"
            row_out["dante_frac"] = f"{dante_frac:.8f}"
            row_out["vm_frac"] = f"{vm_frac:.8f}"
            writer.writerow(row_out)
            n_rows += 1

    sys.stderr.write(f"[S9b] Wrote {n_rows} rows → {out_path}\n")

if __name__ == "__main__":
    main()
