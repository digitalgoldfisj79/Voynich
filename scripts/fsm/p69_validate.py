#!/usr/bin/env python3
import os, csv, json, hashlib, statistics as stats
from collections import defaultdict, Counter

# ---- Inputs (defaults point to 67.5 outputs + earlier phases) ----
RULES_TSV = os.path.expanduser('~/Voynich/Phase67p/out/p67p_rules_compact.tsv')
SEGMENTS  = os.path.expanduser('~/Voynich/Phase58/out/p58_segments.tsv')         # with columns: stem,section,axis1,axis2,axis3
OUTDIR    = os.path.expanduser('~/Voynich/Phase69/out')
FINAL_TSV = os.path.join(OUTDIR, 'p69_rules_final.tsv')
FINAL_JSON= os.path.join(OUTDIR, 'p69_rules_final.json')
SUMMARY   = os.path.join(OUTDIR, 'p69_summary.json')
DOC_MD    = os.path.join(OUTDIR, 'p69_doc.md')

SECTIONS = ["Herbal","Pharmaceutical","Recipes","Astronomical","Biological","Unassigned"]
WCOLS = {"Herbal":"w_Herbal","Pharmaceutical":"w_Pharm","Recipes":"w_Recipes",
         "Astronomical":"w_Astron","Biological":"w_Biolog","Unassigned":"w_Unasg"}

os.makedirs(OUTDIR, exist_ok=True)

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def load_rules_tsv(path):
    need = ["kind","pattern","pred_side","base_weight","allow_sections","deny_sections"]
    rules = []
    with open(path,encoding='utf-8') as f:
        r = csv.DictReader(f, dialect=csv.excel_tab)
        hdr = r.fieldnames or []
        for k in need:
            if k not in hdr:
                raise SystemExit(f"[ERROR] rules TSV missing column: {k}")
        for row in r:
            if not row.get("kind"): continue
            kind = row["kind"].strip()
            pattern = row["pattern"].strip()
            side = row["pred_side"].strip()
            try:
                base = float(row.get("base_weight","0") or "0")
            except:
                base = 0.0
            allow = [s.strip() for s in (row.get("allow_sections") or "").split(",") if s.strip()]
            deny  = [s.strip() for s in (row.get("deny_sections")  or "").split(",") if s.strip()]
            w_by_sec = {}
            for sec, col in WCOLS.items():
                val = (row.get(col) or "").strip()
                if val:
                    try:
                        w_by_sec[sec] = float(val)
                    except:
                        pass
            rid = f"{kind}:{pattern}:{side}"
            rules.append({
                "rule_id": rid, "kind": kind, "pattern": pattern, "pred_side": side,
                "base_weight": base, "allow": allow, "deny": deny, "w_by_section": w_by_sec,
            })
    if not rules:
        raise SystemExit("[ERROR] no rules loaded")
    return rules

def load_segments(path):
    rows=[]
    with open(path,encoding='utf-8') as f:
        hdr=f.readline().rstrip("\n").split("\t")
        idx={h:i for i,h in enumerate(hdr)}
        need=["stem","section","axis1","axis2","axis3"]
        for k in need:
            if k not in idx: raise SystemExit(f"[ERROR] segments missing {k}")
        for line in f:
            if not line.strip(): continue
            p=line.rstrip("\n").split("\t")
            try:
                rows.append({
                    "stem": p[idx["stem"]],
                    "section": p[idx["section"]],
                    "axis1": float(p[idx["axis1"]]),
                    "axis2": float(p[idx["axis2"]]),
                    "axis3": float(p[idx["axis3"]]),
                })
            except:
                continue
    if not rows: raise SystemExit("[ERROR] no segment rows read")
    return rows

def match_rule(stem, rule):
    k = rule["kind"]; pat = rule["pattern"]
    if k=="pair":
        pre, suf = (pat.split("|",1)+[""])[:2] if "|" in pat else (pat,"")
        return ( (not pre or stem.startswith(pre)) and (not suf or stem.endswith(suf)) )
    elif k=="prefix":
        return stem.startswith(pat)
    elif k=="suffix":
        return stem.endswith(pat)
    elif k=="chargram":
        return (pat in stem)
    return False

def section_allowed(sec, rule):
    if rule["deny"] and sec in rule["deny"]:
        return False
    if rule["allow"] and sec not in rule["allow"]:
        return False
    return True

def predict_item(stem, sec, rules):
    score = {"left":0.0, "right":0.0}
    any_hit = False
    for r in rules:
        if not section_allowed(sec, r): continue
        if not match_rule(stem, r): continue
        any_hit = True
        eff = r["base_weight"]
        if sec in r["w_by_section"]:
            eff *= r["w_by_section"][sec]
        score[r["pred_side"]] += eff
    if not any_hit: return None, 0.0, 0.0
    if score["left"]==score["right"]==0.0: return None, 0.0, 0.0
    return ("left" if score["left"]>score["right"] else "right", score["left"], score["right"])

def side_from_axis1(x):
    return "left" if x < 0 else ("right" if x > 0 else "")

def evaluate(rules, segs):
    n = len(segs)
    n_pred = n_corr = 0
    per_rule = defaultdict(lambda: {"support":0, "agree":0, "by_sec":Counter()})
    # also compute a light leaderboard from rules alone
    for it in segs:
        pred, wl, wr = predict_item(it["stem"], it["section"], rules)
        truth = side_from_axis1(it["axis1"])
        # track rule stats by “could match” to get support/agree
        for r in rules:
            if section_allowed(it["section"], r) and match_rule(it["stem"], r):
                per_rule[r["rule_id"]]["support"] += 1
                if truth and truth == r["pred_side"]:
                    per_rule[r["rule_id"]]["agree"] += 1
                per_rule[r["rule_id"]]["by_sec"][it["section"]] += 1
        if pred is not None and truth:
            n_pred += 1
            if pred == truth:
                n_corr += 1
    cov = n_pred/n if n else 0.0
    acc_cov = (n_corr/n_pred) if n_pred else 0.0
    overall = n_corr/n if n else 0.0
    return {"n_items":n, "n_pred":n_pred, "n_correct":n_corr,
            "coverage":cov, "acc_on_covered":acc_cov, "overall_accuracy":overall}, per_rule

def write_doc_md(rules, perf, per_rule, path_md):
    # leaders
    leader_support = sorted(
        [{"rule_id":rid, "support":d["support"],
          "precision": (d["agree"]/d["support"]) if d["support"] else 0.0}
         for rid,d in per_rule.items()],
        key=lambda x:(-x["support"], -x["precision"])
    )[:20]
    leader_precision = [r for r in leader_support if r["support"]>=6]
    leader_precision = sorted(leader_precision, key=lambda x:(-x["precision"], -x["support"]))[:20]
    with open(path_md,'w',encoding='utf-8') as f:
        f.write("# Phase 69 — Final Rulebook (Frozen)\n\n")
        f.write("## Metrics\n")
        f.write(f"- n_items: **{perf['n_items']}**\n")
        f.write(f"- coverage: **{perf['coverage']:.3f}**  \n")
        f.write(f"- acc_on_covered: **{perf['acc_on_covered']:.3f}**  \n")
        f.write(f"- overall_accuracy: **{perf['overall_accuracy']:.3f}**\n\n")
        f.write("## Leaders by Support (top 20)\n")
        for r in leader_support:
            f.write(f"- {r['rule_id']}: support={r['support']}, precision={r['precision']:.3f}\n")
        f.write("\n## Leaders by Precision (support ≥ 6)\n")
        for r in leader_precision:
            f.write(f"- {r['rule_id']}: precision={r['precision']:.3f}, support={r['support']}\n")

def main():
    # Load & basic checks
    rules = load_rules_tsv(RULES_TSV)
    segs  = load_segments(SEGMENTS)
    # Assert expected scale (not hard-failing on count so it stays robust)
    n_rules = len(rules)
    if n_rules < 80:
        raise SystemExit(f"[ERROR] too few rules loaded: {n_rules}")
    # Evaluate
    perf, per_rule = evaluate(rules, segs)
    # Export frozen copies
    # (a) TSV exact copy
    with open(RULES_TSV, 'rb') as src, open(FINAL_TSV, 'wb') as dst:
        dst.write(src.read())
    # (b) JSON structured
    with open(FINAL_JSON,'w',encoding='utf-8') as f:
        json.dump({"rules":rules}, f, indent=2)
    # (c) Summary with hashes
    sums = {
        "inputs": {
            "rules_tsv": RULES_TSV,
            "segments": SEGMENTS,
        },
        "hashes": {
            "rules_tsv_sha256": sha256(RULES_TSV),
            "segments_sha256": sha256(SEGMENTS),
        },
        "counts": {
            "n_rules": n_rules,
            "n_items": len(segs),
        },
        "metrics": perf,
        "frozen_outputs": {
            "final_rules_tsv": FINAL_TSV,
            "final_rules_json": FINAL_JSON,
            "doc_md": DOC_MD,
        },
        "validated": True
    }
    with open(SUMMARY,'w',encoding='utf-8') as f:
        json.dump(sums, f, indent=2)
    # (d) Short doc
    write_doc_md(rules, perf, per_rule, DOC_MD)
    print("== Phase 69: validation ==")
    print(f"rules: {RULES_TSV}")
    print(f"segments: {SEGMENTS}")
    print(f"n_rules={n_rules}  coverage={perf['coverage']:.3f}  acc_on_cov={perf['acc_on_covered']:.3f}  overall={perf['overall_accuracy']:.3f}")
    print("Wrote:")
    print(" ", FINAL_TSV)
    print(" ", FINAL_JSON)
    print(" ", SUMMARY)
    print(" ", DOC_MD)

if __name__=="__main__":
    main()
