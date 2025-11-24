#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE:-"$(pwd)"}

IN_T2="$BASE/metadata/t2_stem_functional_lexicon.tsv"
IN_CAND="$BASE/metadata/t3_candidates.tsv"
OUT_T3="$BASE/metadata/t3_lexical_lexicon.tsv"
TMP_OUT="${OUT_T3}.tmp"

echo "[s70] BASE:    $BASE"
echo "[s70] IN_T2:   $IN_T2"
echo "[s70] IN_CAND: $IN_CAND"
echo "[s70] OUT_T3:  $OUT_T3"

# Basic checks
if [ ! -f "$IN_T2" ]; then
    echo "[s70] ERROR: T2 lexicon not found at $IN_T2" >&2
    exit 1
fi

if [ ! -f "$IN_CAND" ]; then
    echo "[s70] ERROR: T3 candidate file not found at $IN_CAND" >&2
    exit 1
fi

OUT_T3_TMP="$TMP_OUT" BASE="$BASE" python3 - << 'PY'
import os
import pandas as pd
from collections import defaultdict

base = os.environ.get("BASE", os.getcwd())
in_t2   = os.path.join(base, "metadata", "t2_stem_functional_lexicon.tsv")
in_cand = os.path.join(base, "metadata", "t3_candidates.tsv")
out_t3  = os.environ["OUT_T3_TMP"]

print(f"[s70(py)] Loading T2 lexicon from: {in_t2}")
t2 = pd.read_csv(in_t2, sep='\t', dtype=str)

print(f"[s70(py)] Loading T3 candidates from: {in_cand}")
cand = pd.read_csv(in_cand, sep='\t', dtype=str)

# Ensure required columns
required_t2_cols = {"stem", "functional_label", "confidence", "notes"}
missing_t2 = required_t2_cols - set(t2.columns)
if missing_t2:
    raise SystemExit(f"[s70(py)] ERROR: T2 lexicon missing columns: {missing_t2}")

required_cand_cols = {"stem", "lemma_latin", "gloss_en", "pos", "form_score", "semantic_score", "corpus_score"}
missing_cand = required_cand_cols - set(cand.columns)
if missing_cand:
    raise SystemExit(f"[s70(py)] ERROR: T3 candidates missing columns: {missing_cand}")

# --- Helpers --------------------------------------------------------------

def parse_notes(notes_str):
    """
    Parse notes like:
      dom_family=F_BOTANICAL_CORE; dom_family_frac=1.000; n_tokens=1; target_cat=BOT; target_rg_frac=1.000; ...
    into a dict.
    """
    out = {}
    if not isinstance(notes_str, str):
        return out
    for part in notes_str.split(';'):
        part = part.strip()
        if not part:
            continue
        if '=' not in part:
            continue
        k, v = part.split('=', 1)
        out[k.strip()] = v.strip()
    return out

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def pos_match(t2_label, latin_pos):
    """Ensure grammatical category matches."""
    if t2_label == "PROC_VERB" and latin_pos == "V":
        return 1.0
    elif t2_label == "BOT_ENTITY" and latin_pos in ("N", "NP"):
        return 1.0
    elif t2_label == "BIO_STATE" and latin_pos in ("N", "ADJ"):
        return 1.0
    else:
        return 0.0

HIGH_FREQ_FUNCTION_STOPLIST = {
    # Can extend later; keep minimal for now
    "qok", "qoke", "qoky", "oke", "okeey", "she", "che"
}

def is_t3_eligible(stem_row):
    """
    stem_row: dict with keys:
      stem, t2_label, t2_conf, semantic_family, n_tokens, target_rg_frac
    NOTE: For this pilot (single-folio), we relax:
      - n_tokens >= 1 (instead of >= 10)
      - keep target_rg_frac >= 0.80 (uses your validated T2)
    """
    t2_label = stem_row.get("t2_label")
    t2_conf  = stem_row.get("t2_conf")
    sem_fam  = stem_row.get("semantic_family")
    n_tokens = stem_row.get("n_tokens", 0)
    n_tokens = int(n_tokens) if str(n_tokens).isdigit() else 0
    rg_frac  = float(stem_row.get("target_rg_frac", 0.0))
    stem     = stem_row.get("stem", "")

    if t2_label not in ("PROC_VERB", "BOT_ENTITY", "BIO_STATE"):
        return False
    if t2_conf not in ("MEDIUM", "HIGH"):
        return False
    if sem_fam not in ("F_PROC_CORE", "F_BOTANICAL_CORE", "F_BIO_CORE"):
        return False
    # PILOT: allow single-folio stems
    if n_tokens < 1:
        return False
    # semantic_stable from S56 not available here → assume True for now
    if rg_frac < 0.80:
        return False
    if stem in HIGH_FREQ_FUNCTION_STOPLIST:
        return False
    return True

def band_from_lexical_score(score):
    if score >= 0.85:
        return "HIGH"
    elif score >= 0.75:
        return "MEDIUM"
    elif score >= 0.70:
        return "LOW"
    else:
        return None

def cap_by_t2_conf(t2_conf, t3_band):
    if t3_band is None:
        return None
    order = ["LOW", "MEDIUM", "HIGH"]
    if t2_conf not in order:
        return None
    return order[min(order.index(t2_conf), order.index(t3_band))]

# Build dict of T2 info keyed by stem
t2_info = {}
for _, row in t2.iterrows():
    stem = row["stem"]
    notes = parse_notes(row.get("notes"))
    dom_family = notes.get("dom_family")
    n_tokens = notes.get("n_tokens", "0")
    target_rg_frac = notes.get("target_rg_frac", "0.0")

    t2_info[stem] = {
        "stem": stem,
        "t2_label": row["functional_label"],
        "t2_conf": row["confidence"],
        "semantic_family": dom_family,
        "n_tokens": n_tokens,
        "target_rg_frac": safe_float(target_rg_frac),
    }

print(f"[s70(py)] Loaded T2 info for {len(t2_info)} stems")

# Group candidates by stem
cand["form_score"] = cand["form_score"].apply(safe_float)
cand["semantic_score"] = cand["semantic_score"].apply(safe_float)
cand["corpus_score"] = cand["corpus_score"].apply(safe_float)

groups = defaultdict(list)
for _, row in cand.iterrows():
    groups[row["stem"]].append(row)

print(f"[s70(py)] Found candidates for {len(groups)} stems")

out_rows = []

for stem, rows in groups.items():
    if stem not in t2_info:
        # no T2 info → cannot proceed
        continue

    srow = t2_info[stem]
    if not is_t3_eligible(srow):
        continue

    t2_label = srow["t2_label"]
    t2_conf  = srow["t2_conf"]

    scored = []
    for _, c in enumerate(rows):
        pm = pos_match(t2_label, c["pos"])
        if pm == 0.0:
            # POS mismatch → skip
            continue

        form = c["form_score"]
        sem  = c["semantic_score"]
        corp = c["corpus_score"]
        context = 0.5  # neutral default for now

        lexical_score = (
            0.20 * form +
            0.35 * sem +
            0.15 * corp +
            0.15 * context +
            0.15 * pm
        )

        scored.append({
            "lemma_latin": c["lemma_latin"],
            "gloss_en": c["gloss_en"],
            "pos": c["pos"],
            "form_score": form,
            "semantic_score": sem,
            "corpus_score": corp,
            "context_score": context,
            "pos_match": pm,
            "lexical_score": lexical_score,
        })

    if not scored:
        continue

    scored.sort(key=lambda x: x["lexical_score"], reverse=True)
    best = scored[0]
    alt1 = scored[1] if len(scored) > 1 else None
    alt2 = scored[2] if len(scored) > 2 else None

    best_score = best["lexical_score"]
    t3_band = band_from_lexical_score(best_score)
    final_conf = cap_by_t2_conf(t2_conf, t3_band)

    if final_conf is None:
        continue

    if alt1:
        gap_to_alt1 = best_score - alt1["lexical_score"]
    else:
        gap_to_alt1 = best_score

    out_rows.append({
        "stem": stem,
        "lemma_latin": best["lemma_latin"],
        "gloss_en": best["gloss_en"],
        "pos": best["pos"],
        "confidence": final_conf,
        "lexical_score": f"{best_score:.3f}",
        "rule_id": "R_T3_DEFAULT",
        "evidence": "T2,S16,S46,S56,S59,Phase110?",
        "notes": "context_score=0.5; single-pass; pilot",
        "alt1_lemma": alt1["lemma_latin"] if alt1 else "",
        "alt1_score": f"{alt1['lexical_score']:.3f}" if alt1 else "",
        "alt2_lemma": alt2["lemma_latin"] if alt2 else "",
        "alt2_score": f"{alt2['lexical_score']:.3f}" if alt2 else "",
        "gap_to_alt1": f"{gap_to_alt1:.3f}",
    })

print(f"[s70(py)] Wrote {len(out_rows)} T3 entries")

cols = [
    "stem",
    "lemma_latin",
    "gloss_en",
    "pos",
    "confidence",
    "lexical_score",
    "rule_id",
    "evidence",
    "notes",
    "alt1_lemma",
    "alt1_score",
    "alt2_lemma",
    "alt2_score",
    "gap_to_alt1",
]

out_df = pd.DataFrame(out_rows, columns=cols)
out_df.to_csv(out_t3, sep='\t', index=False)
print(f"[s70(py)] T3 lexicon written to {out_t3}")
PY

# Atomic-ish promote
if [ -f "$TMP_OUT" ]; then
    mv "$TMP_OUT" "$OUT_T3"
fi

echo "[s70] Done."
