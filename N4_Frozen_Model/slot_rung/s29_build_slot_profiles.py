#!/usr/bin/env python3
import argparse
import csv
import os
from collections import defaultdict

REQUIRED_COLS = [
    "family",
    "role_group",
    "template_id",
    "pattern",
    "count",
    "family_total_instances",
]

def read_templates(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        missing = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing:
            raise RuntimeError(f"[S29] Templates file missing columns: {missing}")
        family_totals = {}
        # key: (family, role_group, token, pos_label) -> hits
        slot_hits = defaultdict(int)
        # key: (family, role_group, token) -> total hits across all positions
        token_total_hits = defaultdict(int)

        for row in reader:
            fam = row["family"]
            role_group = row["role_group"]
            pattern = row["pattern"]
            try:
                cnt = int(row["count"])
            except ValueError:
                continue
            try:
                fam_total = int(row["family_total_instances"])
            except ValueError:
                continue

            if fam not in family_totals:
                family_totals[fam] = fam_total
            else:
                if family_totals[fam] != fam_total:
                    raise RuntimeError(
                        f"[S29] Inconsistent family_total_instances for {fam}: "
                        f"{family_totals[fam]} vs {fam_total}"
                    )

            parts = pattern.split("|")
            if len(parts) != 3:
                # We expect all frames to be three-token patterns
                continue

            pos_labels = ["L", "C", "R"]
            for token, pos_label in zip(parts, pos_labels):
                key = (fam, role_group, token, pos_label)
                slot_hits[key] += cnt
                token_key = (fam, role_group, token)
                token_total_hits[token_key] += cnt

    return slot_hits, token_total_hits, family_totals

def write_tsv(path, slot_hits, token_total_hits, family_totals):
    tmp_path = path + ".tmp"
    fieldnames = [
        "family",
        "role_group",
        "token",
        "position",              # L, C, R
        "hits",                  # template-count-weighted hits
        "token_total_hits",      # across all positions for this family
        "position_share",        # hits / token_total_hits
        "family_total_instances",
        "coverage_frac",         # hits / family_total_instances
    ]
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        # Sort for stable, readable output
        for fam, role, token, pos in sorted(slot_hits.keys()):
            hits = slot_hits[(fam, role, token, pos)]
            tok_total = token_total_hits[(fam, role, token)]
            fam_total = family_totals[fam]
            pos_share = hits / tok_total if tok_total > 0 else 0.0
            cov = hits / fam_total if fam_total > 0 else 0.0
            writer.writerow({
                "family": fam,
                "role_group": role,
                "token": token,
                "position": pos,
                "hits": hits,
                "token_total_hits": tok_total,
                "position_share": f"{pos_share:.6f}",
                "family_total_instances": fam_total,
                "coverage_frac": f"{cov:.6f}",
            })
    os.replace(tmp_path, path)

def write_txt(path, slot_hits, token_total_hits, family_totals):
    tmp_path = path + ".tmp"

    # Build convenience views
    # per-family: list of (token, pos, hits)
    per_family = defaultdict(list)
    for (fam, role, token, pos), hits in slot_hits.items():
        per_family[fam].append((role, token, pos, hits))

    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write("S29 slot profile summary\n")
        f.write("========================================\n\n")
        for fam in sorted(per_family.keys()):
            fam_total = family_totals.get(fam, 0)
            items = per_family[fam]
            n_entries = len(items)
            tokens = set((role, token) for (role, token, _pos, _h) in items)
            f.write(f"Family: {fam}\n")
            f.write(f"  Total family instances (from S26): {fam_total}\n")
            f.write(f"  Distinct token/role pairs: {len(tokens)}\n")
            f.write(f"  Distinct token/role/position entries: {n_entries}\n")

            # Top 10 (token, pos) by hits
            sorted_items = sorted(
                items,
                key=lambda tup: tup[3],
                reverse=True
            )
            f.write("  Top token/position slots (up to 10):\n")
            for role, token, pos, hits in sorted_items[:10]:
                tok_total = token_total_hits[(fam, role, token)]
                share = hits / tok_total if tok_total > 0 else 0.0
                frac = hits / fam_total if fam_total > 0 else 0.0
                f.write(
                    f"    - {token} @ {pos} "
                    f"(role={role}, hits={hits}, "
                    f"pos_share={share:.3f}, cov={frac:.4f})\n"
                )
            f.write("\n")

    os.replace(tmp_path, path)

def main():
    ap = argparse.ArgumentParser(
        description="S29 – build per-token slot profiles from recurrent templates."
    )
    ap.add_argument("--templates", required=True, help="s26_recurrent_templates.tsv")
    ap.add_argument("--out-tsv", required=True, help="Output TSV for slot profiles")
    ap.add_argument("--out-txt", required=True, help="Output TXT summary")
    args = ap.parse_args()

    print(f"[S29] Loading templates from {args.templates}")
    slot_hits, token_total_hits, family_totals = read_templates(args.templates)
    print(f"[S29] Slot entries: {len(slot_hits)}")
    print(f"[S29] Families: {len(family_totals)}")

    print(f"[S29] Writing TSV to {args.out_tsv}")
    write_tsv(args.out_tsv, slot_hits, token_total_hits, family_totals)

    print(f"[S29] Writing TXT summary to {args.out_txt}")
    write_txt(args.out_txt, slot_hits, token_total_hits, family_totals)

if __name__ == "__main__":
    main()
