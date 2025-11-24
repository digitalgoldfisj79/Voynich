#!/usr/bin/env python3
import argparse
import csv
import os
from collections import defaultdict

REQUIRED_COLS = [
    "family",
    "role_group",
    "token",
    "position",
    "hits",
    "token_total_hits",
    "family_total_instances",
]

def read_slots(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        missing = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing:
            raise RuntimeError(f"[S30] Slot file missing columns: {missing}")

        fam_pos_tokens = defaultdict(lambda: defaultdict(set))
        fam_pos_hits = defaultdict(lambda: defaultdict(int))
        fam_token_pos_hits = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        fam_total_instances = {}

        for row in reader:
            fam = row["family"]
            role = row["role_group"]
            token = row["token"]
            pos = row["position"]
            try:
                hits = int(row["hits"])
            except ValueError:
                continue
            try:
                fam_total = int(row["family_total_instances"])
            except ValueError:
                fam_total = 0

            if fam not in fam_total_instances:
                fam_total_instances[fam] = fam_total
            # we don't strictly enforce equality here, but could

            fam_pos_tokens[fam][pos].add((role, token))
            fam_pos_hits[fam][pos] += hits
            fam_token_pos_hits[fam][token][pos] += hits

    return fam_pos_tokens, fam_pos_hits, fam_token_pos_hits, fam_total_instances

def write_summary_tsv(path, fam_pos_tokens, fam_pos_hits, fam_token_pos_hits):
    tmp_path = path + ".tmp"
    fieldnames = [
        "family",
        "position",              # L/C/R
        "n_tokens",              # distinct tokens with hits at this position
        "total_hits",            # sum of hits across tokens
        "mean_hits_per_token",   # total_hits / n_tokens
        "n_tokens_pref_this",    # tokens whose dominant position is this
    ]

    # precompute dominant position per token within each family
    dominant_counts = defaultdict(lambda: defaultdict(int))  # fam -> pos -> count
    for fam, token_map in fam_token_pos_hits.items():
        for token, pos_map in token_map.items():
            # choose argmax; if ties, treat as "no dominant" and skip
            best_pos = None
            best_hits = -1
            tied = False
            for pos, hits in pos_map.items():
                if hits > best_hits:
                    best_pos = pos
                    best_hits = hits
                    tied = False
                elif hits == best_hits:
                    tied = True
            if not tied and best_pos is not None:
                dominant_counts[fam][best_pos] += 1

    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for fam in sorted(fam_pos_tokens.keys()):
            for pos in ["L", "C", "R"]:
                tokens = fam_pos_tokens[fam].get(pos, set())
                n_tokens = len(tokens)
                total_hits = fam_pos_hits[fam].get(pos, 0)
                mean_hits = (total_hits / n_tokens) if n_tokens > 0 else 0.0
                n_pref = dominant_counts[fam].get(pos, 0)
                writer.writerow({
                    "family": fam,
                    "position": pos,
                    "n_tokens": n_tokens,
                    "total_hits": total_hits,
                    "mean_hits_per_token": f"{mean_hits:.3f}",
                    "n_tokens_pref_this": n_pref,
                })

    os.replace(tmp_path, path)

def write_summary_txt(path, fam_pos_tokens, fam_pos_hits, fam_token_pos_hits, fam_total_instances):
    tmp_path = path + ".tmp"

    # dominant positions again for narrative
    dominant_counts = defaultdict(lambda: defaultdict(int))
    for fam, token_map in fam_token_pos_hits.items():
        for token, pos_map in token_map.items():
            best_pos = None
            best_hits = -1
            tied = False
            for pos, hits in pos_map.items():
                if hits > best_hits:
                    best_pos = pos
                    best_hits = hits
                    tied = False
                elif hits == best_hits:
                    tied = True
            if not tied and best_pos is not None:
                dominant_counts[fam][best_pos] += 1

    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write("S30 slot summary by family and position\n")
        f.write("========================================\n\n")

        for fam in sorted(fam_pos_tokens.keys()):
            fam_total = fam_total_instances.get(fam, 0)
            f.write(f"Family: {fam}\n")
            f.write(f"  Total family instances (from S26): {fam_total}\n")

            for pos in ["L", "C", "R"]:
                tokens = fam_pos_tokens[fam].get(pos, set())
                n_tokens = len(tokens)
                total_hits = fam_pos_hits[fam].get(pos, 0)
                mean_hits = (total_hits / n_tokens) if n_tokens > 0 else 0.0
                n_pref = dominant_counts[fam].get(pos, 0)
                cov = total_hits / fam_total if fam_total > 0 else 0.0
                pos_name = {"L": "left", "C": "centre", "R": "right"}[pos]
                f.write(
                    f"  Position {pos} ({pos_name}): "
                    f"n_tokens={n_tokens}, total_hits={total_hits}, "
                    f"mean_hits={mean_hits:.3f}, coverage={cov:.4f}, "
                    f"n_tokens_pref_this={n_pref}\n"
                )

            # Also show a few example strongly-biased tokens
            # Build per-token preference scores
            token_map = fam_token_pos_hits[fam]
            biased = []
            for token, pos_map in token_map.items():
                total = sum(pos_map.values())
                if total <= 0:
                    continue
                for pos in ["L", "C", "R"]:
                    hits = pos_map.get(pos, 0)
                    share = hits / total
                    biased.append((share, pos, token))
            biased.sort(reverse=True)
            f.write("  Example strongly-positioned tokens (top 10 by share):\n")
            for share, pos, token in biased[:10]:
                pos_name = {"L": "left", "C": "centre", "R": "right"}[pos]
                f.write(
                    f"    - {token} prefers {pos_name} "
                    f"(share={share:.3f})\n"
                )
            f.write("\n")

    os.replace(tmp_path, path)

def main():
    ap = argparse.ArgumentParser(
        description="S30 – summarise slot profiles by family and position."
    )
    ap.add_argument("--slots", required=True, help="s29_slot_profiles.tsv")
    ap.add_argument("--out-tsv", required=True, help="Output TSV summary")
    ap.add_argument("--out-txt", required=True, help="Output TXT summary")
    args = ap.parse_args()

    print(f"[S30] Loading slot profiles from {args.slots}")
    fam_pos_tokens, fam_pos_hits, fam_token_pos_hits, fam_total_instances = read_slots(args.slots)

    print(f"[S30] Families: {len(fam_pos_tokens)}")
    print(f"[S30] Writing TSV summary to {args.out_tsv}")
    write_summary_tsv(args.out_tsv, fam_pos_tokens, fam_pos_hits, fam_token_pos_hits)

    print(f"[S30] Writing TXT summary to {args.out_txt}")
    write_summary_txt(args.out_txt, fam_pos_tokens, fam_pos_hits, fam_token_pos_hits, fam_total_instances)

if __name__ == "__main__":
    main()
