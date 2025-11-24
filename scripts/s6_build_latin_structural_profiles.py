#!/usr/bin/env python3
import sys
import os
from collections import Counter, defaultdict

def normalise_token(t):
    letters = [ch for ch in t if ch.isalpha()]
    t2 = "".join(letters).lower()
    return t2

def main():
    if len(sys.argv) != 5:
        print("Usage: s6_build_latin_structural_profiles.py "
              "<latin_tokens.txt> <out_token_freq.tsv> "
              "<out_suffix2_summary.tsv> <out_global_summary.tsv>",
              file=sys.stderr)
        sys.exit(1)

    latin_path, out_tokens, out_suffix2, out_global = sys.argv[1:]

    if not os.path.isfile(latin_path):
        print(f"[ERR] Latin token file not found: {latin_path}", file=sys.stderr)
        sys.exit(1)

    token_counts = Counter()
    length_counts = Counter()
    suffix2_counts = Counter()
    suffix2_type_set = defaultdict(set)

    total_raw_lines = 0
    total_tokens = 0

    with open(latin_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            total_raw_lines += 1
            t = line.strip()
            if not t:
                continue
            t_norm = normalise_token(t)
            if not t_norm:
                continue

            token_counts[t_norm] += 1
            total_tokens += 1

            L = len(t_norm)
            length_counts[L] += 1

            if L >= 2:
                s2 = t_norm[-2:]
            else:
                s2 = t_norm
            suffix2_counts[s2] += 1
            suffix2_type_set[s2].add(t_norm)

    total_types = len(token_counts)

    # token frequency table
    os.makedirs(os.path.dirname(out_tokens), exist_ok=True)
    with open(out_tokens, "w", encoding="utf-8") as f_out:
        f_out.write("token\ttotal_count\tlength\tsuffix2\n")
        for tok, cnt in sorted(token_counts.items(), key=lambda x: (-x[1], x[0])):
            L = len(tok)
            s2 = tok[-2:] if L >= 2 else tok
            f_out.write(f"{tok}\t{cnt}\t{L}\t{s2}\n")

    # suffix2 summary
    with open(out_suffix2, "w", encoding="utf-8") as f_out:
        f_out.write("suffix2\ttotal_count\tn_types\tmean_len\n")
        for s2, cnt in sorted(suffix2_counts.items(), key=lambda x: (-x[1], x[0])):
            types = suffix2_type_set[s2]
            n_types = len(types)
            if n_types > 0:
                mean_len = sum(len(t) for t in types) / n_types
            else:
                mean_len = 0.0
            f_out.write(f"{s2}\t{cnt}\t{n_types}\t{mean_len:.4f}\n")

    # global summary
    vowels = set("aeiouy")
    vowel_final = 0
    consonant_final = 0
    for tok, cnt in token_counts.items():
        if tok[-1] in vowels:
            vowel_final += cnt
        else:
            consonant_final += cnt

    with open(out_global, "w", encoding="utf-8") as f_out:
        f_out.write("metric\tvalue\n")
        f_out.write(f"total_raw_lines\t{total_raw_lines}\n")
        f_out.write(f"total_tokens\t{total_tokens}\n")
        f_out.write(f"total_types\t{total_types}\n")
        f_out.write(f"vowel_final_tokens\t{vowel_final}\n")
        f_out.write(f"consonant_final_tokens\t{consonant_final}\n")
        total_final = vowel_final + consonant_final
        if total_final == 0:
            frac_vowel = 0.0
            frac_cons = 0.0
        else:
            frac_vowel = vowel_final / total_final
            frac_cons = consonant_final / total_final
        f_out.write(f"frac_vowel_final\t{frac_vowel:.6f}\n")
        f_out.write(f"frac_consonant_final\t{frac_cons:.6f}\n")

        for L in sorted(length_counts.keys()):
            f_out.write(f"length_{L}\t{length_counts[L]}\n")

    print(f"[OK] Processed {total_tokens} tokens")
    print(f"[OK] Wrote → {out_tokens}")
    print(f"[OK] Wrote → {out_suffix2}")
    print(f"[OK] Wrote → {out_global}")

if __name__ == "__main__":
    main()
