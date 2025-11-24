#!/usr/bin/env python3
"""
p70_preview_axis1.py (simple, robust version)

Takes:
  - corpora/p6_voynich_tokens.txt           (one token per line, corpus order)
  - Phase69/out/p69_axis1_tokens.tsv        (axis-1 scores per token TYPE)

Produces:
  - Phase70/out/p70_axis1_preview.tsv

Output columns:
  tok_id    : 1-based index in p6_voynich_tokens stream
  token     : EVA token as in p6 file
  left_score
  right_score
  pred_side : left / right / unknown
  rule_hits : integer (0 if not covered by rulebook)
"""

import os
import sys
import csv

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")

TOKENS_PATH      = os.path.join(BASE, "corpora", "p6_voynich_tokens.txt")
AXIS1_TOK_PATH   = os.path.join(BASE, "Phase69", "out", "p69_axis1_tokens.tsv")
OUT_DIR          = os.path.join(BASE, "Phase70", "out")
OUT_PATH         = os.path.join(OUT_DIR, "p70_axis1_preview.tsv")


def load_axis1_token_table(path):
    """
    Load p69_axis1_tokens.tsv into a dict:
      axis_info[token] = (left_score, right_score, pred_side, rule_hits)
    """
    axis_info = {}

    if not os.path.exists(path):
        print(f"[ERROR] Axis-1 token file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            print(f"[ERROR] Empty axis-1 token file: {path}", file=sys.stderr)
            sys.exit(1)

        # Map column name -> index
        col_idx = {name: i for i, name in enumerate(header)}

        required = ["token", "left_score", "right_score", "pred_side", "rule_hits"]
        for col in required:
            if col not in col_idx:
                print(f"[ERROR] Missing required column '{col}' in {path}", file=sys.stderr)
                print(f"        Header was: {header}", file=sys.stderr)
                sys.exit(1)

        for row in reader:
            if not row:
                continue
            token = row[col_idx["token"]]
            try:
                left_score  = float(row[col_idx["left_score"]])
                right_score = float(row[col_idx["right_score"]])
            except ValueError:
                # Fallback: treat non-numeric as 0
                left_score  = 0.0
                right_score = 0.0
            pred_side  = row[col_idx["pred_side"]]
            try:
                rule_hits = int(row[col_idx["rule_hits"]])
            except ValueError:
                rule_hits = 0

            axis_info[token] = (left_score, right_score, pred_side, rule_hits)

    print(f"[INFO] Loaded axis-1 info for {len(axis_info)} token types from {path}", file=sys.stderr)
    return axis_info


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    axis_info = load_axis1_token_table(AXIS1_TOK_PATH)

    if not os.path.exists(TOKENS_PATH):
        print(f"[ERROR] Token stream not found: {TOKENS_PATH}", file=sys.stderr)
        sys.exit(1)

    tmp_path = OUT_PATH + ".tmp"
    total = 0
    covered = 0

    with open(TOKENS_PATH, "r", encoding="utf-8") as f_in, \
         open(tmp_path, "w", encoding="utf-8", newline="") as f_out:

        writer = csv.writer(f_out, delimiter="\t", lineterminator="\n")
        writer.writerow(["tok_id", "token", "left_score", "right_score", "pred_side", "rule_hits"])

        for tok_id, line in enumerate(f_in, start=1):
            token = line.rstrip("\n")
            if token == "":
                continue

            total += 1
            if token in axis_info:
                left_score, right_score, pred_side, rule_hits = axis_info[token]
                covered += 1
            else:
                left_score  = 0.0
                right_score = 0.0
                pred_side   = "unknown"
                rule_hits   = 0

            writer.writerow([tok_id, token, left_score, right_score, pred_side, rule_hits])

    os.replace(tmp_path, OUT_PATH)

    cov_pct = 100.0 * covered / total if total else 0.0
    print(f"[OK] Wrote axis-1 preview → {OUT_PATH}", file=sys.stderr)
    print(f"[INFO] Tokens: {total}, with axis-1 info: {covered} ({cov_pct:.1f}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
