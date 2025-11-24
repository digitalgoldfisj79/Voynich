#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
IND="$BASE/PhaseS/out"
IN_SLOTS="$IND/s29_slot_profiles.tsv"
OUT_TSV="$IND/s31_slot_bootstrap.tsv"
OUT_TXT="$IND/s31_slot_bootstrap.txt"

echo "[S31] BASE      = $BASE"
echo "[S31] IN_SLOTS  = $IN_SLOTS"
echo "[S31] OUT_TSV   = $OUT_TSV"
echo "[S31] OUT_TXT   = $OUT_TXT"

python3 - "$IN_SLOTS" "$OUT_TSV" "$OUT_TXT" << 'PY'
import sys, csv, math, random
from collections import defaultdict

in_slots, out_tsv, out_txt = sys.argv[1:4]

# --- Load slot profiles (S29) ---
rows = []
with open(in_slots, encoding="utf-8", newline="") as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        rows.append(row)

# Group by (family, token) and track L/C/R counts
by_ft = defaultdict(lambda: {"L": 0, "C": 0, "R": 0, "total": 0, "fam_total": None})
families = set()

for row in rows:
    fam = row["family"]
    tok = row["token"]
    pos = row["position"]
    hits = int(row["hits"])
    fam_total = int(row["family_total_instances"])
    key = (fam, tok)

    families.add(fam)
    by_ft[key][pos] += hits
    by_ft[key]["total"] += hits
    # fam_total should be the same for all rows of this family
    if by_ft[key]["fam_total"] is None:
        by_ft[key]["fam_total"] = fam_total

# --- Bootstrap configuration ---
N_BOOT = 2000
RNG = random.Random(12345)  # deterministic for reproducibility

def multinomial_sample(total, probs, rng):
    """Draw counts for L/C/R via multinomial using simple sampling."""
    keys = list(probs.keys())  # e.g., ["L","C","R"]
    weights = [probs[k] for k in keys]
    counts = {k: 0 for k in keys}
    # sample total times
    for _ in range(total):
        x = rng.random()
        acc = 0.0
        for k, w in zip(keys, weights):
            acc += w
            if x <= acc:
                counts[k] += 1
                break
    return counts

def quantiles(xs, lo_q, hi_q):
    if not xs:
        return (0.0, 0.0)
    xs = sorted(xs)
    n = len(xs)
    def q(qv):
        if n == 1:
            return xs[0]
        idx = qv * (n - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return xs[lo]
        frac = idx - lo
        return xs[lo] * (1 - frac) + xs[hi] * frac
    return q(lo_q), q(hi_q)

# --- Bootstrap per (family, token, position) ---
out_rows = []
summary_by_fam = defaultdict(lambda: {"L": [], "C": [], "R": []})

for (fam, tok), d in by_ft.items():
    total = d["total"]
    if total <= 0:
        continue
    fam_total = d["fam_total"]
    # empirical probabilities across positions
    probs = {}
    for pos in ("L", "C", "R"):
        if d[pos] > 0:
            probs[pos] = d[pos] / total
        else:
            probs[pos] = 0.0

    # bootstrap: simulate shares for each position
    boot_shares = {pos: [] for pos in ("L", "C", "R")}
    for _ in range(N_BOOT):
        counts = multinomial_sample(total, probs, RNG)
        for pos in ("L", "C", "R"):
            if total > 0:
                boot_shares[pos].append(counts[pos] / total)
            else:
                boot_shares[pos].append(0.0)

    # for each position with observed hits > 0, compute CI
    for pos in ("L", "C", "R"):
        hits = d[pos]
        if hits == 0:
            continue
        obs_share = hits / total
        coverage = hits / fam_total
        mean_boot = sum(boot_shares[pos]) / len(boot_shares[pos])
        lo, hi = quantiles(boot_shares[pos], 0.025, 0.975)

        out_rows.append({
            "family": fam,
            "token": tok,
            "position": pos,
            "hits": hits,
            "token_total_hits": total,
            "position_share": f"{obs_share:.6f}",
            "family_total_instances": fam_total,
            "coverage_frac": f"{coverage:.6f}",
            "boot_mean_share": f"{mean_boot:.6f}",
            "boot_ci_lower": f"{lo:.6f}",
            "boot_ci_upper": f"{hi:.6f}",
            "n_boot": N_BOOT,
        })

        summary_by_fam[fam][pos].append({
            "token": tok,
            "hits": hits,
            "total": total,
            "share": obs_share,
            "ci": (lo, hi),
        })

# --- Write TSV output ---
with open(out_tsv, "w", encoding="utf-8", newline="") as f:
    fieldnames = [
        "family", "token", "position", "hits", "token_total_hits",
        "position_share", "family_total_instances", "coverage_frac",
        "boot_mean_share", "boot_ci_lower", "boot_ci_upper", "n_boot",
    ]
    w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
    w.writeheader()
    for row in sorted(out_rows, key=lambda r: (r["family"], r["token"], r["position"])):
        w.writerow(row)

# --- Write human-readable TXT summary ---
with open(out_txt, "w", encoding="utf-8") as f:
    f.write("S31 slot bootstrap summary (95% CIs)\n")
    f.write("=====================================\n\n")
    for fam in sorted(families):
        slots = summary_by_fam[fam]
        f.write(f"Family: {fam}\n")
        for pos_label, label_name in (("L", "left"), ("C", "centre"), ("R", "right")):
            lst = slots[pos_label]
            if not lst:
                continue
            # mark "strongly locked" tokens: share >= 0.8 and CI lower >= 0.6
            strong = [
                t for t in lst
                if t["share"] >= 0.8 and t["ci"][0] >= 0.6
            ]
            f.write(f"  Position {pos_label} ({label_name}): n_tokens={len(lst)}, strongly_locked={len(strong)}\n")
            if strong:
                # top 5 by share
                strong_sorted = sorted(strong, key=lambda t: t["share"], reverse=True)[:5]
                f.write("    Example strongly-locked tokens:\n")
                for t in strong_sorted:
                    lo, hi = t["ci"]
                    f.write(
                        f"      - {t['token']} share={t['share']:.3f}, "
                        f"CI95=[{lo:.3f}, {hi:.3f}], hits={t['hits']}, total={t['total']}\n"
                    )
        f.write("\n")
PY
