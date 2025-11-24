#!/usr/bin/env python3
import sys
import csv
from typing import Dict, Tuple

EXPECTED_COLS = [
    "token",
    "total_count",
    "n_folios",
    "n_sections",
    "frac_astro",
    "frac_bio",
    "frac_herbal",
    "frac_pharm",
    "frac_recipes",
    "proc_share",
    "bot_share",
    "bio_share",
    "left_frac",
    "right_frac",
    "unknown_frac",
    "axis_diff",
    "primary_section",
    "structural_class",
]

# ---- Heuristic thresholds (tweakable, but all visible) ----
MIN_COUNT = 5       # below this: too rare → F_LOW_COUNT
MIN_FOLIOS = 2      # stems on a single folio are fragile

PROC_SHARE_STRONG = 0.50
PROC_SHARE_MED    = 0.30
LEFT_FRAC_STRONG  = 0.60
RIGHT_FRAC_STRONG = 0.80

BOT_SHARE_STRONG  = 0.50
BIO_SHARE_STRONG  = 0.50

RECIPES_DOM       = 0.40
HERBAL_DOM        = 0.40
BIO_DOM           = 0.40

def parse_float(row: Dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except Exception:
        return 0.0

def classify_row(row: Dict[str, str]) -> Tuple[str, str]:
    """
    Returns (semantic_family, reason_string).
    Families are intentionally coarse:
      - F_LOW_COUNT       : too rare to trust
      - F_PROC_VERB_CORE  : strong procedural operator
      - F_BIO_PROC        : biological procedure operator
      - F_BOTANICAL_CORE  : botanical/ingredient term
      - F_CONNECTIVE      : connective / grammatical-like
      - F_MEASURE_MOD     : quantity/measure/modifier
      - F_MIXED_PROC      : procedural but structurally mixed
      - F_OTHER_CONTENT   : contentful but not clearly in above families
    """
    token = row["token"]
    total_count = int(row["total_count"])
    n_folios = int(row["n_folios"])

    frac_astro = parse_float(row, "frac_astro")
    frac_bio = parse_float(row, "frac_bio")
    frac_herbal = parse_float(row, "frac_herbal")
    frac_pharm = parse_float(row, "frac_pharm")
    frac_recipes = parse_float(row, "frac_recipes")

    proc_share = parse_float(row, "proc_share")
    bot_share = parse_float(row, "bot_share")
    bio_share = parse_float(row, "bio_share")

    left_frac = parse_float(row, "left_frac")
    right_frac = parse_float(row, "right_frac")
    unknown_frac = parse_float(row, "unknown_frac")

    axis_diff = parse_float(row, "axis_diff")
    primary_section = row["primary_section"]
    structural_class = row["structural_class"]

    # 1) Very low-count stems → not safe
    if total_count < MIN_COUNT or n_folios < MIN_FOLIOS:
        return "F_LOW_COUNT", "low_count_or_local"

    # 2) Clear botanical core (Herbal / botanical share + not strongly procedural)
    if (
        (primary_section == "Herbal" and frac_herbal >= HERBAL_DOM)
        or bot_share >= BOT_SHARE_STRONG
        or structural_class == "CL_BOTANICAL"
    ) and proc_share < PROC_SHARE_MED:
        return "F_BOTANICAL_CORE", "herbal_or_botanical_dominant"

    # 3) Clear biological procedure (Bio/Recipes + high proc + left side)
    if (
        (frac_bio >= BIO_DOM or frac_recipes >= RECIPES_DOM)
        and proc_share >= PROC_SHARE_STRONG
        and left_frac >= LEFT_FRAC_STRONG
    ):
        return "F_BIO_PROC", "bio_recipes_proc_left"

    # 4) General procedural verb/operator (any section, strong proc + left)
    if (
        proc_share >= PROC_SHARE_STRONG
        and left_frac >= LEFT_FRAC_STRONG
    ):
        return "F_PROC_VERB_CORE", "strong_proc_left"

    # 5) Connective / structural: very right-heavy, weak proc, widespread
    if (
        right_frac >= RIGHT_FRAC_STRONG
        and proc_share < PROC_SHARE_MED
        and unknown_frac < 0.5  # not just "unknown"
        and (frac_herbal + frac_recipes + frac_bio) >= 0.40
    ):
        return "F_CONNECTIVE", "right_heavy_structural"

    # 6) Measure / modifier candidates:
    # right-biased, often Bio/Recipes but not strongly procedural
    if (
        right_frac >= 0.60
        and proc_share < PROC_SHARE_STRONG
        and (frac_bio + frac_recipes + frac_pharm) >= 0.40
    ):
        return "F_MEASURE_MOD", "right_biased_measure_modifier"

    # 7) Mixed procedural: medium proc-share, mixed sections
    if (
        PROC_SHARE_MED <= proc_share < PROC_SHARE_STRONG
        and left_frac >= 0.40
        and (frac_bio + frac_recipes + frac_herbal) >= 0.40
    ):
        return "F_MIXED_PROC", "medium_proc_mixed_sections"

    # 8) Everything else that isn't obviously low-count
    return "F_OTHER_CONTENT", "no_strong_family_rule"

def check_header(header: list) -> None:
    missing = [c for c in EXPECTED_COLS if c not in header]
    if missing:
        sys.stderr.write(
            "[S9][ERROR] Missing expected columns in input: {}\n".format(
                ", ".join(missing)
            )
        )
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        sys.stderr.write(
            "Usage: s9_build_semantic_families.py IN_TSV OUT_TSV\n"
        )
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    with open(in_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
        header = reader.fieldnames or []
        check_header(header)

        out_header = header + ["semantic_family", "family_reason"]
        rows_out = []

        for row in reader:
            fam, reason = classify_row(row)
            row_out = dict(row)
            row_out["semantic_family"] = fam
            row_out["family_reason"] = reason
            rows_out.append(row_out)

    # Atomic-ish: write to temp then move
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, delimiter="\t", fieldnames=out_header)
        writer.writeheader()
        for row in rows_out:
            writer.writerow(row)

    import os
    os.replace(tmp_path, out_path)

    sys.stderr.write(
        "[S9] Wrote {} rows with semantic families → {}\n".format(
            len(rows_out), out_path
        )
    )

if __name__ == "__main__":
    main()
