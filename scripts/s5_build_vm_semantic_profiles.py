#!/usr/bin/env python3
import sys
import csv

def load_structural(path):
    structural = {}
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            token = row.get('token', '')
            if not token:
                continue
            structural[token] = row
    return structural

def get_float(row, key, default=0.0):
    val = row.get(key)
    if val is None or val == '':
        return default
    try:
        return float(val)
    except ValueError:
        return default

def main():
    if len(sys.argv) != 4:
        print(
            "Usage: s5_build_vm_semantic_profiles.py "
            "<s4_stem_structural_vectors.tsv> "
            "<s4_stem_section_distribution.tsv> "
            "<out_tsv>",
            file=sys.stderr,
        )
        sys.exit(1)

    struct_path = sys.argv[1]
    dist_path = sys.argv[2]
    out_path = sys.argv[3]

    structural = load_structural(struct_path)

    out_rows = []

    with open(dist_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            token = row.get('token', '')
            if not token:
                continue

            total_count = get_float(row, 'total_count', 0.0)
            n_folios = get_float(row, 'n_folios', 0.0)

            c_ast  = get_float(row, 'count_Astronomical', 0.0)
            c_bio  = get_float(row, 'count_Biological', 0.0)
            c_herb = get_float(row, 'count_Herbal', 0.0)
            c_phar = get_float(row, 'count_Pharmaceutical', 0.0)
            c_rec  = get_float(row, 'count_Recipes', 0.0)
            c_unas = get_float(row, 'count_Unassigned', 0.0)
            c_unk  = get_float(row, 'count_Unknown', 0.0)

            if total_count > 0.0:
                f_ast  = c_ast  / total_count
                f_bio  = c_bio  / total_count
                f_herb = c_herb / total_count
                f_phar = c_phar / total_count
                f_rec  = c_rec  / total_count
                f_unas = c_unas / total_count
                f_unk  = c_unk  / total_count
            else:
                f_ast = f_bio = f_herb = f_phar = f_rec = f_unas = f_unk = 0.0

            srow = structural.get(token, {})
            left_frac   = get_float(srow, 'left_frac', 0.0)
            right_frac  = get_float(srow, 'right_frac', 0.0)
            axis_diff   = get_float(srow, 'axis_diff', 0.0)
            primary_sec = srow.get('primary_section', '')

            out_rows.append({
                'token': token,
                'total_count': int(total_count),
                'n_folios': int(n_folios),
                'frac_Astronomical': f_ast,
                'frac_Biological': f_bio,
                'frac_Herbal': f_herb,
                'frac_Pharmaceutical': f_phar,
                'frac_Recipes': f_rec,
                'frac_Unassigned': f_unas,
                'frac_Unknown': f_unk,
                'left_frac': left_frac,
                'right_frac': right_frac,
                'axis_diff': axis_diff,
                'primary_section': primary_sec,
            })

    fieldnames = [
        'token',
        'total_count',
        'n_folios',
        'frac_Astronomical',
        'frac_Biological',
        'frac_Herbal',
        'frac_Pharmaceutical',
        'frac_Recipes',
        'frac_Unassigned',
        'frac_Unknown',
        'left_frac',
        'right_frac',
        'axis_diff',
        'primary_section',
    ]

    with open(out_path, 'w', encoding='utf-8', newline='') as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for row in out_rows:
            writer.writerow(row)

    print(f"[OK] Wrote VM semantic-style profiles → {out_path}", file=sys.stderr)

if __name__ == '__main__':
    main()
