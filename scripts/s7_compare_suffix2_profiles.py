#!/usr/bin/env python3
import os
import sys
from collections import defaultdict

def load_suffix_summary(path, label):
    data = {}
    total_tokens = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            if line.startswith("suffix2\t"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            sfx = parts[0]
            try:
                total = int(parts[1])
                n_types = int(parts[2])
                mean_len = float(parts[3])
            except ValueError:
                continue
            data[sfx] = {
                "total": total,
                "n_types": n_types,
                "mean_len": mean_len,
            }
            total_tokens += total
    print(f"[S7c] Loaded {len(data)} suffix2 rows from {path} ({label}), total_tokens={total_tokens}")
    return data, total_tokens

def main():
    base = os.environ.get("BASE")
    if not base:
        print("[ERR] BASE not set", file=sys.stderr)
        sys.exit(1)

    latin_path = os.environ.get("LATIN_SUMMARY", os.path.join(base, "PhaseS", "out", "s6_latin_suffix2_summary.tsv"))
    vm_tok_path = os.environ.get("VM_TOK_SUMMARY", os.path.join(base, "PhaseS", "out", "s7_voynich_suffix2_tokens_summary.tsv"))
    vm_stem_path = os.environ.get("VM_STEM_SUMMARY", os.path.join(base, "PhaseS", "out", "s7_voynich_suffix2_stems_summary.tsv"))
    out_path = os.environ.get("OUT_COMPARE", os.path.join(base, "PhaseS", "out", "s7_suffix2_comparison.tsv"))

    latin, latin_total = load_suffix_summary(latin_path, "latin")
    vm_tok, vm_tok_total = load_suffix_summary(vm_tok_path, "vm_tokens")
    vm_stem, vm_stem_total = load_suffix_summary(vm_stem_path, "vm_stems")

    all_suffixes = set(latin.keys()) | set(vm_tok.keys()) | set(vm_stem.keys())

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as out:
        out.write(
            "suffix2\t"
            "latin_total\tlatin_frac\tlatin_n_types\tlatin_mean_len\t"
            "vm_tok_total\tvm_tok_frac\tvm_tok_n_types\tvm_tok_mean_len\t"
            "vm_stem_total\tvm_stem_frac\tvm_stem_n_types\tvm_stem_mean_len\n"
        )

        for sfx in sorted(all_suffixes):
            lt = latin.get(sfx, {"total": 0, "n_types": 0, "mean_len": 0.0})
            vt = vm_tok.get(sfx, {"total": 0, "n_types": 0, "mean_len": 0.0})
            vs = vm_stem.get(sfx, {"total": 0, "n_types": 0, "mean_len": 0.0})

            lt_total = lt["total"]
            vt_total = vt["total"]
            vs_total = vs["total"]

            latin_frac = lt_total / latin_total if latin_total > 0 else 0.0
            vm_tok_frac = vt_total / vm_tok_total if vm_tok_total > 0 else 0.0
            vm_stem_frac = vs_total / vm_stem_total if vm_stem_total > 0 else 0.0

            out.write(
                f"{sfx}\t"
                f"{lt_total}\t{latin_frac:.6f}\t{lt['n_types']}\t{lt['mean_len']:.4f}\t"
                f"{vt_total}\t{vm_tok_frac:.6f}\t{vt['n_types']}\t{vt['mean_len']:.4f}\t"
                f"{vs_total}\t{vm_stem_frac:.6f}\t{vs['n_types']}\t{vs['mean_len']:.4f}\n"
            )

    print(f"[S7c] Wrote combined suffix2 comparison → {out_path}")

if __name__ == "__main__":
    main()
