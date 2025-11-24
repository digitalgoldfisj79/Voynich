#!/usr/bin/env python3
import os, sys, csv

def find_suffix_column(fieldnames):
    # Pick the first header that contains 'suffix' (case-insensitive)
    for name in fieldnames:
        if 'suffix' in name.lower():
            return name
    return None

def main():
    base = os.environ.get("BASE", os.path.join(os.environ["HOME"], "Voynich", "Voynich_Reproducible_Core"))
    slots_path = os.path.join(base, "PhaseS", "out", "s29_slot_profiles.tsv")
    core_path  = os.path.join(base, "PhaseS", "out", "s13_semantic_core_report.tsv")
    out_path   = os.path.join(base, "PhaseS", "out", "s29_slot_profiles_with_suffix.tsv")

    if not os.path.exists(slots_path):
        sys.stderr.write(f"[s29_suffix] ERROR: slots file not found: {slots_path}\n")
        sys.exit(1)
    if not os.path.exists(core_path):
        sys.stderr.write(f"[s29_suffix] ERROR: core file not found: {core_path}\n")
        sys.exit(1)

    # Load semantic core and index suffix by (family, token)
    with open(core_path, "r", encoding="utf-8", newline="") as f_core:
        core_reader = csv.DictReader(f_core, delimiter="\t")
        suffix_col = find_suffix_column(core_reader.fieldnames)
        if suffix_col is None:
            sys.stderr.write(f"[s29_suffix] ERROR: no column containing 'suffix' found in {core_path}\n")
            sys.stderr.write(f"[s29_suffix] Headers: {core_reader.fieldnames}\n")
            sys.exit(1)

        core_map = {}
        n_rows = 0
        for row in core_reader:
            n_rows += 1
            fam = row.get("family", "").strip()
            tok = row.get("token", "").strip()
            if not tok:
                continue
            key = (fam, tok)
            core_map[key] = row.get(suffix_col, "").strip() or "NA"

    # Now enrich slots
    with open(slots_path, "r", encoding="utf-8", newline="") as f_in:
        slots_reader = csv.DictReader(f_in, delimiter="\t")
        fieldnames = list(slots_reader.fieldnames)
        if "suffix" not in fieldnames:
            fieldnames.append("suffix")

        tmp_path = out_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, delimiter="\t", fieldnames=fieldnames)
            writer.writeheader()

            n_in = 0
            n_hit = 0
            for row in slots_reader:
                n_in += 1
                fam = row.get("family", "").strip()
                tok = row.get("token", "").strip()
                key = (fam, tok)
                suffix = core_map.get(key, "NA")
                row["suffix"] = suffix
                writer.writerow(row)
                if suffix != "NA":
                    n_hit += 1

        os.replace(tmp_path, out_path)

    sys.stderr.write(f"[s29_suffix] Done. Input rows={n_in}, matched suffix rows={n_hit}\n")
    sys.stderr.write(f"[s29_suffix] Output written to {out_path}\n")

if __name__ == "__main__":
    main()
