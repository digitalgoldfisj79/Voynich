#!/usr/bin/env python3
"""
Apply the p69 calibrated axis-1 rulebook to a flat token list.

Inputs
------
1) tokens file: one EVA token per line (no header)
2) rules JSON: p69_rules_calibrated.json
3) output TSV for token-level scores
4) output TSV for type-level aggregation
"""

import sys
import json
from collections import defaultdict

def load_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_rules = data.get("rules", [])
    rules = []

    for r in raw_rules:
        kind = r["kind"]
        pattern = r["pattern"]
        pred_side = r["pred_side"]
        w = float(r.get("base_weight", 1.0))

        # ignore section-specific masks here (no section info in p6 tokens)
        if kind == "chargram":
            rules.append(("chargram", pattern, pred_side, w))
        elif kind == "prefix":
            rules.append(("prefix", pattern, pred_side, w))
        elif kind == "suffix":
            rules.append(("suffix", pattern, pred_side, w))
        elif kind == "pair":
            if "|" in pattern:
                pre, suf = pattern.split("|", 1)
            else:
                pre, suf = "", ""
            rules.append(("pair", (pre, suf), pred_side, w))
        else:
            continue

    return rules


def apply_rules_to_token(tok, rules):
    left = 0.0
    right = 0.0

    for kind, pattern, pred_side, w in rules:
        hit = False

        if kind == "chargram":
            if pattern in tok:
                hit = True
        elif kind == "prefix":
            if tok.startswith(pattern):
                hit = True
        elif kind == "suffix":
            if tok.endswith(pattern):
                hit = True
        elif kind == "pair":
            pre, suf = pattern
            if pre and not tok.startswith(pre):
                continue
            if suf and not tok.endswith(suf):
                continue
            hit = True

        if not hit:
            continue

        if pred_side == "left":
            left += w
        elif pred_side == "right":
            right += w

    return left, right


def side_from_scores(left, right):
    if left == 0.0 and right == 0.0:
        return "unknown"
    if left > right:
        return "left"
    if right > left:
        return "right"
    return "tie"


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 4:
        sys.stderr.write(
            "Usage: p69_apply_rules_simple.py "
            "<tokens.txt> <p69_rules_calibrated.json> "
            "<out_tokens.tsv> <out_types.tsv>\n"
        )
        sys.exit(1)

    tokens_path, rules_path, out_tokens_path, out_types_path = argv

    rules = load_rules(rules_path)

    type_accum = defaultdict(lambda: {
        "n": 0, "n_hit": 0, "left": 0.0, "right": 0.0,
        "n_left": 0, "n_right": 0, "n_tie": 0, "n_unknown": 0
    })

    # token-level output
    with open(tokens_path, "r", encoding="utf-8") as f_in, \
         open(out_tokens_path, "w", encoding="utf-8") as f_tok:

        f_tok.write("token\tleft_score\tright_score\tpred_side\trule_hits\n")

        for line in f_in:
            tok = line.strip()
            if not tok:
                continue

            left, right = apply_rules_to_token(tok, rules)
            side = side_from_scores(left, right)
            hits = int(left > 0.0 or right > 0.0)

            f_tok.write(f"{tok}\t{left:.6f}\t{right:.6f}\t{side}\t{hits}\n")

            acc = type_accum[tok]
            acc["n"] += 1
            acc["left"] += left
            acc["right"] += right
            if hits:
                acc["n_hit"] += 1
            if side == "left":
                acc["n_left"] += 1
            elif side == "right":
                acc["n_right"] += 1
            elif side == "tie":
                acc["n_tie"] += 1
            elif side == "unknown":
                acc["n_unknown"] += 1

    # type-level aggregation
    with open(out_types_path, "w", encoding="utf-8") as f_typ:
        f_typ.write(
            "token_type\tn_tokens\tn_hit\tmean_left\tmean_right\t"
            "net_score\tfrac_hit\tfrac_left\tfrac_right\tfrac_tie\t"
            "frac_unknown\tmaj_side\n"
        )

        for tok, acc in sorted(type_accum.items()):
            n = acc["n"]
            n_hit = acc["n_hit"]
            mean_left = acc["left"] / n if n else 0.0
            mean_right = acc["right"] / n if n else 0.0
            net = mean_left - mean_right
            frac_hit = n_hit / n if n else 0.0
            frac_left = acc["n_left"] / n if n else 0.0
            frac_right = acc["n_right"] / n if n else 0.0
            frac_tie = acc["n_tie"] / n if n else 0.0
            frac_unknown = acc["n_unknown"] / n if n else 0.0

            counts = {
                "left": acc["n_left"],
                "right": acc["n_right"],
                "tie": acc["n_tie"],
                "unknown": acc["n_unknown"],
            }
            non_unknown_total = acc["n_left"] + acc["n_right"] + acc["n_tie"]
            if non_unknown_total > 0:
                counts.pop("unknown", None)
            maj_side = max(counts.items(), key=lambda kv: kv[1])[0] if counts else "unknown"

            f_typ.write(
                f"{tok}\t{n}\t{n_hit}\t"
                f"{mean_left:.6f}\t{mean_right:.6f}\t{net:.6f}\t"
                f"{frac_hit:.6f}\t{frac_left:.6f}\t{frac_right:.6f}\t"
                f"{frac_tie:.6f}\t{frac_unknown:.6f}\t{maj_side}\n"
            )

if __name__ == "__main__":
    main()
