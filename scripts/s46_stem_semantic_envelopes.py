#!/usr/bin/env python3
import os
import csv

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
OUTD = os.path.join(BASE, "PhaseS", "out")

# Input paths
s12_stems_path = os.path.join(OUTD, "s12_semantic_core_stems.tsv")
s34_pos_path   = os.path.join(OUTD, "s34_positional_roles.tsv")
s35_roles_path = os.path.join(OUTD, "s35_clause_roles.tsv")

out_path = os.path.join(OUTD, "s46_stem_semantic_envelopes.tsv")


def load_s12_stems(path):
    """Load core stem table: one row per token, lots of base info."""
    stems = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        # We don't assume exact column set; we keep whatever is there
        base_fields = reader.fieldnames or []
        for row in reader:
            token = row.get("token", "")
            if not token:
                continue
            # Copy base row; we will enrich it
            stems[token] = dict(row)
            # Initialise role / positional fields if not present
            stems[token].update({
                "best_position": "",
                "best_share": "",
                "best_ci_lower": "",
                "best_ci_upper": "",
                "strongly_locked": "",
                "positional_role_label": "",
                "n_clause_hits": 0,
                "n_agent_like": 0,
                "n_patient_like": 0,
                "n_ambiguous": 0,
                "n_other_roles": 0,
                "frac_agent_like": 0.0,
                "frac_patient_like": 0.0,
                "frac_ambiguous": 0.0,
            })
    return stems


def merge_positional_roles(stems, path):
    """Patch stems with positional role info from s34, if available."""
    if not os.path.exists(path):
        print(f"[S46] Warning: positional roles file not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            token = row.get("token", "")
            if not token or token not in stems:
                continue
            s = stems[token]
            s["best_position"] = row.get("best_position", "")
            s["best_share"] = row.get("best_share", "")
            s["best_ci_lower"] = row.get("best_ci_lower", "")
            s["best_ci_upper"] = row.get("best_ci_upper", "")
            s["strongly_locked"] = row.get("strongly_locked", "")
            # This is the coarse positional role label from s34
            s["positional_role_label"] = row.get("role_label", "")


def aggregate_clause_roles(stems, path):
    """Aggregate clause-role behaviour per token from s35."""
    if not os.path.exists(path):
        print(f"[S46] Warning: clause roles file not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                count = int(row.get("count", "0"))
            except ValueError:
                count = 0
            if count <= 0:
                continue

            for pos in ("L", "C", "R"):
                tok = row.get(f"{pos}_token", "")
                role = row.get(f"{pos}_role", "")
                if not tok or tok not in stems:
                    continue

                s = stems[tok]
                s["n_clause_hits"] += count
                role_key = (role or "").upper()
                if role_key == "AGENT_CAND":
                    s["n_agent_like"] += count
                elif role_key == "PATIENT_CAND":
                    s["n_patient_like"] += count
                elif role_key == "AMBIGUOUS":
                    s["n_ambiguous"] += count
                else:
                    s["n_other_roles"] += count

    # Compute fractions
    for s in stems.values():
        total = s["n_clause_hits"]
        if total > 0:
            s["frac_agent_like"] = s["n_agent_like"] / float(total)
            s["frac_patient_like"] = s["n_patient_like"] / float(total)
            s["frac_ambiguous"] = s["n_ambiguous"] / float(total)
        else:
            s["frac_agent_like"] = 0.0
            s["frac_patient_like"] = 0.0
            s["frac_ambiguous"] = 0.0


def main():
    if not os.path.exists(s12_stems_path):
        raise SystemExit(f"[S46] ERROR: cannot find {s12_stems_path}")

    stems = load_s12_stems(s12_stems_path)
    print(f"[S46] Loaded {len(stems)} stems from s12_semantic_core_stems.tsv")

    merge_positional_roles(stems, s34_pos_path)
    aggregate_clause_roles(stems, s35_roles_path)

    # Decide output columns: keep all s12 columns, plus the S46 extras
    # We re-read s12 header to preserve column order.
    with open(s12_stems_path, "r", encoding="utf-8") as f_in:
        base_reader = csv.DictReader(f_in, delimiter="\t")
        base_fields = base_reader.fieldnames or []

    extra_fields = [
        "best_position",
        "best_share",
        "best_ci_lower",
        "best_ci_upper",
        "strongly_locked",
        "positional_role_label",
        "n_clause_hits",
        "n_agent_like",
        "n_patient_like",
        "n_ambiguous",
        "n_other_roles",
        "frac_agent_like",
        "frac_patient_like",
        "frac_ambiguous",
    ]

    # Make sure base fields include 'token'; if not, we add it.
    if "token" not in base_fields:
        base_fields = ["token"] + base_fields

    fieldnames = base_fields + [f for f in extra_fields if f not in base_fields]

    os.makedirs(OUTD, exist_ok=True)
    tmp_path = out_path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        # deterministic order by token
        for token in sorted(stems.keys()):
            s = stems[token]
            row = {}
            for k in fieldnames:
                v = s.get(k, "")
                # normalise floats to a reasonable string form
                if isinstance(v, float):
                    v = f"{v:.6f}"
                row[k] = v
            writer.writerow(row)

    # atomic move
    os.replace(tmp_path, out_path)
    print(f"[S46] Wrote stem semantic envelopes to: {out_path}")


if __name__ == "__main__":
    main()
