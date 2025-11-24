#!/usr/bin/env python3
import sys
import csv

"""
S9 – Stem semantic families

Inputs:
  PhaseS/out/s8_stem_semantic_candidates.tsv

Outputs:
  PhaseS/out/s9_stem_semantic_families.tsv

This script assigns each stem to a coarse structural/semantic family.
Thresholds here are heuristic *hyperparameters* and can be tuned.
They are NOT empirical “findings”.
"""

# -----------------------------
# Hyperparameters (tunable)
# -----------------------------

MIN_COUNT_CORE = 20          # below this → F_LOW_FREQ
MIN_FOLIOS_CORE = 3          # minimum folios for anything “core”

# Botanical core: mostly Herbal/“content” folios
BOT_SHARE_MIN = 0.60         # botanical share threshold for F_BOTANICAL_CORE
HERBAL_FRAC_MIN = 0.55       # frac_herbal threshold

# “Connective” stems: cross-section, right-heavy, low procedural share
CONNECTIVE_RIGHT_MIN = 0.95  # right_frac threshold
CONNECTIVE_PROC_MAX = 0.25   # max proc_share
CONNECTIVE_MIN_SECTIONS = 4  # must appear in many sections

# Procedural left-heavy (bio/recipes)
PROC_LEFT_MIN = 0.90         # left_frac threshold
PROC_PROC_SHARE_MIN = 0.25   # overall procedural share threshold
PROC_BIO_REC_MIN = 0.40      # frac_bio + frac_recipes minimum

# Mixed proc family: less strict, but still clearly procedural
MIXED_LEFT_MIN = 0.80
MIXED_PROC_SHARE_MIN = 0.20
MIXED_BIO_REC_MIN = 0.30

# -----------------------------
# Helpers
# -----------------------------

def classify_family(row):
    """
    row is a dict from s8_stem_semantic_candidates.tsv:
      token, total_count, n_folios, n_sections,
      frac_astro, frac_bio, frac_herbal, frac_pharm, frac_recipes,
      proc_share, bot_share, bio_share,
      left_frac, right_frac, unknown_frac,
      axis_diff, primary_section, structural_class
    Returns (family_id, family_label).
    """

    token = row["token"]
    try:
        total_count = int(row["total_count"])
        n_folios = int(row["n_folios"])
        n_sections = int(row["n_sections"])
        frac_astro = float(row["frac_astro"])
        frac_bio = float(row["frac_bio"])
        frac_herbal = float(row["frac_herbal"])
        frac_pharm = float(row["frac_pharm"])
        frac_recipes = float(row["frac_recipes"])
        proc_share = float(row["proc_share"])
        bot_share = float(row["bot_share"])
        bio_share = float(row["bio_share"])
        left_frac = float(row["left_frac"])
        right_frac = float(row["right_frac"])
    except ValueError:
        # If anything is malformed, push into a catch-all family
        return "F_OTHER_CONTENT", "other_or_unclassified"

    primary_section = row["primary_section"]
    structural_class = row["structural_class"]

    # 1) Low frequency guardrail
    if total_count < MIN_COUNT_CORE or n_folios < MIN_FOLIOS_CORE:
        return "F_LOW_FREQ", "low_frequency_or_sparse"

    # 2) Botanical / Herbal-core content
    if (
        bot_share >= BOT_SHARE_MIN
        and frac_herbal >= HERBAL_FRAC_MIN
    ):
        return "F_BOTANICAL_CORE", "herbal_or_botanical_dominant"

    # 3) Strong procedural, left-heavy, bio/recipes-weighted
    bio_rec = frac_bio + frac_recipes

    if (
        left_frac >= PROC_LEFT_MIN
        and proc_share >= PROC_PROC_SHARE_MIN
        and bio_rec >= PROC_BIO_REC_MIN
    ):
        # Distinguish a bit between pure bio-procedural vs recipes-procedural
        if frac_recipes > frac_bio:
            return "F_RECIPES_PROC_LEFT", "recipes_proc_left"
        else:
            return "F_BIO_PROC_LEFT", "bio_proc_left"

    # 4) Mixed procedural family (less strict, but recognisably procedural)
    if (
        left_frac >= MIXED_LEFT_MIN
        and proc_share >= MIXED_PROC_SHARE_MIN
        and bio_rec >= MIXED_BIO_REC_MIN
    ):
        return "F_MIXED_PROC", "medium_proc_mixed_sections"

    # 5) Connective / structural: right-heavy, cross-section, low procedural
    if (
        right_frac >= CONNECTIVE_RIGHT_MIN
        and proc_share <= CONNECTIVE_PROC_MAX
        and n_sections >= CONNECTIVE_MIN_SECTIONS
    ):
        return "F_CONNECTIVE", "right_heavy_structural"

    # 6) Bio-dominated content stems without strong procedural signal
    if bio_share >= 0.50 and primary_section in ("Biological", "Recipes"):
        return "F_BIO_CONTENT", "bio_or_recipe_content"

    # 7) Fallbacks based on structural_class
    if structural_class.startswith("CL_BOTANICAL"):
        return "F_BOTANICAL_MISC", "botanical_content_no_strong_family"
    if structural_class.startswith("CL_BIO"):
        return "F_BIO_MISC", "bio_content_no_strong_family"

    # 8) Default catch-all
    return "F_OTHER_CONTENT", "other_or_unclassified"

# -----------------------------
# Main
# -----------------------------

def main():
    if len(sys.argv) != 3:
        sys.stderr.write(
            "Usage: s9_build_stem_semantic_families.py "
            "<s8_stem_semantic_candidates.tsv> "
            "<s9_stem_semantic_families.tsv>\n"
        )
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    with open(in_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
        fieldnames = reader.fieldnames + ["family_id", "family_label"]

        rows = []
        for row in reader:
            fid, flabel = classify_family(row)
            row["family_id"] = fid
            row["family_label"] = flabel
            rows.append(row)

    with open(out_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    sys.stderr.write(f"[S9] Wrote {len(rows)} rows → {out_path}\n")


if __name__ == "__main__":
    main()
