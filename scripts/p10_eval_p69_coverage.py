#!/usr/bin/env python3
import os
import sys
import subprocess
from collections import Counter, defaultdict
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_TOKENS = ROOT / "corpora" / "p6_voynich_tokens.txt"
SEG_FILE = ROOT / "corpora" / "voynich_segmented_p69.txt"
SEGMENT_SCRIPT = ROOT / "scripts" / "p9_segment_with_p69.py"

MIN_SEG_PARTS = 2          # treat ≥2 chunks as segmented
MIN_STEM_TOKENS = 10       # stems need ≥10 token-support to be counted
N_PERM = 500               # permutations for null distribution


def read_tokens(path):
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                tokens.append(t)
    return tokens


def ensure_segmentation():
    if SEG_FILE.is_file():
        print(f"[INFO] Using existing segmentation: {SEG_FILE}")
        return
    if not SEGMENT_SCRIPT.is_file():
        print(f"[ERR] Segmentation script not found: {SEGMENT_SCRIPT}", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] Running Phase 69 segmentation via {SEGMENT_SCRIPT} ...")
    subprocess.run([sys.executable, str(SEGMENT_SCRIPT)], check=True)
    if not SEG_FILE.is_file():
        print(f"[ERR] Expected segmentation file not found after run: {SEG_FILE}", file=sys.stderr)
        sys.exit(1)


def split_seg(seg_str):
    """Split segmentation string into parts on +, ., or whitespace."""
    s = seg_str.strip()
    if not s:
        return []
    # normalize separators to spaces
    for ch in ["+", "."]:
        s = s.replace(ch, " ")
    parts = [p for p in s.split() if p]
    return parts


def parse_segmentation_line(line):
    """
    Robust parser for the various formats p9_segment_with_p69.py
    might have produced.

    Supported:
      raw<TAB>seg
      raw seg
      seg-only (e.g. qo+ked+y) → raw reconstructed by stripping separators
    """
    line = line.strip()
    if not line:
        return None, None

    raw = None
    seg = None

    if "\t" in line:
        # format: raw<TAB>segmentation
        lhs, rhs = line.split("\t", 1)
        raw = lhs.strip() or None
        seg = rhs.strip() or None
    else:
        parts = line.split()
        if len(parts) >= 2:
            # format: raw seg
            raw = parts[0].strip() or None
            seg = " ".join(parts[1:]).strip() or None
        else:
            # seg-only
            seg = parts[0].strip()
            # reconstruct raw by removing common separators
            raw = seg.replace("+", "").replace(".", "").replace(" ", "")

    if not seg:
        return raw, None

    seg_parts = split_seg(seg)
    if not seg_parts:
        return raw, None

    return raw, seg_parts


def entropy(dist):
    total = sum(dist.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for c in dist.values():
        p = c / total
        if p > 0:
            h -= p * math.log2(p)
    return h


def main():
    if not CORPUS_TOKENS.is_file():
        print(f"[ERR] Missing {CORPUS_TOKENS}. Run p6_build_voynich_tokens.py first.", file=sys.stderr)
        sys.exit(1)

    ensure_segmentation()

    tokens = read_tokens(CORPUS_TOKENS)
    type_counts = Counter(tokens)
    types = sorted(type_counts.keys())
    total_types = len(types)
    total_tokens = len(tokens)

    # read segmentation file
    seg_map = {}
    with open(SEG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            raw, seg_parts = parse_segmentation_line(line)
            if raw is None or not seg_parts:
                continue
            # only keep if segmentation is non-trivial
            if len(seg_parts) >= MIN_SEG_PARTS:
                # in case of duplicates, keep first; they should be consistent
                if raw not in seg_map:
                    seg_map[raw] = seg_parts

    if not seg_map:
        print("[ERR] No usable segmentations read from "
              f"{SEG_FILE}. Check its format.", file=sys.stderr)
        sys.exit(1)

    # Coverage counts
    segmented_types = 0
    segmented_tokens = 0

    # Stem-suffix distributions
    stem_suffix = defaultdict(Counter)   # stem → suffix counts
    stem_token_counts = Counter()

    for t in types:
        count = type_counts[t]
        seg_parts = seg_map.get(t)
        if not seg_parts or len(seg_parts) < MIN_SEG_PARTS:
            continue

        segmented_types += 1
        segmented_tokens += count

        # crude but consistent:
        # if 2+ parts: stem = all but last; suffix = last
        if len(seg_parts) >= 2:
            stem = "".join(seg_parts[:-1])
            suffix = seg_parts[-1]
        else:
            continue

        if stem and suffix:
            stem_suffix[stem][suffix] += count
            stem_token_counts[stem] += count

    print("[RESULT] Phase 69 segmentation coverage:")
    print(f"  Types with ≥{MIN_SEG_PARTS} segments: {segmented_types} / {total_types} "
          f"({segmented_types/total_types:.2%})")
    print(f"  Tokens with ≥{MIN_SEG_PARTS} segments: {segmented_tokens} / {total_tokens} "
          f"({segmented_tokens/total_tokens:.2%})")

    # Collect stems with enough evidence and >1 suffix type
    real_entropies = []
    eligible_stems = []
    for stem, suff_dist in stem_suffix.items():
        if stem_token_counts[stem] >= MIN_STEM_TOKENS and len(suff_dist) > 1:
            h = entropy(suff_dist)
            real_entropies.append(h)
            eligible_stems.append(stem)

    if not real_entropies:
        print("[WARN] No stems met criteria (MIN_STEM_TOKENS, >1 suffix). "
              "Adjust thresholds if needed.")
        sys.exit(0)

    real_mean = sum(real_entropies) / len(real_entropies)
    print(f"[RESULT] Mean suffix entropy over informative stems: "
          f"{real_mean:.3f} bits (n_stems={len(real_entropies)})")

    # Build suffix pool for permutation test
    suffix_pool = []
    stem_sizes = {}
    for stem in eligible_stems:
        dist = stem_suffix[stem]
        size = sum(dist.values())
        stem_sizes[stem] = size
        for s, c in dist.items():
            suffix_pool.extend([s] * c)

    if len(suffix_pool) < 2:
        print("[WARN] Not enough suffix tokens for permutation test.")
        sys.exit(0)

    null_means = []
    for _ in range(N_PERM):
        random.shuffle(suffix_pool)
        idx = 0
        ent_vals = []
        for stem in eligible_stems:
            size = stem_sizes[stem]
            assigned = suffix_pool[idx:idx+size]
            idx += size
            dist = Counter(assigned)
            if len(dist) > 1:
                ent_vals.append(entropy(dist))
        if ent_vals:
            null_means.append(sum(ent_vals) / len(ent_vals))

    if not null_means:
        print("[WARN] Null distribution empty; cannot compute p-value.")
        sys.exit(0)

    null_mean = sum(null_means) / len(null_means)
    # tighter-than-random = lower entropy
    more_extreme = sum(1 for x in null_means if x <= real_mean)
    p_value = more_extreme / len(null_means)

    print(f"[RESULT] Null mean suffix entropy: {null_mean:.3f} bits")
    print(f"[RESULT] p (null ≤ observed) = {p_value:.3f}")
    print("Interpretation: small p means Phase 69 yields systematically tighter "
          "stem–suffix behavior than randomized baselines → genuine structure.")


if __name__ == "__main__":
    main()
