#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

# Use FILTERED candidates if present, else fall back to curated
CAND_FILTERED="$BASE/metadata/t3_candidates_domains_filtered.tsv"
CAND_CURATED="$BASE/metadata/t3_candidates_domains_curated.tsv"

if [ -f "$CAND_FILTERED" ]; then
  CANDIDATES="$CAND_FILTERED"
  echo "[s97] Using FILTERED candidates: $CANDIDATES"
else
  CANDIDATES="$CAND_CURATED"
  echo "[s97] WARNING: Filtered candidates not found; using CURATED: $CANDIDATES"
fi

FORM_SIM="$BASE/PhaseT/out/s83_charonly_fixed.tsv"
STEM_FREQ="$BASE/metadata/t03_stem_frequencies.tsv"
OUT_SCORED="$BASE/PhaseT/out/t3_candidates_scored_freq.tsv"
OUT_SELECTED="$BASE/PhaseT/out/t3_lexicon_selected_freq.tsv"

echo "[s97] BASE:        $BASE"
echo "[s97] Candidates:  $CANDIDATES"
echo "[s97] Form sim:    $FORM_SIM (optional)"
echo "[s97] Stem freq:   $STEM_FREQ (optional)"
echo "[s97] Scored out:  $OUT_SCORED"
echo "[s97] Selected out:$OUT_SELECTED"

mkdir -p "$BASE/PhaseT/out"

python3 - "$CANDIDATES" "$FORM_SIM" "$STEM_FREQ" "$OUT_SCORED" "$OUT_SELECTED" << 'PY'
import sys, math
import pandas as pd

candidates_path = sys.argv[1]
form_path       = sys.argv[2]
stemfreq_path   = sys.argv[3]
out_scored      = sys.argv[4]
out_selected    = sys.argv[5]

print(f"[s97(py)] Loading candidates from: {candidates_path}", file=sys.stderr)
df = pd.read_csv(candidates_path, sep='\t')
print(f"[s97(py)] Loaded {len(df)} candidate rows", file=sys.stderr)

# --- Form similarity ---
form_dict = {}
try:
    form_df = pd.read_csv(form_path, sep='\t')
    for _, row in form_df.iterrows():
        key = (row['stem'], row['latin_token'])
        form_dict[key] = row['char_cosine']
    print(f"[s97(py)] Loaded {len(form_dict)} form similarity scores", file=sys.stderr)
except Exception as e:
    print(f"[s97(py)] Form similarity not available ({e}); using neutral scores", file=sys.stderr)

# --- Stem frequencies ---
stem_freq = {}
try:
    sf = pd.read_csv(stemfreq_path, sep='\t')
    # Expect columns: stem, stem_freq
    if not {'stem','stem_freq'}.issubset(sf.columns):
        raise ValueError(f"Could not uniquely identify frequency column in {stemfreq_path}: {list(sf.columns)}")
    for _, row in sf.iterrows():
        stem_freq[row['stem']] = int(row['stem_freq'])
    print(f"[s97(py)] Loaded stem frequencies for {len(stem_freq)} stems", file=sys.stderr)
except Exception as e:
    print(f"[s97(py)] Stem frequencies not available ({e}); defaulting to 0", file=sys.stderr)

def score_corpus_frequency(freq):
    if freq <= 0:
        return 0.0
    return min(1.0, math.log10(freq + 1) / 2.0)

def score_form_similarity(stem, lemma):
    key = (stem, lemma)
    return form_dict.get(key, 0.50)

def score_domain_centrality(lemma, domain):
    central_verbs = {
        'PROC_COOKING':  ['coquo', 'decoquo'],
        'PROC_MIXING':   ['misceo', 'admisceo'],
        'PROC_GRINDING': ['tero', 'contero'],
        'PROC_ADDING':   ['infundo', 'pono'],
        'BOT_HERB':      ['ruta', 'rosa', 'mentha', 'anethum', 'apium', 'petroselinum', 'salvia'],
        'BIO_FLUID':     ['aqua', 'oleum', 'succus', 'humor', 'mel', 'acetum'],
    }
    if domain in central_verbs and lemma in central_verbs[domain]:
        return 1.0
    return 0.5

def score_lemma_specificity(lemma):
    generic = {'pono', 'facio', 'do'}
    return 0.3 if lemma in generic else 1.0

rows = []
for _, row in df.iterrows():
    stem   = row['stem']
    lemma  = row['lemma_latin']
    domain = row['latin_domain']
    freq   = float(row['corpus_freq'])

    freq_score   = score_corpus_frequency(freq)
    form_score   = score_form_similarity(stem, lemma)
    domain_score = score_domain_centrality(lemma, domain)
    spec_score   = score_lemma_specificity(lemma)

    total_score = (
        0.20 * freq_score +
        0.05 * form_score +
        0.40 * domain_score +
        0.35 * spec_score
    )

    rows.append({
        'stem': stem,
        'functional_label': row['functional_label'],
        'lemma_latin': lemma,
        'gloss_en': row['gloss_en'],
        'latin_domain': domain,
        'corpus_freq': freq,
        'freq_score': round(freq_score, 3),
        'form_score': round(form_score, 3),
        'domain_score': round(domain_score, 3),
        'spec_score': round(spec_score, 3),
        'total_score': round(total_score, 3),
    })

scores_df = pd.DataFrame(rows)
scores_df = scores_df.sort_values(['stem','total_score'], ascending=[True, False])
scores_df.to_csv(out_scored, sep='\t', index=False)
print(f"[s97(py)] Wrote scored candidates to {out_scored}", file=sys.stderr)

print("[s97(py)] Selecting winners with stem-frequency priority...", file=sys.stderr)

# stem-frequency order
unique_stems = scores_df['stem'].unique().tolist()
unique_stems.sort(key=lambda s: stem_freq.get(s, 0), reverse=True)

selected = []
used_lemmas = set()

for stem in unique_stems:
    sfreq = stem_freq.get(stem, 0)
    stem_cands = scores_df[scores_df['stem'] == stem]
    avail = stem_cands[~stem_cands['lemma_latin'].isin(used_lemmas)]
    if avail.empty:
        print(f"[s97(py)] {stem}: no available lemmas (all used)", file=sys.stderr)
        continue

    viable = avail[avail['total_score'] >= 0.50]
    if viable.empty:
        print(f"[s97(py)] {stem}: no viable candidates (all <0.50)", file=sys.stderr)
        continue

    winner = viable.iloc[0]

    ts = winner['total_score']
    if ts >= 0.75:
        confidence = 'MEDIUM-HIGH'
    elif ts >= 0.60:
        confidence = 'MEDIUM'
    elif ts >= 0.50:
        confidence = 'LOW-MEDIUM'
    else:
        confidence = 'LOW'

    note = ''
    if winner['form_score'] < 0.60:
        if confidence == 'MEDIUM-HIGH':
            confidence = 'MEDIUM'
        elif confidence == 'MEDIUM':
            confidence = 'LOW-MEDIUM'
        note = 'downgraded: weak form support'

    selected.append({
        'stem': stem,
        'functional_label': winner['functional_label'],
        'lemma_latin': winner['lemma_latin'],
        'gloss_en': winner['gloss_en'],
        'latin_domain': winner['latin_domain'],
        'corpus_freq': winner['corpus_freq'],
        'stem_freq': sfreq,
        'freq_score': winner['freq_score'],
        'form_score': winner['form_score'],
        'domain_score': winner['domain_score'],
        'spec_score': winner['spec_score'],
        'total_score': winner['total_score'],
        'confidence': confidence,
        'note': note,
    })

    used_lemmas.add(winner['lemma_latin'])
    print(f"[s97(py)] {stem} (stem_freq={sfreq}) \u2192 {winner['lemma_latin']} "
          f"(score={winner['total_score']:.3f}, conf={confidence})", file=sys.stderr)

selected_df = pd.DataFrame(selected)
selected_df = selected_df.sort_values('total_score', ascending=False)
selected_df.to_csv(out_selected, sep='\t', index=False)

print(f"[s97(py)] Selected {len(selected_df)} stems for T3 lexicon (freq-priority)", file=sys.stderr)
print(f"[s97(py)] Confidence distribution:", file=sys.stderr)
print(selected_df['confidence'].value_counts().to_string(), file=sys.stderr)
PY

echo "[s97] Done. Top of selected T3 lexicon (freq-priority):"
echo "------------------------------------------------------"
column -t -s $'\t' "$OUT_SELECTED" | head -20
echo "[s97] Full results:"
echo "  Scored:   $OUT_SCORED"
echo "  Selected: $OUT_SELECTED"
