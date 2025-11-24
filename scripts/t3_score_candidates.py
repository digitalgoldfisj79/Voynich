#!/usr/bin/env python3
import sys
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

T2_PATH   = BASE / "metadata" / "t2_stem_functional_lexicon.tsv"
CAND_PATH = BASE / "metadata" / "t3_candidates.tsv"
FORM_PATH = BASE / "metadata" / "t3_form_similarity_merged.tsv"
OUT_PATH  = BASE / "metadata" / "t3_lexical_lexicon.tsv.tmp"

CONF_LEVELS = ["LOW", "LOW-MEDIUM", "MEDIUM", "MEDIUM-HIGH", "HIGH", "DEMOTED"]

def cap_conf(current, max_level):
    """Cap confidence at a maximum level in CONF_LEVELS ordering."""
    if current not in CONF_LEVELS:
        return current
    if max_level not in CONF_LEVELS:
        return current
    if CONF_LEVELS.index(current) > CONF_LEVELS.index(max_level):
        return max_level
    return current

def main():
    # --- Load inputs ---------------------------------------------------------
    try:
        t2 = pd.read_csv(T2_PATH, sep="\t")
    except FileNotFoundError:
        print(f"[t3_score] ERROR: Could not find {T2_PATH}", file=sys.stderr)
        sys.exit(1)

    try:
        cand = pd.read_csv(CAND_PATH, sep="\t")
    except FileNotFoundError:
        print(f"[t3_score] ERROR: Could not find {CAND_PATH}", file=sys.stderr)
        sys.exit(1)

    # T2 lexicon: we expect at least: stem, functional_label, confidence
    # Normalise column names a bit
    cols_lower = {c: c.lower() for c in t2.columns}
    t2.columns = [cols_lower[c] for c in t2.columns]

    # Ensure we have these names
    if "stem" not in t2.columns:
        print("[t3_score] ERROR: t2 lexicon has no 'stem' column", file=sys.stderr)
        sys.exit(1)
    if "functional_label" not in t2.columns:
        # Try to recover from e.g. 'functional' or 't2_label'
        for alt in ["functional", "t2_label", "t2_functional_label"]:
            if alt in t2.columns:
                t2 = t2.rename(columns={alt: "functional_label"})
                break
    if "functional_label" not in t2.columns:
        print("[t3_score] WARNING: no 'functional_label' in t2; cluster rule will ignore function", file=sys.stderr)

    if "confidence" not in t2.columns:
        # Fallback if stored as e.g. 't2_confidence'
        for alt in ["t2_confidence", "t2_conf"]:
            if alt in t2.columns:
                t2 = t2.rename(columns={alt: "confidence"})
                break

    # --- Load form similarity (may be absent / partial) ---------------------
    try:
        form = pd.read_csv(FORM_PATH, sep="\t")
        if "stem" not in form.columns:
            raise ValueError("form similarity file has no 'stem' column")
        # Assume one row per stem after s84; if not, first row per stem
        form_by_stem = form.drop_duplicates("stem").set_index("stem").to_dict(orient="index")
    except Exception as e:
        print(f"[t3_score] WARNING: could not load form similarity ({e}); using neutral scores.", file=sys.stderr)
        form_by_stem = {}

def safe_float(val, default):
    """
    Try to parse a float, otherwise return a neutral default.
    This protects us from bad / misaligned form-similarity rows like 'quarto'.
    """
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def get_form_scores(stem):
    """
    Look up precomputed form similarity scores for a stem.

    Returns:
        (form_char_cosine, form_edit_similarity, form_combined, form_rank)
    All values are robust: if anything is missing or non-numeric,
    we fall back to neutral defaults (0.5 for scores, 999 for rank).
    """
    row = form_dict.get(stem)
    if row is None:
        # Stem not in form-similarity table → treat as neutral
        return 0.5, 0.5, 0.5, 999

    # Prefer our explicitly merged columns; fall back to raw s80–s83 names
    cos = safe_float(
        row.get("form_char_cosine", row.get("char_cosine", 0.5)),
        0.5,
    )
    edit = safe_float(
        row.get("form_edit_similarity", row.get("edit_similarity", 0.5)),
        0.5,
    )
    comb = safe_float(
        row.get("form_combined", row.get("combined_score", 0.5)),
        0.5,
    )
    rank = int(
        safe_float(
            row.get("form_rank", row.get("rank", 999)),
            999,
        )
    )

    return cos, edit, comb, rank

    # --- Merge T2 info onto candidates --------------------------------------
    # normalise cand column names only lightly (keep originals mostly)
    if "stem" not in cand.columns:
        print("[t3_score] ERROR: t3_candidates.tsv has no 'stem' column", file=sys.stderr)
        sys.exit(1)

    merged = cand.merge(
        t2[["stem", "functional_label", "confidence"]],
        on="stem",
        how="left",
        suffixes=("", "_t2")
    )

    # rename for clarity
    if "confidence_t2" in merged.columns:
        merged = merged.rename(columns={"confidence_t2": "t2_confidence"})
    else:
        # t2 confidence may already be called 'confidence' from t2
        if "confidence" in t2.columns and "t2_confidence" not in merged.columns:
            merged = merged.rename(columns={"confidence": "t2_confidence"})

    # --- Scoring weights -----------------------------------------------------
    # New weights (sum to 1.0)
    W_SEM   = 0.40   # semantic_score
    W_CORP  = 0.20   # corpus_score
    W_CTX   = 0.20   # context_score (neutral if missing)
    W_POS   = 0.15   # pos_match_score (neutral if missing)
    W_FORM  = 0.05   # form_combined

    out_rows = []

    for _, row in merged.iterrows():
        stem = str(row["stem"])

        # basic scores (fallback to neutral=0.5 if missing)
        sem_score = float(row["semantic_score"]) if "semantic_score" in row.index and pd.notna(row["semantic_score"]) else 0.5
        corp_score = float(row["corpus_score"]) if "corpus_score" in row.index and pd.notna(row["corpus_score"]) else 0.5

        ctx_score = float(row["context_score"]) if "context_score" in row.index and pd.notna(row["context_score"]) else 0.5
        pos_score = float(row["pos_match_score"]) if "pos_match_score" in row.index and pd.notna(row["pos_match_score"]) else 0.5

        form_cos, form_edit, form_comb, form_rank = get_form_scores(stem)

        # lexical score with new weights
        lexical_score = (
            W_SEM  * sem_score +
            W_CORP * corp_score +
            W_CTX  * ctx_score +
            W_POS  * pos_score +
            W_FORM * form_comb
        )

        # --- initial confidence from lexical_score -------------------------
        if lexical_score >= 0.85:
            conf = "HIGH"
        elif lexical_score >= 0.75:
            conf = "MEDIUM-HIGH"
        elif lexical_score >= 0.70:
            conf = "MEDIUM"
        elif lexical_score >= 0.60:
            conf = "LOW-MEDIUM"
        else:
            conf = "LOW"

        # --- cap by T2 confidence ------------------------------------------
        t2_conf = row.get("t2_confidence", None)
        if isinstance(t2_conf, str) and t2_conf in CONF_LEVELS:
            conf = cap_conf(conf, t2_conf)

        # --- apply form-based constraints ----------------------------------
        form_effect = ""
        if form_comb < 0.60:
            # cannot claim HIGH without form support
            if conf == "HIGH":
                conf = "MEDIUM-HIGH"
                form_effect = "DOWNGRADE: weak form support (<0.60)"
            if form_comb < 0.50 and conf in ["MEDIUM-HIGH", "MEDIUM"]:
                conf = "LOW-MEDIUM"
                form_effect = "DOWNGRADE: very weak form support (<0.50)"

        # Optional boost for very short stems with very strong form match
        if len(stem) <= 2 and form_comb >= 0.75 and conf in ["MEDIUM", "MEDIUM-HIGH"]:
            conf = "HIGH"
            form_effect = "BOOST: very strong form support on short stem"

        out_row = dict(row)  # start with all original candidate + T2 fields
        out_row["form_char_cosine"]   = form_cos
        out_row["form_edit_similarity"] = form_edit
        out_row["form_combined"]      = form_comb
        out_row["form_rank"]          = form_rank
        out_row["lexical_score"]      = lexical_score
        out_row["confidence"]         = conf
        out_row["form_confidence_effect"] = form_effect

        out_rows.append(out_row)

    scored = pd.DataFrame(out_rows)

    # --- one-lemma-per-functional cluster rule ------------------------------
    # If we have multiple stems competing for the same (lemma_latin, functional_label),
    # keep the highest lexical_score, demote others.
    cluster_cols = ["lemma_latin"]
    if "functional_label" in scored.columns:
        cluster_cols.append("functional_label")

    if all(c in scored.columns for c in cluster_cols):
        scored["cluster_key"] = scored[cluster_cols].astype(str).agg("||".join, axis=1)

        winners_idx = set()
        losers_idx  = set()

        for key, group in scored.groupby("cluster_key"):
            # ignore empty lemma slots
            if group["lemma_latin"].isna().all():
                continue
            if len(group) == 1:
                winners_idx.add(group.index[0])
                continue
            # pick winner by lexical_score
            max_idx = group["lexical_score"].idxmax()
            winners_idx.add(max_idx)
            for idx in group.index:
                if idx == max_idx:
                    continue
                losers_idx.add(idx)

        # Demote losers
        for idx in losers_idx:
            stem = scored.at[idx, "stem"]
            lemma = scored.at[idx, "lemma_latin"]
            scored.at[idx, "confidence"] = "DEMOTED"
            note = str(scored.at[idx, "notes"]) if "notes" in scored.columns else ""
            extra = f"demoted: secondary candidate for {lemma}; primary handled elsewhere"
            scored.at[idx, "notes"] = f"{note}; {extra}".strip("; ")
    else:
        print("[t3_score] NOTE: cluster columns missing; skipping one-lemma-per-cluster rule.", file=sys.stderr)

    # --- write output -------------------------------------------------------
    scored.to_csv(OUT_PATH, sep="\t", index=False)
    print(f"[t3_score] Wrote scored T3 lexicon to {OUT_PATH}")

if __name__ == "__main__":
    main()
