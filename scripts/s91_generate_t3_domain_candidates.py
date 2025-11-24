#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
t2_path = BASE / "metadata" / "t2_stem_functional_lexicon.tsv"
lemma_path = BASE / "metadata" / "latin_lemmas_by_domain.tsv"
out_path = BASE / "metadata" / "t3_candidates_domains.tsv"

# --- 1. Load inputs ---
t2 = pd.read_csv(t2_path, sep="\t")
lemmas = pd.read_csv(lemma_path, sep="\t")

# Normalise column names just in case
t2.columns = [c.strip() for c in t2.columns]
lemmas.columns = [c.strip() for c in lemmas.columns]

# Expected columns:
# t2: stem, functional_label, confidence, ...
# lemmas: domain, lemma, gloss_en, frequency, source

# --- 2. Map T2 labels to lemma domains ---

domain_map = {
    "PROC_VERB": ["PROC_COOKING", "PROC_MIXING", "PROC_GRINDING", "PROC_ADDING"],
    "BOT_ENTITY": ["BOT_HERB"],   # extend later if you add BOT_TREE, BOT_FLOWER
    "BIO_STATE": ["BIO_FLUID"],   # extend later with BIO_SUBSTANCE if needed
}

# Only consider reasonably solid T2 labels
ELIGIBLE_CONF = {"HIGH", "MEDIUM"}

rows = []

for _, row in t2.iterrows():
    stem = str(row.get("stem", "")).strip()
    func = str(row.get("functional_label", "")).strip()
    conf = str(row.get("confidence", "")).strip().upper()

    if not stem:
        continue
    if func not in domain_map:
        # e.g. stems that are not PROC_VERB/BOT_ENTITY/BIO_STATE
        continue
    if conf not in ELIGIBLE_CONF:
        # skip low-confidence T2
        continue

    domains = domain_map[func]
    sub = lemmas[lemmas["domain"].isin(domains)].copy()
    if sub.empty:
        continue

    # sort by frequency (descending) and take top N
    # if frequency missing, treat as 0
    if "frequency" in sub.columns:
        sub["frequency"] = pd.to_numeric(sub["frequency"], errors="coerce").fillna(0)
        sub = sub.sort_values("frequency", ascending=False)
    topN = sub.head(8)  # tweak N if you want more/less

    for _, lrow in topN.iterrows():
        rows.append({
            "stem": stem,
            "t2_functional_label": func,
            "t2_confidence": conf,
            "latin_lemma": str(lrow.get("lemma", "")).strip(),
            "gloss_en": str(lrow.get("gloss_en", "")).strip(),
            "lemma_domain": str(lrow.get("domain", "")).strip(),
            "lemma_corpus_freq": int(lrow.get("frequency", 0)) if str(lrow.get("frequency", "")).strip() else 0,
            "lemma_source": str(lrow.get("source", "")).strip(),
            "candidate_source": "DOMAIN_MATCH_S91"
        })

if not rows:
    print("[s91] No candidates generated (check t2 and latin_lemmas_by_domain.tsv)")
    out_path.write_text("stem\t" +
                        "t2_functional_label\t" +
                        "t2_confidence\t" +
                        "latin_lemma\t" +
                        "gloss_en\t" +
                        "lemma_domain\t" +
                        "lemma_corpus_freq\t" +
                        "lemma_source\t" +
                        "candidate_source\n",
                        encoding="utf-8")
else:
    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_path, sep="\t", index=False)
    print(f"[s91] Wrote {len(out_df)} candidate rows to {out_path}")
