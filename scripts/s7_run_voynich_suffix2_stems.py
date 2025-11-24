#!/usr/bin/env python3
import os
import sys
from collections import Counter, defaultdict

def main():
    base = os.environ.get("BASE")
    if not base:
        print("[ERR] BASE not set", file=sys.stderr)
        sys.exit(1)

    stem_path = os.environ.get("STEM_PATH", os.path.join(base, "PhaseS", "out", "s5_stem_structural_summary.tsv"))
    out_stems = os.environ.get("OUT_STEMS", os.path.join(base, "PhaseS", "out", "s7_voynich_stem_suffix2.tsv"))
    out_summary = os.environ.get("OUT_SUMMARY", os.path.join(base, "PhaseS", "out", "s7_voynich_suffix2_stems_summary.tsv"))

    os.makedirs(os.path.dirname(out_stems), exist_ok=True)

    stem_counts = {}
    total_lines = 0

    with open(stem_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            if line.startswith("token\t"):
                # header
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            token = parts[0]
            try:
                count = int(parts[1])
            except ValueError:
                continue
            stem_counts[token] = count
            total_lines += 1

    print(f"[S7b] Loaded {total_lines} stem rows from {stem_path} ({len(stem_counts)} distinct tokens)")

    with open(out_stems, "w", encoding="utf-8") as out:
        out.write("token\ttotal_count\tlength\tsuffix2\n")
        for token, cnt in sorted(stem_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            length = len(token)
            if length == 0:
                continue
            if length == 1:
                suffix2 = token
            else:
                suffix2 = token[-2:]
            out.write(f"{token}\t{cnt}\t{length}\t{suffix2}\n")

    print(f"[S7b] Wrote stem-level suffix2 table → {out_stems}")

    # Build suffix2 summary for stems
    suffix2_type_counts = Counter()
    suffix2_type_lengths = defaultdict(list)
    suffix2_token_totals = Counter()

    for token, cnt in stem_counts.items():
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

    print(f"[S7b] Wrote stem suffix2 summary → {out_summary}")

if __name__ == "__main__":
    main()
