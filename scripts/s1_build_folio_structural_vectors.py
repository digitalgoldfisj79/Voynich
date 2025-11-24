#!/usr/bin/env python3
"""
s1_build_folio_structural_vectors.py

Build per-folio structural vectors using:

  - TOK_PATH: folio-token stream (default: PhaseS/out/p6_folio_tokens.tsv)
      format (TSV, header or headerless OK if 4 cols):
        token<TAB>header_tag<TAB>line<TAB>pos
      where header_tag looks like: "f1r>      <! $Q=A ..."

  - TYPES_PATH: per-token structural vectors
      e.g. Phase71/out/p71_vm_structural_vectors.tsv
      required columns:
        token, left_frac, right_frac, unknown_frac,
        mean_left_score, mean_right_score,
        mean_rule_hits, mean_axis_diff

  - SECTION_PATH: folio → section map
      e.g. sections_map_frameworkB.tsv (with header: folio<TAB>section)

Output:
  - OUT_PATH: PhaseS/out/s1_folio_structural_vectors.tsv

Columns:
  folio, section, total_tokens, total_types,
  avg_left_frac, avg_right_frac, avg_unknown_frac,
  avg_left_score, avg_right_score,
  avg_rule_hits, avg_axis_diff
"""

import os
import sys
import csv
from collections import defaultdict

BASE = os.path.expanduser(os.environ.get("BASE", "~/Voynich/Voynich_Reproducible_Core"))

TOK_PATH     = os.environ.get("TOK_PATH",     os.path.join(BASE, "p6_folio_tokens.tsv"))
TYPES_PATH   = os.environ.get("TYPES_PATH",   os.path.join(BASE, "Phase71", "out", "p71_vm_structural_vectors.tsv"))
SECTION_PATH = os.environ.get("SECTION_PATH", os.path.join(BASE, "sections_map_frameworkB.tsv"))
OUT_DIR      = os.path.join(BASE, "PhaseS", "out")
OUT_PATH     = os.environ.get("OUT_PATH",     os.path.join(OUT_DIR, "s1_folio_structural_vectors.tsv"))


def load_sections(path):
    sections = {}
    if not os.path.exists(path):
        sys.stderr.write(f"[WARN] Section map not found: {path}\n")
        return sections
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            folio, sec = parts[0].strip(), parts[1].strip()
            if folio:
                sections[folio] = sec
    sys.stderr.write(f"[INFO] Loaded {len(sections)} folio→section mappings\n")
    return sections


def load_structural_types(path):
    if not os.path.exists(path):
        sys.stderr.write(f"[ERROR] Structural vectors file not found: {path}\n")
        sys.exit(1)

    feats = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = [
            "token",
            "left_frac", "right_frac", "unknown_frac",
            "mean_left_score", "mean_right_score",
            "mean_rule_hits", "mean_axis_diff",
        ]
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            sys.stderr.write(f"[ERROR] Missing required columns in %s: %s\n" % (path, missing))
            sys.exit(1)

        for row in reader:
            tok = row["token"].strip()
            if not tok:
                continue
            try:
                feats[tok] = {
                    "left_frac":       float(row["left_frac"]),
                    "right_frac":      float(row["right_frac"]),
                    "unknown_frac":    float(row["unknown_frac"]),
                    "mean_left_score": float(row["mean_left_score"]),
                    "mean_right_score":float(row["mean_right_score"]),
                    "mean_rule_hits":  float(row["mean_rule_hits"]),
                    "mean_axis_diff":  float(row["mean_axis_diff"]),
                }
            except ValueError:
                continue

    sys.stderr.write(f"[INFO] Loaded structural features for {len(feats)} token types\n")
    return feats


def extract_folio(header_tag):
    """
    header_tag looks like:
      'f1r>      <! $Q=A $P=A ...'
    We take everything before the first '>' as the folio ID.
    """
    if not header_tag:
        return ""
    parts = header_tag.split(">", 1)
    return parts[0].strip()


def build_folio_vectors(tok_path, type_feats, sections, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp_path = out_path + ".tmp"

    total_tokens = defaultdict(int)
    type_sets    = defaultdict(set)
    sums         = defaultdict(lambda: defaultdict(float))

    n_lines = 0
    n_used  = 0
    n_missing_type = 0

    with open(tok_path, "r", encoding="utf-8") as f:
        for raw in f:
            n_lines += 1
            line = raw.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            tok = parts[0].strip()
            header_tag = parts[1].strip()
            if not tok:
                continue

            folio = extract_folio(header_tag)
            if not folio:
                continue

            if tok not in type_feats:
                n_missing_type += 1
                continue

            feats = type_feats[tok]

            total_tokens[folio] += 1
            type_sets[folio].add(tok)

            for key, val in feats.items():
                sums[folio][key] += val

            n_used += 1

    with open(tmp_path, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "folio", "section",
            "total_tokens", "total_types",
            "avg_left_frac", "avg_right_frac", "avg_unknown_frac",
            "avg_left_score", "avg_right_score",
            "avg_rule_hits", "avg_axis_diff",
        ])

        for folio in sorted(total_tokens.keys()):
            n = total_tokens[folio]
            t = len(type_sets[folio])
            sec = sections.get(folio, "Unknown")

            def avg(key):
                return sums[folio][key] / n if n > 0 else 0.0

            writer.writerow([
                folio, sec,
                n, t,
                avg("left_frac"),
                avg("right_frac"),
                avg("unknown_frac"),
                avg("mean_left_score"),
                avg("mean_right_score"),
                avg("mean_rule_hits"),
                avg("mean_axis_diff"),
            ])

    os.replace(tmp_path, out_path)

    sys.stderr.write(f"[INFO] Processed %d lines from %s\n" % (n_lines, tok_path))
    sys.stderr.write(f"[INFO] Used %d token instances with structural features\n" % n_used)
    sys.stderr.write(f"[INFO] Missing-type tokens (skipped): %d\n" % n_missing_type)
    sys.stderr.write(f"[OK] Wrote folio structural vectors → %s\n" % out_path)


def main():
    if not os.path.exists(TOK_PATH):
        sys.stderr.write(f"[ERROR] Token stream not found: %s\n" % TOK_PATH)
        sys.exit(1)

    sections = load_sections(SECTION_PATH)
    type_feats = load_structural_types(TYPES_PATH)
    build_folio_vectors(TOK_PATH, type_feats, sections, OUT_PATH)


if __name__ == "__main__":
    main()
