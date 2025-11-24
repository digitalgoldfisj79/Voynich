#!/usr/bin/env python3
import os
import sys
from collections import defaultdict

def load_windows(path):
    if not os.path.exists(path):
        raise RuntimeError(f"[S21] Windows file not found: {path}")
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
                # required columns from S20
                for c in ("family", "role_group", "token", "left1", "right1"):
                    if c not in col_idx:
                        raise RuntimeError(f"[S21] Missing required column: {c}")
                continue
            rows.append(parts)
    return header, col_idx, rows

def norm(tok):
    tok = tok.strip()
    return tok if tok else "∅"

def main():
    base = os.environ.get("BASE", os.getcwd())
    windows_path = os.path.join(base, "PhaseS/out/s20_core_context_windows.tsv")
    out_frames = os.path.join(base, "PhaseS/out/s21_family_frames.tsv")

    print(f"[S21] BASE         = {base}")
    print(f"[S21] WINDOWS_PATH = {windows_path}")
    print(f"[S21] OUT_FRAMES   = {out_frames}")
    print(f"[S21] Loading context windows from {windows_path}")

    header, col_idx, rows = load_windows(windows_path)

    # Aggregate frames by (family, role_group, pattern)
    frame_counts = defaultdict(int)

    for parts in rows:
        family = parts[col_idx["family"]]
        role_group = parts[col_idx["role_group"]]
        center = parts[col_idx["token"]]
        left1 = parts[col_idx["left1"]]
        right1 = parts[col_idx["right1"]]

        pattern = f"{norm(left1)}|{center}|{norm(right1)}"
        key = (family, role_group, pattern)
        frame_counts[key] += 1

    os.makedirs(os.path.dirname(out_frames), exist_ok=True)
    with open(out_frames, "w", encoding="utf-8") as out:
        out.write("family\trole_group\tpattern\tcount\n")
        for (family, role_group, pattern), cnt in sorted(
            frame_counts.items(),
            key=lambda x: (x[0][0], -x[1], x[0][2])
        ):
            out.write(f"{family}\t{role_group}\t{pattern}\t{cnt}\n")

    print(f"[S21] Total distinct frames: {len(frame_counts)}")

if __name__ == "__main__":
    main()
