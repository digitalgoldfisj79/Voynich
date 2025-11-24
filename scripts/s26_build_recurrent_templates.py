#!/usr/bin/env python3
"""
S26: Recurrent Template Rung

Reads s21_family_frames.tsv and extracts all patterns with count >= 2.
Assigns template IDs per family, computes coverage within each family,
and writes both a TSV and a human-readable TXT summary.

Inputs:
  --frames   Path to s21_family_frames.tsv

Outputs:
  --out-tsv  Path to s26_recurrent_templates.tsv
  --out-txt  Path to s26_recurrent_templates.txt
"""

import argparse
import csv
from collections import defaultdict, namedtuple

Frame = namedtuple("Frame", ["family", "role_group", "pattern", "count"])

def load_frames(path):
    frames = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if header is None:
            raise RuntimeError("[S26] Empty frames file")
        # Map columns
        col_idx = {name: i for i, name in enumerate(header)}
        required = ["family", "role_group", "pattern", "count"]
        for c in required:
            if c not in col_idx:
                raise RuntimeError(f"[S26] Missing required column in frames file: {c}")
        fam_idx = col_idx["family"]
        rg_idx = col_idx["role_group"]
        pat_idx = col_idx["pattern"]
        cnt_idx = col_idx["count"]

        for row in reader:
            if not row or len(row) <= max(fam_idx, rg_idx, pat_idx, cnt_idx):
                continue
            family = row[fam_idx].strip()
            role_group = row[rg_idx].strip()
            pattern = row[pat_idx].strip()
            try:
                count = int(row[cnt_idx])
            except ValueError:
                # skip header-like or bad lines
                continue
            frames.append(Frame(family, role_group, pattern, count))
    return frames

def build_templates(frames, min_count=2):
    """
    From a list of Frame objects, select those with count>=min_count,
    grouped by family. Also compute total instances per family.
    """
    by_family = defaultdict(list)
    family_totals = defaultdict(int)

    for fr in frames:
        family_totals[fr.family] += fr.count
        if fr.count >= min_count:
            by_family[fr.family].append(fr)

    # Sort patterns within each family by descending count, then pattern
    for fam, flist in by_family.items():
        flist.sort(key=lambda r: (-r.count, r.pattern))

    return by_family, family_totals

def write_tsv(path, templates_by_family, family_totals):
    """
    Write s26_recurrent_templates.tsv:
    family, role_group, template_id, pattern, count,
    family_total_instances, coverage_frac
    """
    with open(path, "w", encoding="utf-8") as f:
        # Use csv.writer with delimiter and custom lineterm to avoid CRLF confusion
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "family",
            "role_group",
            "template_id",
            "pattern",
            "count",
            "family_total_instances",
            "coverage_frac"
        ])

        for fam in sorted(templates_by_family.keys()):
            total = family_totals.get(fam, 0)
            # derive short family tag for ID
            if fam.startswith("F_") and fam.endswith("_CORE"):
                core_name = fam[2:-5]  # e.g. BIO_CORE -> BIO_
                core_name = core_name.rstrip("_")
            else:
                core_name = fam
            # Some simple mapping: BOTANICAL -> BOT, BIO -> BIO, PROC -> PROC
            # We'll take up to first 3 letters of core_name
            short = core_name[:3].upper()

            for idx, fr in enumerate(templates_by_family[fam], start=1):
                tid = f"T_{short}_{idx:04d}"
                coverage = fr.count / total if total > 0 else 0.0
                writer.writerow([
                    fam,
                    fr.role_group,
                    tid,
                    fr.pattern,
                    fr.count,
                    total,
                    f"{coverage:.6f}",
                ])

def write_txt(path, templates_by_family, family_totals):
    """
    Write s26_recurrent_templates.txt with a readable summary.
    """
    lines = []
    lines.append("S26 recurrent template summary")
    lines.append("========================================")
    lines.append("")

    # Helper: sum coverage
    def fam_coverage(frames, total):
        if total <= 0:
            return 0.0
        return sum(fr.count for fr in frames) / float(total)

    for fam in sorted(templates_by_family.keys()):
        frames = templates_by_family[fam]
        total = family_totals.get(fam, 0)
        n_templates = len(frames)
        cov = fam_coverage(frames, total) * 100.0

        # Extract role_group from first frame (they're consistent)
        role_group = frames[0].role_group if frames else "?"

        lines.append(f"Family: {fam} ({role_group})")
        lines.append(f"  Total frames (instances): {total}")
        lines.append(f"  Recurrent templates (count>=2): {n_templates}")
        lines.append(f"  Coverage by recurrent templates: {cov:.2f}%")

        # Top 10
        lines.append(f"  Top patterns (up to 10):")
        for fr in frames[:10]:
            share = (fr.count / total * 100.0) if total > 0 else 0.0
            lines.append(f"    - {fr.pattern}  (count={fr.count}, {share:.2f}%)")

        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True, help="Path to s21_family_frames.tsv")
    ap.add_argument("--out-tsv", required=True, help="Output TSV path for recurrent templates")
    ap.add_argument("--out-txt", required=True, help="Output TXT path for summary")
    args = ap.parse_args()

    frames = load_frames(args.frames)
    if not frames:
        raise RuntimeError("[S26] No frames loaded; aborting")

    templates_by_family, family_totals = build_templates(frames, min_count=2)

    # Quick sanity checks
    # - sum of counts over all frames should match S23 totals: 2320, 4236, 6394
    #   but we won't enforce it here; that's already verified upstream.

    write_tsv(args.out_tsv, templates_by_family, family_totals)
    write_txt(args.out_txt, templates_by_family, family_totals)

if __name__ == "__main__":
    main()
