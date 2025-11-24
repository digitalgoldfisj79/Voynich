#!/usr/bin/env python3
import os
import csv
from collections import defaultdict, Counter

BASE = os.path.expanduser("~/Voynich/Voynich_Reproducible_Core")
OUTD = os.path.join(BASE, "PhaseS", "out")

s47_path = os.path.join(OUTD, "s47_clause_semantic_skeletons.tsv")

out_section_tsv = os.path.join(OUTD, "s48_section_diglossia_stats.tsv")
out_summary_txt = os.path.join(OUTD, "s48_prediction_tests.txt")


def dominant_section(row):
    """Pick the majority primary_section among L/C/R_*; if tie/none -> MixedOrUnknown."""
    sections = []
    for pos in ("L", "C", "R"):
        sec = row.get(f"{pos}_primary_section", "").strip()
        if sec:
            sections.append(sec)
    if not sections:
        return "MixedOrUnknown"
    counts = Counter(sections)
    sec, n = counts.most_common(1)[0]
    # If tie between two or more, treat as mixed
    if list(counts.values()).count(n) > 1:
        return "MixedOrUnknown"
    return sec


def safe_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def main():
    if not os.path.exists(s47_path):
        raise SystemExit(f"[S48] ERROR: cannot find {s47_path}")

    # Aggregation structures per dominant section
    stats = defaultdict(lambda: {
        "total_weight": 0,           # sum of clause counts
        "sum_proc_slots": 0.0,
        "sum_bot_slots": 0.0,
        "sum_bio_slots": 0.0,
        "sum_ambig_slots": 0.0,
        "sum_has_agent_patient": 0.0,
        "sum_valency_score": 0.0,
        "sum_pure_botbio_clauses": 0.0,  # clauses where all slots are BOT/BIO
        "sum_pure_proc_clauses": 0.0,    # clauses where all slots are PROC
        "sum_clauses": 0.0,
        "sum_slots": 0.0,           # 3 * total_weight for 3-slot clauses
    })

    with open(s47_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                weight = int(row.get("count", "0"))
            except ValueError:
                weight = 0
            if weight <= 0:
                continue

            sec = dominant_section(row)
            s = stats[sec]

            s["total_weight"] += weight
            s["sum_clauses"] += weight
            s["sum_slots"] += 3 * weight

            # Slot-level inspection
            role_groups = []
            sem_fams = []
            roles = []
            proc_slots = 0
            bot_slots = 0
            bio_slots = 0
            ambig_slots = 0

            for pos in ("L", "C", "R"):
                rg = row.get(f"{pos}_role_group", "").strip()
                sf = row.get(f"{pos}_semantic_family", "").strip()
                r = row.get(f"{pos}_role", "").strip()

                role_groups.append(rg)
                sem_fams.append(sf)
                roles.append(r)

                if rg == "PROC":
                    proc_slots += 1
                if rg == "BOT" or sf == "F_BOTANICAL_CORE":
                    bot_slots += 1
                if rg == "BIO" or sf == "F_BIO_CORE":
                    bio_slots += 1
                if r == "AMBIGUOUS":
                    ambig_slots += 1

            s["sum_proc_slots"] += proc_slots * weight
            s["sum_bot_slots"] += bot_slots * weight
            s["sum_bio_slots"] += bio_slots * weight
            s["sum_ambig_slots"] += ambig_slots * weight

            # Agent–patient presence: simple binary
            has_agent = any(r == "AGENT_CAND" for r in roles)
            has_patient = any(r == "PATIENT_CAND" for r in roles)
            if has_agent and has_patient:
                s["sum_has_agent_patient"] += weight

            # Pure descriptive = all slots BOT or BIO (by role_group or family)
            if proc_slots == 0 and all(
                (rg in ("BOT", "BIO") or sf in ("F_BOTANICAL_CORE", "F_BIO_CORE"))
                for rg, sf in zip(role_groups, sem_fams)
            ):
                s["sum_pure_botbio_clauses"] += weight

            # Pure PROC = all three slots PROC
            if proc_slots == 3:
                s["sum_pure_proc_clauses"] += weight

            # Valency score: L vs R agent-likeness
            L_frac_agent = safe_float(row.get("L_frac_agent_like", "0"))
            R_frac_agent = safe_float(row.get("R_frac_agent_like", "0"))
            valency_score = L_frac_agent - R_frac_agent
            s["sum_valency_score"] += valency_score * weight

    # Write per-section TSV
    os.makedirs(OUTD, exist_ok=True)
    tmp_tsv = out_section_tsv + ".tmp"

    fieldnames = [
        "section",
        "total_weight",
        "mean_proc_slots_per_clause",
        "proc_slot_fraction",
        "mean_bot_slots_per_clause",
        "mean_bio_slots_per_clause",
        "mean_ambig_slots_per_clause",
        "prop_clauses_with_agent_patient",
        "mean_valency_score_L_minus_R",
        "prop_pure_botbio_clauses",
        "prop_pure_proc_clauses",
    ]

    with open(tmp_tsv, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for sec, s in sorted(stats.items()):
            total = s["total_weight"] or 1.0
            slots = s["sum_slots"] or 1.0

            row = {
                "section": sec,
                "total_weight": int(s["total_weight"]),
                "mean_proc_slots_per_clause": f"{s['sum_proc_slots'] / total:.6f}",
                "proc_slot_fraction": f"{s['sum_proc_slots'] / slots:.6f}",
                "mean_bot_slots_per_clause": f"{s['sum_bot_slots'] / total:.6f}",
                "mean_bio_slots_per_clause": f"{s['sum_bio_slots'] / total:.6f}",
                "mean_ambig_slots_per_clause": f"{s['sum_ambig_slots'] / total:.6f}",
                "prop_clauses_with_agent_patient": f"{s['sum_has_agent_patient'] / total:.6f}",
                "mean_valency_score_L_minus_R": f"{s['sum_valency_score'] / total:.6f}",
                "prop_pure_botbio_clauses": f"{s['sum_pure_botbio_clauses'] / total:.6f}",
                "prop_pure_proc_clauses": f"{s['sum_pure_proc_clauses'] / total:.6f}",
            }
            writer.writerow(row)

    os.replace(tmp_tsv, out_section_tsv)

    # Human-readable summary linked to predictions
    tmp_txt = out_summary_txt + ".tmp"
    with open(tmp_txt, "w", encoding="utf-8") as f:
        f.write("[S48] Diglossia prediction tests (section-based)\n")
        f.write("Inputs: s47_clause_semantic_skeletons.tsv\n\n")

        f.write("Per-section stats:\n")
        for sec, s in sorted(stats.items()):
            total = s["total_weight"] or 1.0
            slots = s["sum_slots"] or 1.0
            mean_proc = s["sum_proc_slots"] / total
            mean_bot = s["sum_bot_slots"] / total
            mean_bio = s["sum_bio_slots"] / total
            mean_ambig = s["sum_ambig_slots"] / total
            prop_val = s["sum_has_agent_patient"] / total
            mean_val_sc = s["sum_valency_score"] / total
            prop_pure_botbio = s["sum_pure_botbio_clauses"] / total
            prop_pure_proc = s["sum_pure_proc_clauses"] / total

            f.write(f"- Section {sec} (weighted clauses={int(total)}):\n")
            f.write(f"    mean PROC slots/clauses: {mean_proc:.3f}\n")
            f.write(f"    mean BOT slots/clauses:  {mean_bot:.3f}\n")
            f.write(f"    mean BIO slots/clauses:  {mean_bio:.3f}\n")
            f.write(f"    mean AMBIGUOUS roles:    {mean_ambig:.3f}\n")
            f.write(f"    prop clauses with AGENT+PATIENT: {prop_val:.3f}\n")
            f.write(f"    mean valency (L_agent - R_agent): {mean_val_sc:.3f}\n")
            f.write(f"    prop pure BOT/BIO clauses: {prop_pure_botbio:.3f}\n")
            f.write(f"    prop pure PROC clauses:    {prop_pure_proc:.3f}\n")
            f.write("\n")

        f.write("Interpretation hooks (for you to align with S45 Currier mapping):\n")
        f.write("- Biological and Recipes sections are Currier B-only (S45).\n")
        f.write("- Herbal is A-dominant; Pharmaceutical mixed but small.\n")
        f.write("Use the above stats to check:\n")
        f.write("  Prediction 1: Herbal/A sections should show more pure BOT/BIO, more AMBIGUOUS roles.\n")
        f.write("  Prediction 2: Biological/Recipes (B) should show more PROC slots and AGENT→PATIENT patterns.\n")
        f.write("  Prediction 3: Recipes should show highest PROC density and strongest valency.\n")

    os.replace(tmp_txt, out_summary_txt)

    print(f"[S48] Wrote section diglossia stats to: {out_section_tsv}")
    print(f"[S48] Wrote prediction summary to:        {out_summary_txt}")


if __name__ == "__main__":
    main()
