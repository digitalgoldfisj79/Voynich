#!/usr/bin/env sh
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
T3_IN="$BASE/metadata/t3_lexical_lexicon.tsv"
T3_OUT="$BASE/metadata/t3_lexical_lexicon_wave2.tsv"

echo "[s98] BASE: $BASE" >&2
echo "[s98] Input T3:  $T3_IN" >&2
echo "[s98] Output T3: $T3_OUT" >&2

if [ ! -f "$T3_IN" ]; then
  echo "[s98][ERROR] Missing T3 lexicon: $T3_IN" >&2
  exit 1
fi

awk -F'\t' -v OFS='\t' '
NR==1 {
  # Keep header as-is
  header = $0
  print $0
  next
}

# Drop any existing entries for these stems; we will replace them
($1=="qotar" || $1=="y" || $1=="s" || $1=="r" || $1=="l") { next }

{ print }

END {
  # NOTE: This assumes your columns are:
  # stem, semantic_family_stemlex, role_group_stemlex, primary_section,
  # structural_class_stemlex, lemma_latin, gloss_en, pos_t3,
  # confidence, lexical_score, rule_id, evidence, notes_t3
  #
  # If you have extra trailing columns, they will simply be empty.

  # 1) qotar – promoted PROC stem (lemma left blank for now)
  print "qotar", \
        "F_PROC_CORE", \
        "PROC", \
        "Recipes", \
        "CL_PROC_MIXED", \
        "", \
        "", \
        "V", \
        "MEDIUM", \
        "0.80", \
        "R_T3_WAVE2", \
        "Tests1-5: section_bias,PMI,role,pos,perm", \
        "Wave2: promoted morphologically; fill lemma_latin/gloss_en once Latin evidence is ready"

  # 2) y – generic botanical patient marker
  print "y", \
        "F_BOT_GENERIC_PATIENT", \
        "BOT", \
        "Herbal", \
        "CL_BOTANICAL", \
        "", \
        "", \
        "", \
        "LOW", \
        "0.50", \
        "R_T3_WAVE2", \
        "Tests1-5: BOT,PATIENT_CAND,Herbal-biased", \
        "Wave2: treat as generic botanical patient; no concrete Latin lemma yet"

  # 3) r – generic botanical agent marker
  print "r", \
        "F_BOT_GENERIC_AGENT", \
        "BOT", \
        "Recipes", \
        "CL_BOTANICAL", \
        "", \
        "", \
        "", \
        "LOW", \
        "0.50", \
        "R_T3_WAVE2", \
        "Tests1-5: BOT,AGENT_CAND,Recipes-biased", \
        "Wave2: treat as generic botanical agent; no concrete Latin lemma yet"

  # 4) s – generic ambiguous botanical marker
  print "s", \
        "F_BOT_GENERIC_AMBIG", \
        "BOT", \
        "Herbal", \
        "CL_BOTANICAL", \
        "", \
        "", \
        "", \
        "LOW", \
        "0.50", \
        "R_T3_WAVE2", \
        "Tests1-5: BOT,AMBIGUOUS,Herbal-biased", \
        "Wave2: generic botanical marker; reserved for pattern grammar, not lexical mapping"

  # 5) l – generic light procedural verb
  print "l", \
        "F_PROC_GENERIC_LIGHT", \
        "PROC", \
        "Recipes", \
        "CL_PROC_MIXED", \
        "", \
        "", \
        "V", \
        "LOW", \
        "0.50", \
        "R_T3_WAVE2", \
        "Tests1-5: PROC-only,Recipes-biased", \
        "Wave2: light procedural verb; used in pattern grammar; lemma_latin to be decided later"
}
' "$T3_IN" > "$T3_OUT"

echo "[s98] Wrote updated lexicon to $T3_OUT" >&2
echo "[s98] When happy, you can promote it over the old file, e.g.:" >&2
echo "      mv \"$T3_OUT\" \"$T3_IN\"" >&2
