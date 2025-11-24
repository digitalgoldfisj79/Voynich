#!/usr/bin/env python3
import os
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P_TOKENS          = os.path.join(BASE, "p6_voynich_tokens.txt")
P_RULEBOOK        = os.path.join(BASE, "Phase69", "out", "p69_rules_final.json")
P_PMI             = os.path.join(BASE, "Phase72", "out", "p72_rule_pmi_network.tsv")
P_SUMMARY73       = os.path.join(BASE, "Phase73", "out", "p73_summary_metrics.txt")

P_TOK_RULES       = os.path.join(BASE, "Phase74", "out", "p74_token_rules.tsv")
P_RULE_COMS       = os.path.join(BASE, "Phase75", "out", "p75_rule_communities.tsv")
P_TOK_COMS        = os.path.join(BASE, "Phase76", "out", "p76_token_communities.tsv")
P_ANCHORS         = os.path.join(BASE, "Phase77", "out", "p77_anchor_candidates.tsv")


def exists(path, label):
    if not os.path.isfile(path):
        print(f"[MISS] {label}: {path} not found")
        return False
    print(f"[OK]   {label}: {path}")
    return True


def count_tokens(path):
    n = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line and not line.startswith("#"):
                n += 1
    return n


def load_rulebook(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rules = [r for r in data if isinstance(r, dict)]
    return rules


def quick_preview(path, n=5):
    if not os.path.isfile(path):
        return
    print(f"  [head] {os.path.relpath(path, BASE)}")
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            print("    " + line.rstrip())
            if i+1 >= n:
                break


def main():
    print("=== Phase 78: Pipeline Validation ===")

    # 1. Core inputs
    ok_tokens   = exists(P_TOKENS,    "Canonical tokens")
    ok_rules    = exists(P_RULEBOOK,  "Phase69 rulebook")
    ok_pmi      = exists(P_PMI,       "Rule PMI network (Phase72)")
    ok_sum73    = exists(P_SUMMARY73, "Phase73 summary metrics")

    if ok_tokens:
        n_tok = count_tokens(P_TOKENS)
        print(f"[INFO] Canonical Voynich tokens: {n_tok}")
        if n_tok < 20000 or n_tok > 40000:
            print("[WARN] Unexpected token count; expected ~29,688.")

    if ok_rules:
        rules = load_rulebook(P_RULEBOOK)
        print(f"[INFO] Phase69 rules in JSON: {len(rules)} total")
        # quick sanity on structure
        bad = sum(1 for r in rules if not isinstance(r, dict))
        if bad:
            print(f"[WARN] {bad} non-dict entries in rulebook JSON.")
        # count that look like real patterns
        pat_like = sum(1 for r in rules if r.get("pattern") or r.get("pre") or r.get("suf"))
        print(f"[INFO] Usable rules with pattern/pre/suf: {pat_like}")

    # 2. PMI / summary cross-check (if present)
    if ok_pmi:
        edges = 0
        nodes = set()
        with open(P_PMI, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip() or line.startswith("#"):
                    continue
                a,b,fi,fj,cooc,pmi = line.strip().split("\t")
                edges += 1
                nodes.add(a)
                nodes.add(b)
        print(f"[INFO] PMI network: {len(nodes)} rule-nodes, {edges} edges")

    if ok_sum73:
        print("[INFO] Phase73 summary (verbatim):")
        with open(P_SUMMARY73, "r", encoding="utf-8") as f:
            for line in f:
                print("   ", line.rstrip())

    # 3. Token→rule mapping
    tr_ok = exists(P_TOK_RULES, "Phase74 token→rules")
    if tr_ok:
        total_rows = 0
        unique_tokens = set()
        tokens_with_rules = set()
        rule_hits = {}
        with open(P_TOK_RULES, "r", encoding="utf-8") as f:
            header = f.readline()
            for line in f:
                if not line.strip():
                    continue
                total_rows += 1
                idx, tok, rules_csv = line.strip().split("\t")
                unique_tokens.add(tok)
                if rules_csv:
                    tokens_with_rules.add(tok)
                    for rid in rules_csv.split(","):
                        rule_hits[rid] = rule_hits.get(rid, 0) + 1

        print(f"[INFO] Phase74 rows: {total_rows}")
        print(f"[INFO] Unique tokens w/ ≥1 rule: {len(tokens_with_rules)}")
        if ok_tokens:
            cov = (len(tokens_with_rules) / float(n_tok)) * 100.0
            print(f"[INFO] Approx token-level rule coverage: {cov:.2f}%")
        print(f"[INFO] Rules that fired at least once: {len(rule_hits)}")
        print("  [top 5 rules by hits]:")
        for rid, c in sorted(rule_hits.items(), key=lambda x: -x[1])[:5]:
            print(f"    rule {rid}: {c} hits")
        quick_preview(P_TOK_RULES)

    # 4. Rule communities
    rc_ok = exists(P_RULE_COMS, "Phase75 rule communities")
    if rc_ok:
        com_counts = {}
        with open(P_RULE_COMS, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip() or line.startswith("rule_label"):
                    continue
                _, com = line.strip().split("\t")
                com_counts[com] = com_counts.get(com, 0) + 1
        print("[INFO] Rule communities:")
        for com, c in sorted(com_counts.items(), key=lambda x: x[0]):
            print(f"   {com}: {c} rules")
        quick_preview(P_RULE_COMS)

    # 5. Token communities
    tc_ok = exists(P_TOK_COMS, "Phase76 token communities")
    if tc_ok:
        total = 0
        tokens = set()
        with open(P_TOK_COMS, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip() or line.startswith("idx"):
                    continue
                total += 1
                _, tok, _ = line.strip().split("\t")
                tokens.add(tok)
        print(f"[INFO] Phase76: {total} rows, {len(tokens)} unique tokens with community labels")
        if ok_tokens:
            print(f"[INFO] Fraction of corpus tokens w/ community label (rough): "
                  f"{(len(tokens)/float(n_tok))*100:.2f}%")
        quick_preview(P_TOK_COMS)

    # 6. Anchor candidates
    ac_ok = exists(P_ANCHORS, "Phase77 anchor candidates")
    if ac_ok:
        per_com = {}
        with open(P_ANCHORS, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip() or line.startswith("community"):
                    continue
                com, tok, cnt = line.strip().split("\t")
                cnt = int(cnt)
                per_com.setdefault(com, []).append((tok, cnt))

        print("[INFO] Anchor candidates per community (top few):")
        for com in sorted(per_com.keys()):
            top = sorted(per_com[com], key=lambda x: -x[1])[:5]
            print(f"  {com}: " + ", ".join(f"{t}({c})" for t,c in top))
        quick_preview(P_ANCHORS)

    print("=== Phase 78 validation complete ===")


if __name__ == "__main__":
    main()
