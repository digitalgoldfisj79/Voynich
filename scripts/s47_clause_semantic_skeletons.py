#!/usr/bin/env python3
import os
import csv

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
OUTD = os.path.join(BASE, "PhaseS", "out")

s35_roles_path = os.path.join(OUTD, "s35_clause_roles.tsv")
s46_stems_path = os.path.join(OUTD, "s46_stem_semantic_envelopes.tsv")

out_path = os.path.join(OUTD, "s47_clause_semantic_skeletons.tsv")


def load_stem_envelopes(path):
    """Load S46 stem envelopes into a dict: token -> row dict."""
    if not os.path.exists(path):
        raise SystemExit(f"[S47] ERROR: cannot find {path}")

    stems = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []
        for row in reader:
            token = row.get("token", "")
            if not token:
                continue
            stems[token] = row
    print(f"[S47] Loaded {len(stems)} stem envelopes from S46")
    return stems


def main():
    if not os.path.exists(s35_roles_path):
        raise SystemExit(f"[S47] ERROR: cannot find {s35_roles_path}")

    stems = load_stem_envelopes(s46_stems_path)

    # Decide which fields from S46 we want to propagate per slot
    s46_keys = [
        "semantic_family",
        "role_group",
        "primary_section",
        "positional_role_label",
        "best_position",
        "frac_agent_like",
        "frac_patient_like",
        "frac_ambiguous",
    ]

    # Read S35 header to preserve all original columns
    with open(s35_roles_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
        base_fields = reader.fieldnames or []

    # Build extended header
    extra_fields = []
    for pos in ("L", "C", "R"):
        for key in s46_keys:
            extra_fields.append(f"{pos}_{key}")

    fieldnames = base_fields + extra_fields

    os.makedirs(OUTD, exist_ok=True)
    tmp_path = out_path + ".tmp"

    # Process S35 and write extended skeletons
    with open(s35_roles_path, "r", encoding="utf-8") as f_in, \
         open(tmp_path, "w", encoding="utf-8", newline="") as f_out:
        reader = csv.DictReader(f_in, delimiter="\t")
        writer = csv.DictWriter(f_out, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        n_rows = 0
        n_full_sem = 0
        n_any_sem = 0

        for row in reader:
            n_rows += 1
            have_sem = False
            full_sem = True

            out_row = dict(row)

            for pos in ("L", "C", "R"):
                tok = row.get(f"{pos}_token", "")
                stem_env = stems.get(tok)
                if stem_env is None:
                    # no semantic info for this token
                    full_sem = False
                    for key in s46_keys:
                        out_row[f"{pos}_{key}"] = ""
                    continue

                have_sem = True
                for key in s46_keys:
                    v = stem_env.get(key, "")
                    # normalise floats to a reasonable string
                    if key.startswith("frac_"):
                        try:
                            v = f"{float(v):.6f}"
                        except (TypeError, ValueError):
                            v = ""
                    out_row[f"{pos}_{key}"] = v

            if have_sem:
                n_any_sem += 1
            if full_sem:
                n_full_sem += 1

            writer.writerow(out_row)

    os.replace(tmp_path, out_path)
    print(f"[S47] Wrote clause semantic skeletons to: {out_path}")
    print(f"[S47] Total clause patterns: {n_rows}")
    print(f"[S47] Patterns with semantics for at least one slot: {n_any_sem}")
    print(f"[S47] Patterns with semantics for all three slots: {n_full_sem}")


if __name__ == "__main__":
    main()
