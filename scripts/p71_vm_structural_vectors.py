#!/usr/bin/env python3
"""
p71_vm_structural_vectors.py

Builds purely structural vectors for each EVA token type using:
  - Phase70/out/p70_axis1_preview.tsv

Input (p70_axis1_preview.tsv) must have header:
  tok_id  token  left_score  right_score  pred_side  rule_hits

Output:
  Phase71/out/p71_vm_structural_vectors.tsv

Columns:
  token
  count
  first_tok_id
  last_tok_id
  mean_tok_id
  left_count
  right_count
  unknown_count
  left_frac
  right_frac
  unknown_frac
  mean_left_score
  mean_right_score
  mean_rule_hits
  mean_axis_diff    # mean(left_score - right_score)
"""

import os
import sys
import csv
from collections import defaultdict

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")

P70_PATH = os.path.join(BASE, "Phase70", "out", "p70_axis1_preview.tsv")
OUT_DIR  = os.path.join(BASE, "Phase71", "out")
OUT_PATH = os.path.join(OUT_DIR, "p71_vm_structural_vectors.tsv")


def load_axis1_preview(path):
    """
    Load p70_axis1_preview.tsv and aggregate per token.
    Returns a dict token -> stats dict.
    """
    if not os.path.exists(path):
        print(f"[ERROR] Axis1 preview not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            print(f"[ERROR] Empty file: {path}", file=sys.stderr)
            sys.exit(1)

        col_idx = {name: i for i, name in enumerate(header)}
        required = ["tok_id", "token", "left_score", "right_score", "pred_side", "rule_hits"]
        for col in required:
            if col not in col_idx:
                print(f"[ERROR] Missing column '{col}' in {path}", file=sys.stderr)
                print(f"        Header was: {header}", file=sys.stderr)
                sys.exit(1)

        stats = defaultdict(lambda: {
            "count": 0,
            "first_tok_id": None,
            "last_tok_id": None,
            "sum_tok_id": 0,
            "left_count": 0,
            "right_count": 0,
            "unknown_count": 0,
            "sum_left_score": 0.0,
            "sum_right_score": 0.0,
            "sum_rule_hits": 0.0,
            "sum_axis_diff": 0.0,
        })

        total_rows = 0
        for row in reader:
            if not row:
                continue
            total_rows += 1

            try:
                tok_id = int(row[col_idx["tok_id"]])
            except ValueError:
                # Skip malformed rows
                continue

            token      = row[col_idx["token"]]
            pred_side  = row[col_idx["pred_side"]]

            try:
                left_score  = float(row[col_idx["left_score"]])
            except ValueError:
                left_score = 0.0
            try:
                right_score = float(row[col_idx["right_score"]])
            except ValueError:
                right_score = 0.0
            try:
                rule_hits   = int(row[col_idx["rule_hits"]])
            except ValueError:
                rule_hits = 0

            s = stats[token]
            s["count"] += 1
            s["sum_tok_id"] += tok_id

            if s["first_tok_id"] is None or tok_id < s["first_tok_id"]:
                s["first_tok_id"] = tok_id
            if s["last_tok_id"] is None or tok_id > s["last_tok_id"]:
                s["last_tok_id"] = tok_id

            # side counts
            if pred_side == "left":
                s["left_count"] += 1
            elif pred_side == "right":
                s["right_count"] += 1
            else:
                s["unknown_count"] += 1

            s["sum_left_score"]  += left_score
            s["sum_right_score"] += right_score
            s["sum_rule_hits"]   += rule_hits
            s["sum_axis_diff"]   += (left_score - right_score)

    print(f"[INFO] Loaded {total_rows} rows from {path}", file=sys.stderr)
    print(f"[INFO] Aggregated stats for {len(stats)} distinct tokens", file=sys.stderr)
    return stats


def write_structural_vectors(stats, out_path):
    """
    Write aggregated stats to TSV, one row per token.
    """
    tmp_path = out_path + ".tmp"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fieldnames = [
        "token",
        "count",
        "first_tok_id",
        "last_tok_id",
        "mean_tok_id",
        "left_count",
        "right_count",
        "unknown_count",
        "left_frac",
        "right_frac",
        "unknown_frac",
        "mean_left_score",
        "mean_right_score",
        "mean_rule_hits",
        "mean_axis_diff",
    ]

    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(fieldnames)

        # deterministic order: sort by descending count, then lex token
        for token, s in sorted(stats.items(), key=lambda kv: (-kv[1]["count"], kv[0])):
            count = s["count"]
            if count <= 0:
                continue

            left_count    = s["left_count"]
            right_count   = s["right_count"]
            unknown_count = s["unknown_count"]

            left_frac    = left_count / count
            right_frac   = right_count / count
            unknown_frac = unknown_count / count

            mean_tok_id       = s["sum_tok_id"] / count
            mean_left_score   = s["sum_left_score"] / count
            mean_right_score  = s["sum_right_score"] / count
            mean_rule_hits    = s["sum_rule_hits"] / count
            mean_axis_diff    = s["sum_axis_diff"] / count

            row = [
                token,
                count,
                s["first_tok_id"],
                s["last_tok_id"],
                f"{mean_tok_id:.3f}",
                left_count,
                right_count,
                unknown_count,
                f"{left_frac:.3f}",
                f"{right_frac:.3f}",
                f"{unknown_frac:.3f}",
                f"{mean_left_score:.3f}",
                f"{mean_right_score:.3f}",
                f"{mean_rule_hits:.3f}",
                f"{mean_axis_diff:.3f}",
            ]
            writer.writerow(row)

    os.replace(tmp_path, out_path)
    print(f"[OK] Wrote structural vectors → {out_path}", file=sys.stderr)


def main():
    stats = load_axis1_preview(P70_PATH)
    write_structural_vectors(stats, OUT_PATH)


if __name__ == "__main__":
    main()
