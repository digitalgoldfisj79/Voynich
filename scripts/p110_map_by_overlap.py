# scripts/p110_map_by_overlap.py
import sys, pandas as pd

def parse_set(s):
    return tuple(sorted([t for t in s.strip().split('-') if t]))

def jaccard(a, b):
    A, B = set(a), set(b)
    if not A and not B: return 1.0
    return len(A & B) / len(A | B) if (A|B) else 0.0

def main():
    if len(sys.argv) != 4:
        print("usage: python3 p110_map_by_overlap.py <p112_attribution.tsv> <p77_family_section.tsv> <out_map.tsv>")
        sys.exit(1)
    attr_path, p77_path, out_path = sys.argv[1:4]
    A = pd.read_csv(attr_path, sep='\t')
    P = pd.read_csv(p77_path, sep='\t')

    A['fam_set'] = A['family'].astype(str).apply(parse_set)
    P['fam_set'] = P['family'].astype(str).apply(parse_set)

    # pre-index Phase77 sets
    P_list = P[['family','section','fam_set']].values.tolist()

    rows = []
    for _, r in A.iterrows():
        f110 = r['family']
        s110 = r['fam_set']
        best = (None, None, 0.0)
        for f77, sec, s77 in P_list:
            score = jaccard(s110, s77)
            if score > best[2]:
                best = (f77, sec, score)
        rows.append({
            'family_110': f110,
            'mapped_family_77': best[0],
            'section': best[1],
            'overlap': best[2]
        })
    out = pd.DataFrame(rows)
    # keep only sufficiently strong matches
    out = out[(out['mapped_family_77'].notna()) & (out['overlap'] >= 0.6)]
    out.to_csv(out_path, sep='\t', index=False)
    print(f"[OK] Wrote overlap map → {out_path}")
    print(f"[INFO] Matches kept (overlap≥0.6): {len(out)}")

if __name__ == "__main__":
    main()
