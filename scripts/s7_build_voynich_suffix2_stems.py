#!/usr/bin/env python3
import os
import csv
import collections

def load_stems(stem_path):
    stems = []
    with open(stem_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)

        # Try to locate columns by name; fall back to first two
        try:
            token_idx = header.index("token")
        except ValueError:
            token_idx = 0

        count_idx = None
        for cand in ("total_count", "freq", "count"):
            if cand in header:
                count_idx = header.index(cand)
                break
        if count_idx is None:
            count_idx = 1

        for row in reader:
            if not row:
                continue
            token = row[token_idx].strip()
            if not token:
                continue
            try:
                freq = int(row[count_idx])
            except ValueError:
                # allow float in case of weirdness
                try:
                    freq = int(float(row[count_idx]))
                except ValueError:
                    continue
            stems.append((token, freq))
    return stems

def main():
    base = os.environ.get(
        "BASE",
        os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
    )
    stem_path = os.environ.get(
        "STEM_PATH",
        os.path.join(base, "PhaseS/out/s4_stem_structural_vectors.tsv")
    )
    out_stems = os.environ.get(
        "OUT_STEMS",
        os.path.join(base, "PhaseS/out/s7_voynich_stem_suffix2.tsv")
    )
    out_summary = os.environ.get(
        "OUT_SUMMARY",
        os.path.join(base, "PhaseS/out/s7_voynich_suffix2_stems_summary.tsv")
    )

    print(f"[S7b] BASE       = {base}")
    print(f"[S7b] STEM_PATH  = {stem_path}")
    print(f"[S7b] OUT_STEMS  = {out_stems}")
    print(f"[S7b] OUT_SUMMARY= {out_summary}")

    stems = load_stems(stem_path)
    print(f"[S7b] Loaded {len(stems)} stems from {stem_path}")

    # Write token-level table
    os.makedirs(os.path.dirname(out_stems), exist_ok=True)
    with open(out_stems, "w", encoding="utf-8", newline="") as f_out:
        w = csv.writer(f_out, delimiter="\t")
        w.writerow(["token", "total_count", "suffix2"])
        for token, freq in stems:
            suffix2 = token[-2:] if len(token) >= 2 else token
            w.writerow([token, freq, suffix2])

    # Aggregate summary by suffix2
    suffix_counts = collections.Counter()
    type_sets = collections.defaultdict(set)
    length_weighted = collections.Counter()
    total_tokens = 0

    for token, freq in stems:
        suf = token[-2:] if len(token) >= 2 else token
        suffix_counts[suf] += freq
        type_sets[suf].add(token)
        length_weighted[suf] += len(token) * freq
        total_tokens += freq

    with open(out_summary, "w", encoding="utf-8", newline="") as f_sum:
        w = csv.writer(f_sum, delimiter="\t")
        w.writerow(["suffix2", "total_count", "n_types", "mean_len"])
        for suf, cnt in sorted(suffix_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            n_types = len(type_sets[suf])
            mean_len = (length_weighted[suf] / cnt) if cnt > 0 else 0.0
            w.writerow([suf, cnt, n_types, f"{mean_len:.4f}"])

    print(f"[S7b] Wrote stem-level suffix2 table → {out_stems}")
    print(f"[S7b] Wrote suffix2 stems summary   → {out_summary}")

if __name__ == "__main__":
    main()
