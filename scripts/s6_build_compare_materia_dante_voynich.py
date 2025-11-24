#!/usr/bin/env python3
import sys, math

def load_suffix_summary(path):
    """
    Expect a TSV with at least: suffix2, total_count
    (like the *_suffix2_summary.tsv files).
    Returns: (counts_dict, total_tokens)
    """
    counts = {}
    total_tokens = 0
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            idx_suffix = header.index("suffix2")
            idx_count  = header.index("total_count")
        except ValueError as e:
            raise SystemExit(f"[ERR] {path} missing required columns: {e}")

        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= max(idx_suffix, idx_count):
                continue
            suffix = parts[idx_suffix]
            try:
                cnt = int(parts[idx_count])
            except ValueError:
                continue
            counts[suffix] = counts.get(suffix, 0) + cnt
            total_tokens += cnt
    return counts, total_tokens

def js_divergence(p, q):
    """
    Jensen–Shannon divergence between two distributions p, q
    given as dicts of probabilities over the same support.
    """
    keys = set(p.keys()) | set(q.keys())
    m = {}
    for k in keys:
        pk = p.get(k, 0.0)
        qk = q.get(k, 0.0)
        m[k] = 0.5 * (pk + qk)

    def kl(a, b):
        s = 0.0
        for k in keys:
            ak = a.get(k, 0.0)
            bk = b.get(k, 0.0)
            if ak > 0.0 and bk > 0.0:
                s += ak * math.log(ak / bk, 2.0)
        return s

    return 0.5 * (kl(p, m) + kl(q, m))

def main():
    if len(sys.argv) != 5:
        print("Usage: s6_build_compare_materia_dante_voynich.py "
              "<materia_suffix2.tsv> <dante_suffix2.tsv> "
              "<vm_stem_suffix2.tsv> <out.tsv>")
        sys.exit(1)

    materia_path = sys.argv[1]
    dante_path   = sys.argv[2]
    vm_path      = sys.argv[3]
    out_path     = sys.argv[4]

    # Load counts
    materia_counts, materia_total = load_suffix_summary(materia_path)
    dante_counts,   dante_total   = load_suffix_summary(dante_path)
    vm_counts,      vm_total      = load_suffix_summary(vm_path)

    print(f"[S6-MDV] total_tokens: materia={materia_total}, "
          f"dante={dante_total}, voynich={vm_total}")

    # Build probability distributions for JS divergence
    all_suffixes = set(materia_counts.keys()) | set(dante_counts.keys()) | set(vm_counts.keys())

    materia_p = {s: materia_counts.get(s, 0) / materia_total for s in all_suffixes}
    dante_p   = {s: dante_counts.get(s, 0)   / dante_total   for s in all_suffixes}
    vm_p      = {s: vm_counts.get(s, 0)      / vm_total      for s in all_suffixes}

    js_materia_dante = js_divergence(materia_p, dante_p)
    js_materia_vm    = js_divergence(materia_p, vm_p)
    js_dante_vm      = js_divergence(dante_p, vm_p)

    print(f"[S6-MDV] JS(materia || dante)  = {js_materia_dante:.6f}")
    print(f"[S6-MDV] JS(materia || voynich)= {js_materia_vm:.6f}")
    print(f"[S6-MDV] JS(dante   || voynich)= {js_dante_vm:.6f}")

    # Write combined table
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(
            "suffix2\t"
            "mater_total\tmater_frac\t"
            "dante_total\tdante_frac\t"
            "vm_total\tvm_frac\t"
            "abs_diff_mater_dante\t"
            "abs_diff_mater_vm\t"
            "abs_diff_dante_vm\n"
        )

        for s in sorted(all_suffixes):
            m_cnt = materia_counts.get(s, 0)
            d_cnt = dante_counts.get(s, 0)
            v_cnt = vm_counts.get(s, 0)

            mater_frac = m_cnt / materia_total if materia_total > 0 else 0.0
            dante_frac = d_cnt / dante_total   if dante_total   > 0 else 0.0
            vm_frac    = v_cnt / vm_total      if vm_total      > 0 else 0.0

            diff_md = abs(mater_frac - dante_frac)
            diff_mv = abs(mater_frac - vm_frac)
            diff_dv = abs(dante_frac - vm_frac)

            out.write(
                f"{s}\t"
                f"{m_cnt}\t{mater_frac:.8f}\t"
                f"{d_cnt}\t{dante_frac:.8f}\t"
                f"{v_cnt}\t{vm_frac:.8f}\t"
                f"{diff_md:.8f}\t"
                f"{diff_mv:.8f}\t"
                f"{diff_dv:.8f}\n"
            )

    print(f"[S6-MDV] Wrote combined table → {out_path}")

if __name__ == "__main__":
    main()
