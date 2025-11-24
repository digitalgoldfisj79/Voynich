#!/usr/bin/env python3
import json
import os
from copy import deepcopy

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P69_PATH = os.path.join(BASE, "Phase69", "out", "p69_rules_final.json")
P70_PATH = os.path.join(BASE, "Phase70", "out", "p70_new_rules.json")
OUT_PATH = os.path.join(BASE, "Phase70", "out", "p70_rulebook_extended.json")

def load_json(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    os.makedirs(os.path.join(BASE, "Phase70", "out"), exist_ok=True)

    base = load_json(P69_PATH)

    # Expect either:
    #  (a) dict with "rules" list, or
    #  (b) plain list of rules.
    if isinstance(base, dict) and "rules" in base:
        rules = list(base["rules"])
        wrapper = {k: (v if k != "rules" else rules) for k, v in base.items()}
    elif isinstance(base, list):
        rules = list(base)
        wrapper = {"rules": rules}
    else:
        raise ValueError("Unexpected structure in p69_rules_final.json")

    if os.path.isfile(P70_PATH):
        extra = load_json(P70_PATH)
        if isinstance(extra, dict) and "rules" in extra:
            extra_rules = extra["rules"]
        elif isinstance(extra, list):
            extra_rules = extra
        else:
            raise ValueError("Unexpected structure in p70_new_rules.json")

        # Avoid simple duplicates: use (pre,suf) as rough key when present
        seen = set()
        for r in rules:
            pre = r.get("pre", "")
            suf = r.get("suf", "")
            seen.add((pre, suf))

        added = 0
        for r in extra_rules:
            if not isinstance(r, dict):
                continue
            pre = r.get("pre", "")
            suf = r.get("suf", "")
            key = (pre, suf)
            if key not in seen:
                rules.append(deepcopy(r))
                seen.add(key)
                added += 1

        print(f"[INFO] Merged {added} new rules from p70_new_rules.json")
    else:
        print("[INFO] No p70_new_rules.json found; using Phase69 rules only.")

    # Write out a clean combined rulebook
    wrapper["rules"] = rules
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(wrapper, f, ensure_ascii=False, indent=2)
    print(f"[OK] Wrote extended rulebook → {OUT_PATH}")
    print(f"[OK] Total rules: {len(rules)}")

if __name__ == "__main__":
    main()
