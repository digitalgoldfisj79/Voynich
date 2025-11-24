#!/usr/bin/env python3
import sys
import csv
import math
from collections import defaultdict

def read_tsv(path):
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.reader(f, delimiter='\t'))

def euclid(a, b):
    return math.sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

def norm_folio(fid):
    """
    Normalise folio IDs so that e.g. 'f1r', 'F01R', '1r' all map to '1r'.
    """
    if not fid:
        return ""
    s = fid.strip().lower()
    # strip leading 'f'
    if s.startswith('f'):
        s = s[1:]
    # strip leading zeros before the side marker
    i = 0
    while i < len(s) and s[i] == '0':
        i += 1
    s = s[i:] if i < len(s) else ""
    return s

def extract_folio_from_meta(meta):
    """
    p6_folio_tokens.tsv has:
      token, folio_meta, line, pos

    folio_meta looks like:
      'f1r>      <! $Q=A $P=A ...'

    We want the 'f1r'.
    """
    if not meta:
        return ""
    s = meta.strip()
    # split at '>' first if present
    if '>' in s:
        s = s.split('>', 1)[0]
    # then cut at first whitespace if any
    s = s.split()[0]
    return s

def main():
    if len(sys.argv) != 6:
        print("Usage: s4_build_stem_structural_vectors.py <types_vectors> <folio_tokens> <folio_sections> <section_summary> <out_prefix>")
        sys.exit(1)

    types_path = sys.argv[1]
    folio_tokens_path = sys.argv[2]
    folio_sections_path = sys.argv[3]
    section_summary_path = sys.argv[4]
    out_prefix = sys.argv[5]

    # --- 1) Load type-level structural vectors (from p71) ---
    type_rows = read_tsv(types_path)
    if not type_rows:
        print(f"[ERR] Empty type vector file: {types_path}")
        sys.exit(1)

    type_struct = {}  # token -> feature vector
    for r in type_rows[1:]:
        if not r:
            continue
        tok = r[0]
        if not tok:
            continue
        if len(r) < 8:
            continue
        try:
            feats = [float(x) for x in r[-7:]]
        except ValueError:
            continue
        type_struct[tok] = feats

    print(f"[INFO] Loaded structural features for {len(type_struct)} token types from {types_path}")

    # --- 2) Load section centroids (from S2) ---
    sec_rows = read_tsv(section_summary_path)
    if not sec_rows:
        print(f"[ERR] Empty section summary file: {section_summary_path}")
        sys.exit(1)

    centroids = {}
    sections = []
    for r in sec_rows[1:]:
        if not r:
            continue
        sec = r[0]
        try:
            feats = [float(x) for x in r[-7:]]
        except ValueError:
            continue
        centroids[sec] = feats
        sections.append(sec)

    print(f"[INFO] Loaded centroids for {len(centroids)} sections from {section_summary_path}")

    # --- 3) Load folio→section mapping, normalised ---
    fs_rows = read_tsv(folio_sections_path)
    if not fs_rows:
        print(f"[ERR] Empty folio_sections file: {folio_sections_path}")
        sys.exit(1)

    def is_fs_header(row):
        if not row:
            return False
        s0 = row[0].lower()
        return ("folio" in s0) or (s0 == "f")

    start_idx = 1 if is_fs_header(fs_rows[0]) else 0
    folio_to_section = {}
    for r in fs_rows[start_idx:]:
        if len(r) < 2:
            continue
        raw_folio = r[0]
        sec = r[1]
        if not raw_folio or not sec:
            continue
        nf = norm_folio(raw_folio)
        if not nf:
            continue
        folio_to_section.setdefault(nf, sec)

    print(f"[INFO] Loaded {len(folio_to_section)} normalised folio→section mappings from {folio_sections_path}")

    # --- 4) Load folio tokens, using extracted + normalised folio IDs ---
    ft_rows = read_tsv(folio_tokens_path)
    if not ft_rows:
        print(f"[ERR] Empty folio token file: {folio_tokens_path}")
        sys.exit(1)

    # p6_folio_tokens.tsv has no header; treat all lines as data
    data_rows = ft_rows

    token_total = defaultdict(int)
    token_folios = defaultdict(set)
    token_sections = defaultdict(lambda: defaultdict(int))

    missing_folio_sec = 0
    seen_norm_ids = set()

    for r in data_rows:
        if len(r) < 4:
            continue
        tok = r[0]
        folio_meta = r[1]
        if not tok or not folio_meta:
            continue

        raw_folio = extract_folio_from_meta(folio_meta)
        if not raw_folio:
            missing_folio_sec += 1
            continue

        nf = norm_folio(raw_folio)
        if not nf:
            missing_folio_sec += 1
            continue

        sec = folio_to_section.get(nf)
        if sec is None:
            missing_folio_sec += 1
            continue

        seen_norm_ids.add(nf)
        token_total[tok] += 1
        token_folios[tok].add(raw_folio)
        token_sections[tok][sec] += 1

    print(f"[INFO] Counted tokens for {len(token_total)} token forms that matched a normalised folio ID")
    print(f"[INFO] Normalised folios actually used: {len(seen_norm_ids)}")
    if missing_folio_sec > 0:
        print(f"[WARN] {missing_folio_sec} token rows had no matching normalised folio→section mapping; skipped")

    # --- 5) Build stem structural tables ---
    out_main_path = out_prefix + "_stem_structural_vectors.tsv"
    out_dist_path = out_prefix + "_stem_section_distribution.tsv"

    main_header = [
        "token", "total_count", "n_folios", "n_sections",
        "left_frac", "right_frac", "unknown_frac",
        "left_score", "right_score", "rule_hits", "axis_diff",
        "primary_section"
    ]
    for sec in sections:
        main_header.append(f"dist_{sec}")

    dist_header = ["token", "total_count", "n_folios"]
    for sec in sections:
        dist_header.append(f"count_{sec}")

    n_written = 0

    with open(out_main_path, 'w', encoding='utf-8') as f_main, \
         open(out_dist_path, 'w', encoding='utf-8') as f_dist:

        f_main.write("\t".join(main_header) + "\n")
        f_dist.write("\t".join(dist_header) + "\n")

        for tok, feats in type_struct.items():
            total = token_total.get(tok, 0)
            if total == 0:
                continue

            folios = token_folios.get(tok, set())
            n_folios = len(folios)
            sec_counts = token_sections.get(tok, {})

            n_secs = len([s for s, c in sec_counts.items() if c > 0])

            primary = ""
            if sec_counts:
                primary = sorted(sec_counts.items(), key=lambda x: (-x[1], x[0]))[0][0]

            if len(feats) != 7:
                continue
            left_frac, right_frac, unknown_frac, left_score, right_score, rule_hits, axis_diff = feats

            dists = []
            for sec in sections:
                cvec = centroids.get(sec)
                if cvec is None or len(cvec) != len(feats):
                    d = ""
                else:
                    d = euclid(feats, cvec)
                dists.append(d)

            main_row = [
                tok,
                str(total),
                str(n_folios),
                str(n_secs),
                f"{left_frac:.6f}",
                f"{right_frac:.6f}",
                f"{unknown_frac:.66f}",
                f"{left_score:.6f}",
                f"{right_score:.6f}",
                f"{rule_hits:.6f}",
                f"{axis_diff:.6f}",
                primary
            ]
            for d in dists:
                if d == "":
                    main_row.append("")
                else:
                    main_row.append(f"{d:.6f}")

            f_main.write("\t".join(main_row) + "\n")

            dist_row = [tok, str(total), str(n_folios)]
            for sec in sections:
                dist_row.append(str(sec_counts.get(sec, 0)))
            f_dist.write("\t".join(dist_row) + "\n")

            n_written += 1

    print(f"[OK] Wrote {n_written} token structural rows   → {out_main_path}")
    print(f"[OK] Wrote section distributions for {n_written} tokens → {out_dist_path}")

if __name__ == "__main__":
    main()
