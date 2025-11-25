# Systematic Structural Analysis of the Voynich Manuscript

**Manuscript:** Falsification of Compression and Simple Hoax Hypotheses

**Repository:** Supporting data and code for manuscript submission

**Branch:** `paper-2025` (clean publication branch)

---

## Quick Start

```bash
# Clone repository and switch to publication branch
git clone https://github.com/digitalgoldfisj79/Voynich.git
cd Voynich
git checkout paper-2025

# Install dependencies
pip install -r requirements.txt

# Run complete analysis pipeline
python run_all_analyses.py
```

**Expected runtime:** ~30 minutes on standard laptop (2.5 GHz, 8GB RAM)

**Expected outputs:** All tables and statistics reported in manuscript

---

## Repository Structure

```
paper-2025/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
├── run_all_analyses.py      # Master script - reproduces everything
│
├── data/                     # Corpus files
│   ├── voynich_corpus.txt   # 29,688 tokens (ZL transcription)
│   ├── latin_corpus.txt     # 13,200 tokens (Dioscorides)
│   └── occitan_corpus.txt   # 7,004 tokens (medieval sources)
│
├── scripts/                  # Analysis scripts
│   ├── morphology/
│   │   ├── identify_productive_stems.py
│   │   └── type_frequency_correlation.py
│   ├── fsm/
│   │   ├── build_fsm.py
│   │   └── validate_fsm.py
│   ├── compression/
│   │   ├── compress_latin.py
│   │   ├── compress_occitan.py
│   │   └── evaluate_compression.py
│   ├── hoax/
│   │   ├── generate_rugg_controls.py
│   │   └── evaluate_discriminants.py
│   ├── baseline/
│   │   ├── normalize_corpus.py
│   │   └── compute_statistics.py
│   └── verification/
│       ├── verify_table1.py  # Suffix inventory
│       ├── verify_table2.py  # Stem paradigms
│       ├── verify_table3.py  # Compression examples
│       ├── verify_table4.py  # Compression results
│       └── verify_table5.py  # Hoax discriminants
│
└── results/                  # Generated outputs
    ├── tables/              # CSV files
    └── figures/             # PNG files
```

---

## Verification

Verify specific manuscript claims:

```bash
# Table 1: Suffix inventory (9 types, 78.6% coverage)
python scripts/verification/verify_table1.py

# Table 2: Stem paradigms (10 high-frequency stems)
python scripts/verification/verify_table2.py

# Table 3: Compression failures (Occitan examples)
python scripts/verification/verify_table3.py

# Table 4: Compression model performance (6 models)
python scripts/verification/verify_table4.py

# Table 5: Hoax discriminants (3 synthetic controls)
python scripts/verification/verify_table5.py
```

Each verification script outputs:
- ✓ or ✗ for each claim
- Actual values vs. manuscript claims
- Tolerance: ±0.01 for proportions, ±0.001 for p-values

---

## Key Results

### Morphological Analysis
- **9-suffix system:** -y (38.4%), NULL (21.8%), -aiin (9.8%), -ol (9.1%), -al (5.8%), -or (5.4%), -ain (4.5%), -ody (3.0%), -am (2.2%)
- **Coverage:** 78.6% of tokens (23,192 of 29,688)
- **Productive stems:** 270 stems with 3+ suffix variants
- **Type-frequency correlation:** r = 0.89, p < 0.001

### FSM Grammar
- **109 rules:** 42 left-position, 38 right-position, 29 distributional
- **Coverage:** 79.3% on 900 held-out stems
- **Accuracy:** 72.4% prediction accuracy
- **Conformance:** 93.8% ± 0.6% across all sections

### Compression Testing
- **6 models tested:** All failed (χ² p < 0.001)
- **Entropy-diversity constraint:** Mathematical impossibility identified
- **Combined rejection:** p < 10⁻¹⁵

### Hoax Falsification
- **3 synthetic controls:** Basic Grille, Enhanced Grille, Rule-Augmented
- **MI₁ deficits:** 18-30% below Voynichese
- **Morphological coverage:** 0-21% vs. 78.6% target
- **Combined rejection:** p < 10⁻²⁰⁰

---

## Data Sources

### Voynich Manuscript
- **Source:** ZL transcription (René Zandbergen, voynich.nu)
- **Format:** EVA (European Voynich Alphabet) notation
- **Tokens:** 29,688 (8,114 unique types)
- **Coverage:** 240 folios

### Medieval Latin
- **Source:** Dioscorides *De Materia Medica* (Perseus Digital Library)
- **Tokens:** 13,200
- **Content:** Medical/botanical (matches manuscript content)

### Medieval Occitan
- **Sources:** *Leys d'Amors*, *Ronsasvals* (14th century)
- **Tokens:** 7,004
- **Content:** Mixed genre (narrative, legal, procedural)

---

## Citation

If you use this code or data, please cite:

```
[Author information to be added]
Systematic Structural Analysis of the Voynich Manuscript: 
Falsification of Compression and Simple Hoax Hypotheses
[Journal, year, DOI to be added upon publication]
```

For the computational materials:

```
[Author information]
Voynich Manuscript Analysis - Publication Branch
GitHub: github.com/digitalgoldfisj79/Voynich/tree/paper-2025
[Zenodo DOI to be assigned]
```

---

## License

**Code:** MIT License (see LICENSE file)

**Data compilations:** CC-BY-4.0

**Voynich transcription:** CC0 (public domain, maintained by community)

---

## Contact

For questions about data, code, or reproduction:
- Open an issue: https://github.com/digitalgoldfisj79/Voynich/issues
- Email: [to be added]

We are committed to full computational reproducibility and will respond to all reasonable inquiries.

---

## Reproducibility Statement

This repository enables complete reproduction of all results in the manuscript:

✓ All corpus data included  
✓ All analysis scripts documented  
✓ All parameters specified  
✓ All random seeds fixed  
✓ Expected outputs documented  
✓ Verification scripts provided  

**No results in the manuscript require external data or closed-source tools.**

---

## Manuscript Sections → Scripts Mapping

| Manuscript Section | Script | Output |
|-------------------|--------|--------|
| Morphological Analysis (Table 1) | `scripts/morphology/identify_productive_stems.py` | `results/tables/table1_suffix_inventory.csv` |
| Stem Paradigms (Table 2) | `scripts/morphology/identify_productive_stems.py` | `results/tables/table2_stem_paradigms.csv` |
| FSM Construction | `scripts/fsm/build_fsm.py` | `results/fsm_rules_109.json` |
| FSM Validation | `scripts/fsm/validate_fsm.py` | `results/tables/fsm_performance.csv` |
| Compression Testing (Table 3-4) | `scripts/compression/evaluate_compression.py` | `results/tables/table3_examples.csv`, `table4_models.csv` |
| Hoax Testing (Table 5) | `scripts/hoax/evaluate_discriminants.py` | `results/tables/table5_discriminants.csv` |

---

## Technical Requirements

**Python:** 3.8 or higher

**Required packages:** See requirements.txt

**Disk space:** ~500 MB (data + results)

**Memory:** 4 GB minimum, 8 GB recommended

**OS:** Linux, macOS, or Windows (with bash for shell scripts)

---

## Troubleshooting

**Problem:** `ModuleNotFoundError` when running scripts  
**Solution:** Ensure all dependencies installed: `pip install -r requirements.txt`

**Problem:** Different numerical results (within rounding error)  
**Solution:** This is expected due to floating-point precision. Differences < 0.01 are acceptable.

**Problem:** Verification script fails  
**Solution:** Check that you're running from repository root and data files are present.

**Problem:** Long runtime (>1 hour)  
**Solution:** Some analyses are computationally intensive. Consider running on faster machine or reducing sample size in configuration.

---

**Last updated:** November 2025  
**Version:** 1.0 (Publication)
