#!/usr/bin/env python3
"""
p90_token_profiles.py

Build per-token structural profiles using:
- Canonical Voynich tokens (p6_voynich_tokens.txt)
- Phase 69 rulebook (p69_rules_final.json)
- Rule–rule PMI network (Phase73/out/p73_rule_pmi.tsv)

For each token we report:
- idx                 (0-based index in corpus)
- token
- length
- freq                (global frequency)
- H1_local_bits       = log2(N / freq)
- n_rules             (number of matching chargram rules)
- rule_ids            (comma-separated rule_ids matched)
- family_signature    (sorted unique patterns, '-' joined)
- best_pmi_partner    (rule_id of strongest PMI-linked partner for first hit rule)

This version:
- Computes hits directly from the rulebook (ignores any legacy encodings).
- Uses only concrete chargram rules with non-empty patterns.
- Reads PMI_bits from the Phase73 file if present; otherwise falls back gracefully.
"""

import os
import json
import math
import csv

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, ".."))

TOKENS_PATH = os.path.join(ROOT, "p6_voynich_tokens.txt")
RULEBOOK_PATH = os.path.join(ROOT, "Phase69", "out", "p69_rules_final.json")
PMI_PATH = os.path.join(ROOT, "Phase73", "out", "p73_rule_pmi.tsv")
OUT_DIR = os.path.join(ROOT, "Phase90", "out")
OUT_PATH = os.path.join(OUT_DIR, "p90_token_profiles.tsv")


def load_tokens(path):
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if not t:
                continue
            # allow for possible "idx<TAB>token" formats; keep last field
            parts = t.split()
            tok = parts[-1]
            tokens.append(tok)
    return tokens


def load_rulebook(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Accept either {"rules":[...]} or [...] formats
    if isinstance(data, dict) and "rules" in data:
        rules = data["rules"]
    elif isinstance(data, list):
        rules = data
    else:
        raise ValueError("Unrecognised rulebook JSON structure")

    chargram_rules = []
    for r in rules:
        kind = r.get("kind", "")
        rule_id = r.get("rule_id", "")
        pattern = r.get("pattern", "")
        side = r.get("pred_side", r.get("side", "any"))

        if not pattern:
            continue

        # restrict to explicit chargram-like rules
        if kind == "chargram" or rule_id.startswith("chargram:"):
            side = (side or "any").lower()
            if side not in ("left", "right", "any"):
                side = "any"
            chargram_rules.append(
                {
                    "rule_id": rule_id,
                    "pattern": pattern,
                    "side": side,
                }
            )

    return chargram_rules


def match_rules_to_token(token, rules):
    """Return list of rule_ids whose pattern matches token under side constraint."""
    hits = []
    for r in rules:
        pat = r["pattern"]
        side = r["side"]
        if side == "left":
            if token.startswith(pat):
                hits.append(r["rule_id"])
        elif side == "right":
            if token.endswith(pat):
                hits.append(r["rule_id"])
        else:  # any
            if pat in token:
                hits.append(r["rule_id"])
    return hits


def load_pmi_partners(path):
    """
    Build mapping rule_id -> best_PMI_partner_rule_id
    from Phase73/out/p73_rule_pmi.tsv.

    Expected columns: rule_i, rule_j, PMI_bits (case-insensitive).
    Falls back silently if file or columns missing.
    """
    pmimap = {}

    if not os.path.isfile(path):
        print(f"[WARN] PMI file not found: {path} (best_pmi_partner will be empty)")
        return pmimap

    df = pd.read_csv(path, sep="\t")

    # normalise column names
    cols = {c.lower(): c for c in df.columns}
    if "pmi_bits" in cols:
        pmi_col = cols["pmi_bits"]
    elif "pmi" in cols:
        pmi_col = cols["pmi"]
    else:
        print("[WARN] No PMI column found in p73_rule_pmi.tsv (expected 'PMI_bits'); partners disabled.")
        return pmimap

    if "rule_i" not in df.columns or "rule_j" not in df.columns:
        print("[WARN] Missing rule_i/rule_j columns in p73_rule_pmi.tsv; partners disabled.")
        return pmimap

    # sort by PMI descending so first assignment is strongest
    df = df.sort_values(pmi_col, ascending=False)

    for _, row in df.iterrows():
        a = str(row["rule_i"])
        b = str(row["rule_j"])
        if a not in pmimap:
            pmimap[a] = b
        if b not in pmimap:
            pmimap[b] = a

    return pmimap


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Load tokens
    if not os.path.isfile(TOKENS_PATH):
        raise SystemExit(f"[ERR] Tokens file not found: {TOKENS_PATH}")
    tokens = load_tokens(TOKENS_PATH)
    N = len(tokens)
    if N == 0:
        raise SystemExit("[ERR] No tokens loaded.")
    print(f"[INFO] Loaded {N} tokens from {TOKENS_PATH}")

    # 2. Frequencies and local H1
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1

    # 3. Load chargram rules
    if not os.path.isfile(RULEBOOK_PATH):
        raise SystemExit(f"[ERR] Rulebook not found: {RULEBOOK_PATH}")
    chargram_rules = load_rulebook(RULEBOOK_PATH)
    if not chargram_rules:
        print("[WARN] No chargram rules found in rulebook.")
    else:
        print(f"[INFO] Loaded {len(chargram_rules)} chargram rules from rulebook.")

    # 4. Load PMI partners
    pmimap = load_pmi_partners(PMI_PATH)
    if pmimap:
        print(f"[INFO] Loaded PMI partners for {len(pmimap)} rules.")
    else:
        print("[INFO] No PMI partners available (best_pmi_partner will be blank).")

    # 5. Build profiles
    out_rows = []
    tokens_with_hits = 0

    for idx, tok in enumerate(tokens):
        f = freq[tok]
        # local information content: log2(N / f)
        H1_local = math.log2(N / f)

        # find matching rules
        hits = match_rules_to_token(tok, chargram_rules)
        n_rules = len(hits)

        if n_rules > 0:
            tokens_with_hits += 1

        # family_signature: sorted unique rule_ids (or underlying patterns)
        # To keep it concrete and reproducible, we use rule_ids directly.
        uniq_hits = sorted(set(hits))
        family_signature = "-".join(uniq_hits) if uniq_hits else ""

        # best_pmi_partner: choose for the first hit (if PMI map exists)
        best_partner = ""
        for rid in uniq_hits:
            if rid in pmimap:
                best_partner = pmimap[rid]
                break

        out_rows.append(
            {
                "idx": idx,
                "token": tok,
                "length": len(tok),
                "freq": f,
                "H1_local_bits": round(H1_local, 6),
                "n_rules": n_rules,
                "rule_ids": ",".join(uniq_hits),
                "family_signature": family_signature,
                "best_pmi_partner": best_partner,
            }
        )

    # 6. Write TSV
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "idx",
                "token",
                "length",
                "freq",
                "H1_local_bits",
                "n_rules",
                "rule_ids",
                "family_signature",
                "best_pmi_partner",
            ]
        )
        for row in out_rows:
            writer.writerow(
                [
                    row["idx"],
                    row["token"],
                    row["length"],
                    row["freq"],
                    f"{row['H1_local_bits']:.6f}",
                    row["n_rules"],
                    row["rule_ids"],
                    row["family_signature"],
                    row["best_pmi_partner"],
                ]
            )

    # 7. Summary
    print(f"[OK] Wrote token profiles → {OUT_PATH}")
    print(f"[INFO] {N} tokens profiled.")
    print(f"[INFO] {tokens_with_hits} tokens with ≥1 chargram rule hit "
          f"({tokens_with_hits / N * 100:.2f} %).")


if __name__ == "__main__":
    main()
