#!/usr/bin/env sh
# S97 – Score and select T3 candidates with stem-frequency-aware selection.
# Uses:
#   - metadata/t3_candidates_domains_curated.tsv  (domain-based candidates)
#   - PhaseT/out/s83_charonly_fixed.tsv          (form similarity, optional)
#   - metadata/t03_stem_frequencies.tsv          (Voynich stem frequencies)
# Produces:
#   - PhaseT/out/t3_candidates_scored_withfreq.tsv
#   - PhaseT/out/t3_lexicon_selected_withfreq.tsv

set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

CANDIDATES_TSV="$BASE/metadata/t3_candidates_domains_curated.tsv"
FORM_TSV="$BASE/PhaseT/out/s83_charonly_fixed.tsv"
STEM_FREQ_TSV="$BASE/metadata/t03_stem_frequencies.tsv"

OUT_SCORED="$BASE/PhaseT/out/t3_candidates_scored_withfreq.tsv"
OUT_SELECTED="$BASE/PhaseT/out/t3_lexicon_selected_withfreq.tsv"

echo "[s97] BASE:       $BASE"
echo "[s97] Candidates: $CANDIDATES_TSV"
echo "[s97] Form sim:   $FORM_TSV (optional)"
echo "[s97] Stem freq:  $STEM_FREQ_TSV"
echo "[s97] Scored:     $OUT_SCORED"
echo "[s97] Selected:   $OUT_SELECTED"

mkdir -p "$BASE/PhaseT/out"

python3 - "$CANDIDATES_TSV" "$FORM_TSV" "$STEM_FREQ_TSV" "$OUT_SCORED" "$OUT_SELECTED" << 'PY'
import sys
import math
import pandas as pd

cand_path = sys.argv[1]
form_path = sys.argv[2]
stemfreq_path = sys.argv[3]
out_scored = sys.argv[4]
out_selected = sys.argv[5]

# ---------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------
print(f"[s97(py)] Loading candidates from: {cand_path}", file=sys.stderr)
df = pd.read_csv(cand_path, sep="\t")
print(f"[s97(py)] Loaded {len(df)} candidate rows", file=sys.stderr)

# Load form similarity scores (optional)
try:
    form_df = pd.read_csv(form_path, sep="\t")
    # Expect columns like: stem, latin_token, char_cosine
    form_dict = {}
    for _, row in form_df.iterrows():
        stem = str(row.get("stem", "")).strip()
        latin_tok = str(row.get("latin_token", "")).strip()
        if not stem or not latin_tok:
            continue
        key = (stem, latin_tok)
        try:
            cos = float(row.get("char_cosine", 0.5))
        except Exception:
            cos = 0.5
        form_dict[key] = cos
    print(f"[s97(py)] Loaded {len(form_dict)} form similarity scores", file=sys.stderr)
except Exception as e:
    print(f"[s97(py)] Form similarity not available ({e}); using neutral scores", file=sys.stderr)
    form_dict = {}

# Load stem frequencies from T03
print(f"[s97(py)] Loading stem frequencies from: {stemfreq_path}", file=sys.stderr)
freq_df = pd.read_csv(stemfreq_path, sep="\t")
# Expect columns: stem, count (or similar)
freq_col_candidates = [c for c in freq_df.columns if c.lower() in ("count", "freq", "frequency", "n")]
if len(freq_col_candidates) != 1:
    raise SystemExit(f"[s97(py)][ERROR] Could not uniquely identify frequency column in {stemfreq_path}: {freq_df.columns.tolist()}")
freq_col = freq_col_candidates[0]

stem_freq = {}
for _, row in freq_df.iterrows():
    s = str(row["stem"])
    try:
        stem_freq[s] = int(row[freq_col])
    except Exception:
        stem_freq[s] = 0

print(f"[s97(py)] Loaded {len(stem_freq)} stem frequency entries (col={freq_col})", file=sys.stderr)

# ---------------------------------------------------------------------
# Scoring components
# ---------------------------------------------------------------------
def score_corpus_frequency(freq: float) -> float:
    """Score based on how common the Latin lemma is."""
    if freq is None or freq <= 0:
        return 0.0
    # freq=1→≈0.15, freq=10→0.5, freq≈100→1.0 (capped)
    return min(1.0, math.log10(freq + 1.0) / 2.0)

def score_form_similarity(stem: str, lemma: str) -> float:
    """Weak form similarity signal from s83."""
    key = (stem, lemma)
    if key in form_dict:
        return float(form_dict[key])
    # Neutral if missing
    return 0.50

def score_domain_centrality(lemma: str, domain: str) -> float:
    """Is this lemma central to its semantic domain?"""
    central_verbs = {
        "PROC_COOKING":  ["coquo", "decoquo"],
        "PROC_MIXING":   ["misceo", "admisceo"],
        "PROC_GRINDING": ["tero", "contero"],
        "PROC_ADDING":   ["infundo", "pono"],
    }
    if domain in central_verbs and lemma in central_verbs[domain]:
        return 1.0
    # Peripheral, but still in domain
    return 0.5

def score_lemma_specificity(lemma: str) -> float:
    """Prefer specific actions over generic ones."""
    generic_verbs = ["pono", "facio", "do"]
    if lemma in generic_verbs:
        return 0.3
    return 1.0

# ---------------------------------------------------------------------
# Compute scores
# ---------------------------------------------------------------------
print("[s97(py)] Computing component scores...", file=sys.stderr)
rows = []

for _, row in df.iterrows():
    stem = str(row["stem"])
    lemma = str(row["lemma_latin"])
    domain = str(row["latin_domain"])
    try:
        freq = float(row["corpus_freq"])
    except Exception:
        freq = 0.0

    freq_score = score_corpus_frequency(freq)
    form_score = score_form_similarity(stem, lemma)
    domain_score = score_domain_centrality(lemma, domain)
    spec_score = score_lemma_specificity(lemma)

    total_score = (
        0.20 * freq_score +
        0.05 * form_score +
        0.40 * domain_score +
        0.35 * spec_score
    )

    rows.append({
        "stem": stem,
        "functional_label": row["functional_label"],
        "lemma_latin": lemma,
        "gloss_en": row["gloss_en"],
        "latin_domain": domain,
        "corpus_freq": freq,
        "freq_score": round(freq_score, 3),
        "form_score": round(form_score, 3),
        "domain_score": round(domain_score, 3),
        "spec_score": round(spec_score, 3),
        "total_score": round(total_score, 3),
    })

scores_df = pd.DataFrame(rows)
scores_df = scores_df.sort_values(["stem", "total_score"], ascending=[True, False])
scores_df.to_csv(out_scored, sep="\t", index=False)
print(f"[s97(py)] Wrote scored candidates to {out_scored}", file=sys.stderr)

# ---------------------------------------------------------------------
# Selection with stem-frequency priority
# ---------------------------------------------------------------------
print("[s97(py)] Selecting winners per stem (frequency-prioritised)...", file=sys.stderr)

# Prepare stem frequency for all stems present in candidate list
stems = list(scores_df["stem"].unique())
stems_with_freq = []
for s in stems:
    f = stem_freq.get(s, 0)
    stems_with_freq.append((s, f))
# Sort by frequency DESC (highest frequency first)
stems_sorted = [s for s, _ in sorted(stems_with_freq, key=lambda x: x[1], reverse=True)]

selected = []
used_lemmas = set()

for stem in stems_sorted:
    stem_candidates = scores_df[scores_df["stem"] == stem]

    # Exclude lemmas already used elsewhere
    available = stem_candidates[~stem_candidates["lemma_latin"].isin(used_lemmas)]
    if available.empty:
        print(f"[s97(py)] {stem}: no available lemmas (all used)", file=sys.stderr)
        continue

    # Apply minimum total_score threshold
    viable = available[available["total_score"] >= 0.50]
    if viable.empty:
        print(f"[s97(py)] {stem}: no viable candidates (all <0.50)", file=sys.stderr)
        continue

    winner = viable.iloc[0]

    # Confidence calibration from total_score
    ts = float(winner["total_score"])
    if ts >= 0.75:
        confidence = "MEDIUM-HIGH"
    elif ts >= 0.60:
        confidence = "MEDIUM"
    elif ts >= 0.50:
        confidence = "LOW-MEDIUM"
    else:
        confidence = "LOW"

    # Form-based downgrading (as per S80–S83)
    form_score = float(winner["form_score"])
    note = ""
    if form_score < 0.60:
        if confidence == "MEDIUM-HIGH":
            confidence = "MEDIUM"
            note = "downgraded: weak form support"
        elif confidence == "MEDIUM":
            confidence = "LOW-MEDIUM"
            note = "downgraded: weak form support"
        else:
            note = "weak form support"

    selected.append({
        "stem": stem,
        "functional_label": winner["functional_label"],
        "lemma_latin": winner["lemma_latin"],
        "gloss_en": winner["gloss_en"],
        "latin_domain": winner["latin_domain"],
        "corpus_freq": int(winner["corpus_freq"]),
        "freq_score": winner["freq_score"],
        "form_score": winner["form_score"],
        "domain_score": winner["domain_score"],
        "spec_score": winner["spec_score"],
        "total_score": winner["total_score"],
        "voynich_stem_freq": stem_freq.get(stem, 0),
        "confidence": confidence,
        "note": note,
    })

    used_lemmas.add(winner["lemma_latin"])

    print(
        f"[s97(py)] {stem} (n={stem_freq.get(stem,0)}) → "
        f"{winner['lemma_latin']} (score={winner['total_score']}, conf={confidence})",
        file=sys.stderr,
    )

selected_df = pd.DataFrame(selected)
selected_df = selected_df.sort_values("total_score", ascending=False)
selected_df.to_csv(out_selected, sep="\t", index=False)

print(f"[s97(py)] Selected {len(selected_df)} stems for T3 lexicon", file=sys.stderr)
print("[s97(py)] Confidence distribution:", file=sys.stderr)
if not selected_df.empty:
    print(selected_df["confidence"].value_counts().to_string(), file=sys.stderr)
PY

echo "[s97] Done. Top of selected T3 lexicon with stem frequencies:"
echo "----------------------------------------------------------------"
if [ -f "$OUT_SELECTED" ]; then
  head -20 "$OUT_SELECTED"
else
  echo "[s97] ERROR: Selected file not found: $OUT_SELECTED" >&2
fi
