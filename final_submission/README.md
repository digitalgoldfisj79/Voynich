# Voynichese Grammar Analysis - Submission Package

**Manuscript Title:** Morphological and Grammatical Structure in Voynichese: Evidence from Finite-State Analysis and Cross-Linguistic Comparison

**Target Journal:** PLOS ONE

**Submission Date:** November 2025

---

## Package Contents

### Main Manuscript (1 file)
- `manuscript/MANUSCRIPT_PLOS_ONE_COMPLETE.md` - Full manuscript (~15,000 words)

### Supplements (5 files)
- `supplements/SUPPLEMENT_S6_FSM_RULES.md` - Complete FSM documentation
- `supplements/DATA_S1_FSM_RULES_109.tsv` - Machine-readable rules
- `supplements/FSM_RULES_QUICK_REFERENCE.md` - Usage instructions
- `supplements/SUFFIX_RECONCILIATION_COMPLETE.md` - Methodological notes
- `supplements/MANUSCRIPT_FSM_CLARIFICATION_NOTE.txt` - Methods clarification

### Figures
**Main Manuscript (4 figures):**
- `figures/fig4_1_zipf_curve.png` - Zipfian distribution
- `figures/fig6_1_entropy_mi_comparison.png` - Multi-language comparison
- `figures/fig8_1_directional_vectors.png` - Compression falsification
- `figures/figA2_null_distribution.png` - Hoax falsification

**Supplementary (5 figures):**
- `figures/figA1_reproducibility.png` - Pipeline verification
- `figures/figB1_transliteration_correlation.png` - EVA vs STA1
- `figures/figC1_cooccurrence_network.png` - Token network
- `figures/fig2_1_pipeline.png` - Processing pipeline
- `figures/fig2_5_prefix_suffix_heatmap.png` - Morphological patterns

### Data Files
- `data/p69_rules_final.json` - Complete FSM rules (JSON)
- `data/p69_summary.json` - Validation summary
- `data/p69_validate.py` - Validation script
- `data/score_rulebook.py` - Scoring algorithm

---

## Key Findings

1. **FSM Grammar:** 109-rule finite-state machine (79.3% coverage, 72.4% accuracy)
2. **Morphology:** 9-suffix productive system (78.2% token coverage)
3. **Compression:** All models rejected across Romance languages (p<0.001)
4. **Hoax Falsification:** Synthetic controls systematically distinguished (p<10⁻²⁰⁰)
5. **Register Variation:** Currier A/B differ in frequency but share grammar

---

## Statistics Summary

- Corpus: 29,688 tokens (Voynich Manuscript)
- FSM Rules: 109 (validated on 900-stem test set)
- Morphological Suffixes: 9 productive types
- Compression Models: 6 tested (all rejected)
- Hoax Controls: 3 generated (all falsified)

---

## Reproducibility

All analysis code, data, and validation scripts included in `data/` directory.

**Checksums:**
- Rules: SHA-256 verified
- Validation: 10,000-iteration bootstrap
- Random seed: 42 (all stochastic processes)

---

## File Organization
final_submission/
├── README.md (this file)
├── manuscript/
│   └── MANUSCRIPT_PLOS_ONE_COMPLETE.md
├── supplements/
│   ├── SUPPLEMENT_S6_FSM_RULES.md
│   ├── DATA_S1_FSM_RULES_109.tsv
│   └── [3 more files]
├── figures/
│   ├── fig4_1_zipf_curve.png
│   └── [8 more figures]
└── data/
├── p69_rules_final.json
└── [validation files]
---

## Submission Checklist

- [x] Main manuscript (15,000 words)
- [x] Supplement S6 (FSM rules)
- [x] Data S1 (machine-readable rules)
- [x] 4 main figures
- [x] 5 supplementary figures
- [x] Validation scripts
- [x] Reproducibility documentation

---

## Contact

Edward Bozzard
edwardbozzard@gmail.com

**Repository:** 
https://github.com/digitalgoldfisj79/voynich-morphology-compression/

---

## Version History

- v1.0 (Nov 2025): Initial submission to PLOS ONE
  - Phase 69 FSM validation
  - Conservative findings (no semantic claims)
  - Cross-linguistic baseline comparison

---

## Notes

- **Phase 70 experimental rules NOT included** (unvalidated)
- **Arabic/Hebrew compression NOT included** (methodological concerns)
- **Semantic analysis removed** (Option A: conservative approach)
- **MI₁ = 1.49 bits** (consistent throughout manuscript)

---

**Last Updated:** November 23, 2025
