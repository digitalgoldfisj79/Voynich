#!/usr/bin/env python3
import os
import sys
from collections import Counter, defaultdict

def main():
    base = os.environ.get("BASE")
    if not base:
        print("[ERR] BASE not set", file=sys.stderr)
        sys.exit(1)

    tok_path = os.environ.get("TOK_PATH", os.path.join(base, "corpora", "p6_voynich_tokens.txt"))
    out_tokens = os.environ.get("OUT_TOKENS", os.path.join(base, "PhaseS", "out", "s7_voynich_token_suffix2.tsv"))
    out_summary = os.environ.get("OUT_SUMMARY", os.path.join(base, "PhaseS", "out", "s7_voynich_suffix2_tokens_summary.tsv"))

    os.makedirs(os.path.dirname(out_tokens), exist_ok=True)

    token_counts = Counter()
    total_lines = 0

    with open(tok_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            token = line
            token_counts[token] += 1

    print(f"[S7a] Loaded {total_lines} raw lines, {len(token_counts)} distinct tokens from {tok_path}")

    # Write per-token file
    with open(out_tokens, "w", encoding="utf-8") as out:
        out.write("token\ttotal_count\tlength\tsuffix2\n")
        for token, cnt in token_counts.most_common():
            length = len(token)
            if length == 0:
                continue
            if length == 1:
                suffix2 = token
            else:
                suffix2 = token[-2:]
            out.write(f"{token}\t{cnt}\t{length}\t{suffix2}\n")

    print(f"[S7a] Wrote token-level suffix2 table → {out_tokens}")

    # Build suffix2 summary (types & mean length across types)
    suffix2_type_counts = Counter()
    suffix2_type_lengths = defaultdict(list)
    suffix2_token_totals = Counter()

    for token, cnt in token_counts.items():
        length = len(token)
        if length == 0:
            continue
        if length == 1:
            suffix2 = token
        else:
            suffix2 = token[-2:]
        suffix2_type_counts[suffix2] += 1
        suffix2_type_lengths[suffix2].append(length)
        suffix2_token_totals[suffix2] += cnt

    with open(out_summary, "w", encoding="utf-8") as out:
        out.write("suffix2\ttotal_count\tn_types\tmean_len\n")
        for sfx, total_cnt in suffix2_token_totals.most_common():
            n_types = suffix2_type_counts[sfx]
            lengths = suffix2_type_lengths[sfx]
            mean_len = sum(lengths) / float(len(lengths)) if lengths else 0.0
            out.write(f"{sfx}\t{total_cnt}\t{n_types}\t{mean_len:.4f}\n")

    print(f"[S7a] Wrote suffix2 summary → {out_summary}")

if __name__ == "__main__":
    main()
