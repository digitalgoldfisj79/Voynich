#!/usr/bin/env python3
import os
import re
import csv
from collections import defaultdict, Counter
from math import log2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

TOK_FILE = os.path.join(ROOT, "p6_voynich_tokens.txt")
TRANS_FILE = os.path.join(ROOT, "corpora", "voynich_transliteration.txt")
PROF_FILE = os.path.join(ROOT, "Phase90", "out", "p90_token_profiles.tsv")

OUT_DIR = os.path.join(ROOT, "Phase95", "out")
OUT_TSV = os.path.join(OUT_DIR, "p95_line_metrics.tsv")
OUT_SUMMARY = os.path.join(OUT_DIR, "p95_line_summary.txt")

os.makedirs(OUT_DIR, exist_ok=True)


def load_tokens():
    """Load canonical token stream (one token per line)."""
    tokens = []
    with open(TOK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                tokens.append(t)
    print(f"[INFO] Loaded {len(tokens)} canonical tokens from {TOK_FILE}")
    return tokens


def load_profiles():
    """
    Load token-level profiles from p90_token_profiles.tsv if present.
    Expected columns:
      idx, token, length, freq, H1_local_bits, n_rules, rule_ids, family_signature, best_pmi_partner

    We index by global idx to stay in lockstep with p6_voynich_tokens.txt.
    If file not found, we fall back to minimal metadata.
    """
    profiles = {}
    if not os.path.isfile(PROF_FILE):
        print(f"[WARN] {PROF_FILE} not found; line metrics will omit p90-based fields.")
        return profiles

    with open(PROF_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                idx = int(row.get("idx", "").strip())
            except ValueError:
                continue
            profiles[idx] = row

    print(f"[INFO] Loaded profiles for {len(profiles)} tokens from {PROF_FILE}")
    return profiles


def normalise_token(t):
    """
    Normalise transliteration token to match p6_voynich_tokens.txt conventions.
    Conservative: strip Voynich markup artefacts, trailing punctuation, '?' markers.
    """
    t = t.strip()
    # Drop any inline markup tokens
    if not t or "<" in t or ">" in t:
        return ""

    # Remove common uncertainty markers / punctuation used in some EVAs
    t = t.replace("?", "").replace(",", "").replace(";", "")
    return t


def iterate_transliteration_lines():
    """
    Yield (folio_id, line_id, token_strings[]) from the transliteration file.

    We only use lines with patterns like:
      <f1r.1,*> <...>fachys.ykal.ar.ataiin.shol...
    """
    if not os.path.isfile(TRANS_FILE):
        raise FileNotFoundError(f"Transliteration file not found: {TRANS_FILE}")

    line_re = re.compile(r'^<f(\d+[rv])\.(\d+)[^>]*>\s*(.*)$')

    with open(TRANS_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.rstrip("\n")
            m = line_re.match(raw)
            if not m:
                continue

            folio = m.group(1)
            line_no = m.group(2)
            rest = m.group(3).strip()

            # Remove any inline markup like <%> or <$>
            rest = re.sub(r'<[^>]*>', '', rest)
            if not rest:
                continue

            # Split tokens on '.' as in EVA-style segmented lines
            parts = [p for p in rest.split('.') if p]
            toks = []
            for p in parts:
                nt = normalise_token(p)
                if nt:
                    toks.append(nt)

            if toks:
                yield f"f{folio}", int(line_no), toks


def align_lines_to_tokens(canonical_tokens):
    """
    Align transliteration-derived line tokens to the canonical token stream.

    Returns:
      lines: list of dicts:
        {
          "folio": str,
          "line_no": int,
          "start_idx": int,
          "end_idx": int,   # inclusive
          "idxs": [int, ...]
        }

    Assumes that transliteration and p6_voynich_tokens.txt are globally consistent.
    If mismatches occur, they are reported; alignment proceeds greedily.
    """
    lines = []
    idx = 0
    n = len(canonical_tokens)
    mismatches = 0
    total = 0

    for folio, line_no, toks in iterate_transliteration_lines():
        line_start = idx
        idxs = []
        for t in toks:
            if idx >= n:
                break
            canon = canonical_tokens[idx]

            total += 1
            if canon == t:
                idxs.append(idx)
                idx += 1
                continue

            # Soft normalisation: in case of tiny discrepancies
            c_norm = canon.replace("?", "").replace(",", "").replace(";", "")
            t_norm = t
            if c_norm == t_norm:
                idxs.append(idx)
                idx += 1
            else:
                # Record mismatch but still move on in lockstep
                mismatches += 1
                idxs.append(idx)
                idx += 1

        if idxs:
            lines.append({
                "folio": folio,
                "line_no": line_no,
                "start_idx": idxs[0],
                "end_idx": idxs[-1],
                "idxs": idxs,
            })

    if total > 0:
        print(f"[INFO] Alignment done: {len(lines)} lines mapped.")
        print(f"[INFO] Compared {total} token positions; mismatches: {mismatches} ({(mismatches/total)*100:.2f}%).")
    else:
        print("[WARN] No usable transliteration lines found; no line metrics will be meaningful.")

    return lines


def compute_line_metrics(lines, tokens, profiles):
    """
    For each line, compute structural metrics:

      - n_tokens
      - mean_token_length
      - mean_H1_local_bits (from p90 if available)
      - frac_with_rule (tokens with n_rules > 0)
      - first_token, last_token
      - first_rules, last_rules (comma-separated or '')
    """
    rows = []

    for line in lines:
        idxs = line["idxs"]
        if not idxs:
            continue

        toks = [tokens[i] for i in idxs]
        lengths = [len(t) for t in toks]

        # Local entropy from profiles if present
        h_vals = []
        rule_flags = []
        first_rules = ""
        last_rules = ""

        for j, gi in enumerate(idxs):
            if gi in profiles:
                pr = profiles[gi]
                # H1_local_bits may be missing or empty
                try:
                    hb = float(pr.get("H1_local_bits", "") or "nan")
                    if hb == hb:  # not NaN
                        h_vals.append(hb)
                except ValueError:
                    pass

                try:
                    nr = int(pr.get("n_rules", "") or "0")
                except ValueError:
                    nr = 0
                rule_flags.append(1 if nr > 0 else 0)

                if j == 0:
                    first_rules = pr.get("rule_ids", "") or ""
                if j == len(idxs) - 1:
                    last_rules = pr.get("rule_ids", "") or ""
            else:
                rule_flags.append(0)

        n_tokens = len(idxs)
        mean_len = sum(lengths) / n_tokens if n_tokens else 0.0
        mean_h = sum(h_vals) / len(h_vals) if h_vals else 0.0
        frac_with_rule = sum(rule_flags) / n_tokens if n_tokens else 0.0

        rows.append({
            "folio": line["folio"],
            "line_no": line["line_no"],
            "start_idx": line["start_idx"],
            "end_idx": line["end_idx"],
            "n_tokens": n_tokens,
            "mean_token_length": round(mean_len, 3),
            "mean_H1_local_bits": round(mean_h, 3) if mean_h > 0 else "",
            "frac_with_rule": round(frac_with_rule, 3),
            "first_token": toks[0],
            "last_token": toks[-1],
            "first_rules": first_rules,
            "last_rules": last_rules,
        })

    return rows


def write_tsv(rows, path):
    if not rows:
        print("[WARN] No line metrics to write.")
        return
    fieldnames = [
        "folio",
        "line_no",
        "start_idx",
        "end_idx",
        "n_tokens",
        "mean_token_length",
        "mean_H1_local_bits",
        "frac_with_rule",
        "first_token",
        "last_token",
        "first_rules",
        "last_rules",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[OK] Wrote line metrics → {path}")


def write_summary(rows, path):
    if not rows:
        with open(path, "w", encoding="utf-8") as f:
            f.write("Phase 95: no line metrics (no aligned lines found).\n")
        print(f"[OK] Wrote empty summary → {path}")
        return

    n_lines = len(rows)
    tot_tokens = sum(r["n_tokens"] for r in rows)
    mean_len = sum(r["mean_token_length"] for r in rows) / n_lines
    mean_frac_rules = sum(r["frac_with_rule"] for r in rows) / n_lines

    # Simple per-folio counts
    fol_counts = Counter(r["folio"] for r in rows)

    with open(path, "w", encoding="utf-8") as f:
        f.write("=== Phase 95: Line-level structural metrics ===\n")
        f.write(f"[INFO] Lines analysed: {n_lines}\n")
        f.write(f"[INFO] Tokens covered by aligned lines: {tot_tokens}\n")
        f.write(f"[INFO] Mean tokens per line: {tot_tokens / n_lines:.3f}\n")
        f.write(f"[INFO] Mean token length per line: {mean_len:.3f}\n")
        f.write(f"[INFO] Mean fraction of tokens w/ ≥1 rule per line: {mean_frac_rules:.3f}\n")
        f.write("\n[INFO] Line counts by folio (top 10):\n")
        for fol, c in fol_counts.most_common(10):
            f.write(f"  {fol}: {c}\n")

    print(f"[OK] Summary written → {path}")


def main():
    print("=== Phase 95: Line-level structure ===")
    tokens = load_tokens()
    profiles = load_profiles()
    lines = align_lines_to_tokens(tokens)
    rows = compute_line_metrics(lines, tokens, profiles)
    write_tsv(rows, OUT_TSV)
    write_summary(rows, OUT_SUMMARY)
    print("=== Phase 95 complete ===")


if __name__ == "__main__":
    main()
