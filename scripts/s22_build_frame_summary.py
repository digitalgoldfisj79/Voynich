#!/usr/bin/env python3
import os
from collections import defaultdict

def load_frames(path):
    if not os.path.exists(path):
        raise RuntimeError(f"[S22] Frames file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        header = None
        col_idx = {}
        rows = []
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if header is None:
                header = parts
                col_idx = {c: i for i, c in enumerate(header)}
                for c in ("family", "role_group", "pattern", "count"):
                    if c not in col_idx:
                        raise RuntimeError(f"[S22] Missing required column: {c}")
                continue
            rows.append(parts)
    return header, col_idx, rows

def main():
    base = os.environ.get("BASE", os.getcwd())
    frames_path = os.path.join(base, "PhaseS/out/s21_family_frames.tsv")
    out_tsv = os.path.join(base, "PhaseS/out/s22_frame_summary.tsv")
    out_txt = os.path.join(base, "PhaseS/out/s22_frame_summary.txt")

    print(f"[S22] BASE        = {base}")
    print(f"[S22] FRAMES_PATH = {frames_path}")
    print(f"[S22] OUT_TSV     = {out_tsv}")
    print(f"[S22] OUT_TXT     = {out_txt}")

    header, col_idx, rows = load_frames(frames_path)

    # Per-family aggregation
    family_stats = defaultdict(lambda: {
        "role_groups": set(),
        "total_instances": 0,
        "frames": {},  # pattern -> count
    })

    for parts in rows:
        family = parts[col_idx["family"]]
        role_group = parts[col_idx["role_group"]]
        pattern = parts[col_idx["pattern"]]
        try:
            count = int(parts[col_idx["count"]])
        except ValueError:
            # skip bad line
            continue

        fs = family_stats[family]
        fs["role_groups"].add(role_group)
        fs["total_instances"] += count
        fs["frames"][pattern] = fs["frames"].get(pattern, 0) + count

    os.makedirs(os.path.dirname(out_tsv), exist_ok=True)

    # TSV summary
    with open(out_tsv, "w", encoding="utf-8") as out:
        out.write("# S22 frame summary\n")
        out.write("family\trole_groups\tn_frames\ttotal_instances\ttop_patterns\n")
        for family in sorted(family_stats.keys()):
            fs = family_stats[family]
            frames = fs["frames"]
            n_frames = len(frames)
            total_instances = fs["total_instances"]
            # top 10 patterns
            top = sorted(frames.items(), key=lambda x: -x[1])[:10]
            top_str = "; ".join(f"{p}:{c}" for p, c in top)
            role_groups_str = ",".join(sorted(fs["role_groups"]))
            out.write(
                f"{family}\t{role_groups_str}\t{n_frames}\t"
                f"{total_instances}\t{top_str}\n"
            )

    # TXT narrative summary
    with open(out_txt, "w", encoding="utf-8") as out:
        out.write("S22 family frame summary\n")
        out.write("========================================\n\n")
        for family in sorted(family_stats.keys()):
            fs = family_stats[family]
            frames = fs["frames"]
            n_frames = len(frames)
            total_instances = fs["total_instances"]
            role_groups = ", ".join(sorted(fs["role_groups"]))
            out.write(f"Family: {family}\n")
            out.write(f"  Role groups: {role_groups}\n")
            out.write(f"  Distinct frames: {n_frames}\n")
            out.write(f"  Total frame instances: {total_instances}\n")
            out.write("  Top patterns (up to 10):\n")
            top = sorted(frames.items(), key=lambda x: -x[1])[:10]
            for pattern, cnt in top:
                out.write(f"    - {pattern}  (count={cnt})\n")
            out.write("\n")

    print(f"[S22] Families summarised: {len(family_stats)}")

if __name__ == "__main__":
    main()
