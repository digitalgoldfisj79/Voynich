#!/usr/bin/env python3
import sys
import math

def load_suffix_summary(path, label):
    """
    Load a suffix2 summary TSV with at least:
      suffix2, total_count
    Returns (counts_dict, total_tokens).
    """
    counts = {}
    total = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            header = f.readline().rstrip("\n").split("\t")
            try:
                idx_suf = header.index("suffix2")
                idx_cnt = header.index("total_count")
            except ValueError:
                raise SystemExit(
                    f"[ERROR] {label}: expected columns 'suffix2' and 'total_count' "
                    f"in header: {header}"
                )
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) <= max(idx_suf, idx_cnt):
                    continue
                suf = parts[idx_suf]
                try:
                    cnt = int(parts[idx_cnt])
                except ValueError:
                    continue
                counts[suf] = counts.get(suf, 0) + cnt
                total += cnt
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] {label}: file not found: {path}")
    if total == 0:
        raise SystemExit(f"[ERROR] {label}: no tokens loaded from {path}")
    return counts, total

def to_probs(counts, total, keys):
    """Return probability vector over `keys` with Laplace smoothing to avoid JS issues."""
    # Laplace smoothing: add 1 to every bin
    k = len(keys)
    probs = []
    denom = total + k  # total + 1 per key
    for k_ in keys:
        c = counts.get(k_, 0) + 1
        probs.append(c / denom)
    return probs

def js_divergence(p, q):
    """Jensen–Shannon divergence between two distributions p and q."""
    if len(p) != len(q):
        raise ValueError("Probability vectors must have same length")
    m = [(pi + qi) / 2.0 for pi, qi in zip(p, q)]

    def kl(a, b):
        s = 0.0
        for ai, bi in zip(a, b):
            if ai > 0.0 and bi > 0.0:
                s += ai * math.log(ai / bi)
        return s

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

def main():
    if len(sys.argv) != 5:
        sys.stderr.write(
            "Usage: s6_compare_materia_dante_voynich.py "
            "<materia_suffix2.tsv> <dante_suffix2.tsv> "
            "<voynich_suffix2_stems.tsv> <out.tsv>\n"
        )
        sys.exit(1)

    materia_path = sys.argv[1]
    dante_path   = sys.argv[2]
    vm_path      = sys.argv[3]
    out_path     = sys.argv[4]

    # Load the three suffix2 profiles
    materia, tot_m = load_suffix_summary(materia_path, "materia")
    dante,   tot_d = load_suffix_summary(dante_path,   "dante")
    vm,      tot_v = load_suffix_summary(vm_path,      "voynich")

    # Common key set: union of all suffix2s
    keys = sorted(set(materia.keys()) | set(dante.keys()) | set(vm.keys()))

    p_m = to_probs(materia, tot_m, keys)
    p_d = to_probs(dante,   tot_d, keys)
    p_v = to_probs(vm,      tot_v, keys)

    js_m_d = js_divergence(p_m, p_d)
    js_m_v = js_divergence(p_m, p_v)
    js_d_v = js_divergence(p_d, p_v)

    sys.stderr.write(
        f"[S6-MDV] total_tokens: materia={tot_m}, dante={tot_d}, voynich={tot_v}\n"
    )
    sys.stderr.write(f"[S6-MDV] JS(materia || dante)  = {js_m_d:.6f}\n")
    sys.stderr.write(f"[S6-MDV] JS(materia || voynich)= {js_m_v:.6f}\n")
    sys.stderr.write(f"[S6-MDV] JS(dante   || voynich)= {js_d_v:.6f}\n")

    # Write combined table
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(
            "suffix2\t"
            "materia_total\tmateria_frac\t"
            "dante_total\tdante_frac\t"
            "vm_total\tvm_frac\t"
            "abs_diff_m_d\tabs_diff_m_v\tabs_diff_d_v\n"
        )
        for suf in keys:
            cm = materia.get(suf, 0)
            cd = dante.get(suf,   0)
            cv = vm.get(suf,      0)
            fm = cm / tot_m
            fd = cd / tot_d
            fv = cv / tot_v
            out.write(
                f"{suf}\t"
                f"{cm}\t{fm:.8f}\t"
                f"{cd}\t{fd:.8f}\t"
                f"{cv}\t{fv:.8f}\t"
                f"{abs(fm-fd):.8f}\t"
                f"{abs(fm-fv):.8f}\t"
                f"{abs(fd-fv):.8f}\n"
            )

    sys.stderr.write(f"[S6-MDV] Wrote combined table → {out_path}\n")

if __name__ == "__main__":
    main()
