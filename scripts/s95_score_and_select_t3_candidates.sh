#!/usr/bin/env sh
# S95 – Multi-evidence scoring + selection for T3 candidates
# - Input:  metadata/t3_candidates_domains_curated.tsv
# - Optional: PhaseT/out/s83_charonly_fixed.tsv (form similarity)
# - Output:
#     PhaseT/out/t3_candidates_scored.tsv
#     PhaseT/out/t3_lexicon_selected.tsv

set -eu

BASE=${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}

IN_CANDIDATES="$BASE/metadata/t3_candidates_domains_curated.tsv"
IN_FORM="$BASE/PhaseT/out/s83_charonly_fixed.tsv"   # optional
OUT_SCORED="$BASE/PhaseT/out/t3_candidates_scored.tsv"
OUT_SELECTED="$BASE/PhaseT/out/t3_lexicon_selected.tsv"

echo "[s95] BASE:       $BASE"
echo "[s95] Candidates: $IN_CANDIDATES"
echo "[s95] Form sim:   $IN_FORM (optional)"
echo "[s95] Scored:     $OUT_SCORED"
echo "[s95] Selected:   $OUT_SELECTED"

mkdir -p "$BASE/PhaseT/out"

if [ ! -f "$IN_CANDIDATES" ]; then
  echo "[s95][ERROR] Missing candidates file: $IN_CANDIDATES" >&2
  exit 1
fi

python3 - "$IN_CANDIDATES" "$IN_FORM" "$OUT_SCORED" "$OUT_SELECTED" << 'PY'
import sys
import math
import pandas as pd

in_candidates = sys.argv[1]
in_form = sys.argv[2]
out_scored = sys.argv[3]
out_selected = sys.argv[4]

print("[s95(py)] Loading candidates from:", in_candidates, file=sys.stderr)
df = pd.read_csv(in_candidates, sep="\t")

# --- sanity check on columns ---
required_cols = [
    "stem",
    "functional_label",
    "lemma_latin",
    "gloss_en",
    "latin_domain",
    "corpus_freq",
    "latin_source",
    "candidate_source",
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise SystemExit(f"[s95(py)][ERROR] Missing columns in candidates TSV: {missing}")

print(f"[s95(py)] Loaded {len(df)} candidate rows", file=sys.stderr)

# --------------------------------------------------------------------
# Load form similarity (from s83) if available
# We expect columns: stem, latin_token, char_cosine
# --------------------------------------------------------------------
form_dict = {}
try:
    form_df = pd.read_csv(in_form, sep="\t")
    needed = ["stem", "latin_token", "char_cosine"]
    fm_missing = [c for c in needed if c not in form_df.columns]
    if fm_missing:
        print(f"[s95(py)][WARN] Form file present but missing cols {fm_missing}; using neutral form scores.", file=sys.stderr)
    else:
        for _, row in form_df.iterrows():
            key = (str(row["stem"]), str(row["latin_token"]))
            form_dict[key] = float(row["char_cosine"])
        print(f"[s95(py)] Loaded {len(form_dict)} form similarity scores", file=sys.stderr)
except FileNotFoundError:
    print("[s95(py)] No form similarity file found; using neutral scores.", file=sys.stderr)

# --------------------------------------------------------------------
# Scoring components – aligned with your multi-evidence plan
# --------------------------------------------------------------------

def score_corpus_frequency(freq):
    """
    Corpus frequency → 0..1 (log10 scaled)
    freq = 1  -> ~0.15
    freq = 10 -> ~0.52
    freq = 100 -> 1.0 (capped)
    """
    try:
        f = float(freq)
    except Exception:
        return 0.0
    if f <= 0:
        return 0.0
    return min(1.0, math.log10(f + 1.0) / 2.0)

def score_form_similarity(stem, lemma):
    """
    Character-level similarity from s83 (char_cosine).
    We know this is weak, so it is low weight in the total score.
    If missing, return neutral 0.50.
    """
    key = (str(stem), str(lemma))
    if key in form_dict:
        return float(form_dict[key])
    return 0.50

def score_domain_centrality(lemma, domain):
    """
    Is lemma central to the domain?
    - coquo / decoquo central in PROC_COOKING
    - misceo / admisceo central in PROC_MIXING
    - tero / contero central in PROC_GRINDING
    - infundo / pono central in PROC_ADDING
    Others get 0.5 (peripheral but still plausible).
    """
    central_verbs = {
        "PROC_COOKING":  ["coquo", "decoquo"],
        "PROC_MIXING":   ["misceo", "admisceo"],
        "PROC_GRINDING": ["tero", "contero"],
        "PROC_ADDING":   ["infundo", "pono"],
        # For herbs / fluids we treat all as central (see below)
    }

    if domain in central_verbs and lemma in central_verbs[domain]:
        return 1.0
    # For non-verb domains, everything in the curated list is already "central"
    if domain in ("BOT_HERB", "BIO_FLUID"):
        return 1.0
    return 0.5

def score_lemma_specificity(lemma, domain):
    """
    Prefer specific actions / substances over generic ones.
    - 'pono' is generic placement → lower specificity
    - Most others are domain-specific → high specificity
    """
    generic_verbs = {"pono", "facio", "do"}
    if lemma in generic_verbs:
        return 0.3
    # For BOT_HERB/BIO_FLUID, the lemma list is already quite specific.
    return 1.0

# --------------------------------------------------------------------
# Apply scoring to each candidate
# --------------------------------------------------------------------
print("[s95(py)] Computing component scores...", file=sys.stderr)

rows = []
for _, row in df.iterrows():
    stem   = row["stem"]
    lemma  = row["lemma_latin"]
    domain = row["latin_domain"]
    freq   = row["corpus_freq"]

    freq_s  = score_corpus_frequency(freq)
    form_s  = score_form_similarity(stem, lemma)
    dom_s   = score_domain_centrality(lemma, domain)
    spec_s  = score_lemma_specificity(lemma, domain)

    # Total score: match the narrative exactly
    # 0.20 freq + 0.05 form + 0.40 domain + 0.35 specificity
    total = (
        0.20 * freq_s +
        0.05 * form_s +
        0.40 * dom_s +
        0.35 * spec_s
    )

    rows.append({
        "stem": stem,
        "functional_label": row["functional_label"],
        "lemma_latin": lemma,
        "gloss_en": row["gloss_en"],
        "latin_domain": domain,
        "corpus_freq": freq,
        "freq_score": round(freq_s, 3),
        "form_score": round(form_s, 3),
        "domain_score": round(dom_s, 3),
        "spec_score": round(spec_s, 3),
        "total_score": round(total, 3),
    })

scores_df = pd.DataFrame(rows)
scores_df = scores_df.sort_values(["stem", "total_score"], ascending=[True, False])
scores_df.to_csv(out_scored, sep="\t", index=False)
print(f"[s95(py)] Wrote scored candidates to {out_scored}", file=sys.stderr)

# --------------------------------------------------------------------
# Selection rules:
# 1. One lemma per cluster (lemma can't be reused)
# 2. Minimum total_score >= 0.50
# 3. Pick highest scoring remaining candidate per stem
# 4. Confidence from total_score:
#    >=0.75 → MEDIUM-HIGH
#    >=0.60 → MEDIUM
#    >=0.50 → LOW-MEDIUM
# 5. If form_score < 0.60, downgrade one level (weak form support)
# --------------------------------------------------------------------
print("[s95(py)] Selecting winners per stem...", file=sys.stderr)

selected = []
used_lemmas = set()

def downgrade_conf(conf):
    order = ["HIGH", "MEDIUM-HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"]
    idx = order.index(conf)
    if idx == 0:
        return "MEDIUM-HIGH"
    return order[min(idx + 1, len(order) - 1)]

for stem in scores_df["stem"].unique():
    block = scores_df[scores_df["stem"] == stem]

    # Exclude lemmas already used for other stems
    available = block[~block["lemma_latin"].isin(used_lemmas)]
    if available.empty:
        print(f"[s95(py)] {stem}: no available lemmas (all used)", file=sys.stderr)
        continue

    # Require total_score >= 0.50
    viable = available[available["total_score"] >= 0.50]
    if viable.empty:
        print(f"[s95(py)] {stem}: no viable candidates (all < 0.50)", file=sys.stderr)
        continue

    winner = viable.iloc[0].copy()

    # Confidence mapping from score
    ts = winner["total_score"]
    if ts >= 0.75:
        conf = "MEDIUM-HIGH"
    elif ts >= 0.60:
        conf = "MEDIUM"
    elif ts >= 0.50:
        conf = "LOW-MEDIUM"
    else:
        conf = "LOW"

    note = ""

    # Cap confidence if form support is weak (<0.60)
    if winner["form_score"] < 0.60:
        old_conf = conf
        conf = downgrade_conf(conf)
        if conf != old_conf:
            note = "downgraded: weak form support"
        else:
            note = "weak form support"

    winner["confidence"] = conf
    winner["note"] = note

    selected.append(winner)
    used_lemmas.add(winner["lemma_latin"])

    print(
        f"[s95(py)] {stem} → {winner['lemma_latin']} "
        f"(score={winner['total_score']:.3f}, conf={conf})",
        file=sys.stderr,
    )

selected_df = pd.DataFrame(selected)
selected_df = selected_df.sort_values("total_score", ascending=False)
selected_df.to_csv(out_selected, sep="\t", index=False)

print(f"[s95(py)] Selected {len(selected_df)} stems for T3 lexicon", file=sys.stderr)
if not selected_df.empty:
    print("[s95(py)] Confidence distribution:", file=sys.stderr)
    print(selected_df["confidence"].value_counts().to_string(), file=sys.stderr)
PY

echo "[s95] Done. Top of selected T3 lexicon:"
echo "--------------------------------------"
if [ -f "$OUT_SELECTED" ]; then
  head -20 "$OUT_SELECTED"
else
  echo "[s95] WARNING: No selected file produced."
fi

echo
echo "[s95] Full results:"
echo "  Scored:   $OUT_SCORED"
echo "  Selected: $OUT_SELECTED"
