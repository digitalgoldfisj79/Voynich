#!/usr/bin/env python3
import sys
import math

MIN_COUNT_PROC = 50
MIN_COUNT_OTHER = 30
PROC_SHARE_THRESH = 0.45
BOT_SHARE_THRESH = 0.60
BIO_SHARE_THRESH = 0.50
SIDE_SHARE_THRESH = 0.45  # for left/right-heavy

def load_section_distribution(path):
    """Load per-stem section counts from s4_stem_section_distribution.tsv."""
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        # expected columns:
        # token, total_count, n_folios,
        # count_Astronomical, count_Biological, count_Herbal,
        # count_Pharmaceutical, count_Recipes,
        # count_Unassigned, count_Unknown
        idx = {name: i for i, name in enumerate(header)}
        required = [
            "token",
            "total_count",
            "count_Astronomical",
            "count_Biological",
            "count_Herbal",
            "count_Pharmaceutical",
            "count_Recipes",
        ]
        for name in required:
            if name not in idx:
                raise ValueError(f"Missing column {name} in {path}")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or len(parts) < len(idx):
                continue
            tok = parts[idx["token"]]
            try:
                total = int(parts[idx["total_count"]])
                c_ast = int(parts[idx["count_Astronomical"]])
                c_bio = int(parts[idx["count_Biological"]])
                c_her = int(parts[idx["count_Herbal"]])
                c_pha = int(parts[idx["count_Pharmaceutical"]])
                c_rec = int(parts[idx["count_Recipes"]])
            except ValueError:
                # skip header or malformed
                continue
            content_total = c_ast + c_bio + c_her + c_pha + c_rec
            data[tok] = {
                "total_count": total,
                "content_total": content_total,
                "c_ast": c_ast,
                "c_bio": c_bio,
                "c_her": c_her,
                "c_pha": c_pha,
                "c_rec": c_rec,
            }
    return data

def load_structural_vectors(path):
    """Load per-stem structural usage features from s4_stem_structural_vectors.tsv."""
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        required = [
            "token",
            "n_folios",
            "n_sections",
            "left_frac",
            "right_frac",
            "unknown_frac",
            "axis_diff",
            "primary_section",
        ]
        for name in required:
            if name not in idx:
                raise ValueError(f"Missing column {name} in {path}")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or len(parts) < len(idx):
                continue
            tok = parts[idx["token"]]
            try:
                n_fol = int(parts[idx["n_folios"]])
                n_sec = int(parts[idx["n_sections"]])
                left_frac = float(parts[idx["left_frac"]])
                right_frac = float(parts[idx["right_frac"]])
                unknown_frac = float(parts[idx["unknown_frac"]])
                axis_diff = float(parts[idx["axis_diff"]])
                primary_section = parts[idx["primary_section"]]
            except ValueError:
                # skip header or malformed
                continue
            data[tok] = {
                "n_folios": n_fol,
                "n_sections": n_sec,
                "left_frac": left_frac,
                "right_frac": right_frac,
                "unknown_frac": unknown_frac,
                "axis_diff": axis_diff,
                "primary_section": primary_section,
            }
    return data

def assign_class(total_count, proc_share, bot_share, bio_share,
                 left_frac, right_frac):
    """Deterministic structural class assignment."""
    if total_count >= MIN_COUNT_PROC and proc_share >= PROC_SHARE_THRESH:
        if left_frac >= SIDE_SHARE_THRESH:
            return "CL_PROC_LEFT"
        if right_frac >= SIDE_SHARE_THRESH:
            return "CL_PROC_RIGHT"
        return "CL_PROC_MIXED"
    if total_count >= MIN_COUNT_OTHER and bot_share >= BOT_SHARE_THRESH:
        return "CL_BOTANICAL"
    if total_count >= MIN_COUNT_OTHER and bio_share >= BIO_SHARE_THRESH:
        return "CL_BIO"
    if total_count >= MIN_COUNT_OTHER:
        return "CL_MIXED"
    return "CL_LOW_COUNT"

def main(struct_path, sect_path, out_path):
    sect = load_section_distribution(sect_path)
    struct = load_structural_vectors(struct_path)

    tokens = sorted(set(sect.keys()) & set(struct.keys()))
    out = open(out_path, "w", encoding="utf-8")

    header = [
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
    out.write("\t".join(header) + "\n")

    counts_by_class = {}

    for tok in tokens:
        s = sect[tok]
        st = struct[tok]

        total = s["total_count"]
        content_total = s["content_total"]
        if content_total <= 0:
            continue  # no content-section evidence

        frac_astro = s["c_ast"] / content_total
        frac_bio = s["c_bio"] / content_total
        frac_her = s["c_her"] / content_total
        frac_pha = s["c_pha"] / content_total
        frac_rec = s["c_rec"] / content_total

        proc_share = frac_pha + frac_rec
        bot_share = frac_astro + frac_her
        bio_share = frac_bio

        left_frac = st["left_frac"]
        right_frac = st["right_frac"]
        unknown_frac = st["unknown_frac"]
        axis_diff = st["axis_diff"]
        primary_section = st["primary_section"]

        cls = assign_class(
            total, proc_share, bot_share, bio_share,
            left_frac, right_frac
        )
        counts_by_class[cls] = counts_by_class.get(cls, 0) + 1

        row = [
            tok,
            str(total),
            str(st["n_folios"]),
            str(st["n_sections"]),
            f"{frac_astro:.6f}",
            f"{frac_bio:.6f}",
            f"{frac_her:.6f}",
            f"{frac_pha:.6f}",
            f"{frac_rec:.6f}",
            f"{proc_share:.6f}",
            f"{bot_share:.6f}",
            f"{bio_share:.6f}",
            f"{left_frac:.6f}",
            f"{right_frac:.6f}",
            f"{unknown_frac:.6f}",
            f"{axis_diff:.6f}",
            primary_section,
            cls,
        ]
        out.write("\t".join(row) + "\n")

    out.close()

    # Small summary to stdout
    sys.stderr.write("[S8] Structural class counts:\n")
    for cls, n in sorted(counts_by_class.items(), key=lambda x: (-x[1], x[0])):
        sys.stderr.write(f"  {cls}\t{n}\n")
    sys.stderr.write(f"[S8] Wrote {len(tokens)} rows → {out_path}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.stderr.write(
            "Usage: s8_build_stem_semantic_candidates.py "
            "STRUCT_PATH SECT_DIST_PATH OUT_PATH\n"
        )
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
