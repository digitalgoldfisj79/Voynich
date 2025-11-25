# Analysis Scripts

This directory contains all scripts needed to reproduce the analyses in the manuscript.

## Directory Structure

```
scripts/
├── morphology/          # Morphological analysis (Tables 1-2)
├── compression/         # Compression testing (Tables 3-4)
├── fsm/                 # FSM grammar validation
└── verification/        # Table verification scripts
```

## Morphology Scripts (Tables 1-2)

### m01_extract_all_suffixes.py
**Generates Table 1: Suffix Inventory**
- Extracts 9-suffix system from Voynich corpus
- Counts suffix frequencies
- Calculates type-token statistics
- **Output:** `results/tables/m01_suffix_inventory.tsv`

### m06_extract_all_stems.py
**Extracts stem inventory**
- Identifies productive stems
- Used as input for stem-suffix combinations
- **Output:** `results/tables/m06_stem_inventory.tsv`

### m08_stem_suffix_combinations.py
**Generates Table 2: Stem Paradigms**
- Combines stems with suffixes
- Shows paradigm productivity
- **Output:** `results/tables/m08_stem_suffix_combinations.tsv`

### m05_suffix_productivity.py
**Type-frequency correlation analysis**
- Tests Zipf's law on suffixes
- **Generates r = 0.89 correlation reported in manuscript**
- **Output:** `results/tables/m05_productivity_correlation.tsv`

## Compression Scripts (Tables 3-4)

### c12_systematic_compression_tests.py
**Main compression test suite**
- Tests ALL compression models systematically
- Implements aggressive, tuned, minimal variants
- Compares against Voynich distribution
- **This is the primary compression analysis script**

### c14_tuned_collapse.py
**Best-fit compression model**
- Tuned to match Voynich 38.4% y-suffix distribution
- Many-to-one Latin → Voynich suffix mapping
- **Best performing model in Table 4**

### c10_occitan_compression.py
**Occitan vernacular testing**
- Applies compression to medieval Occitan
- Tests vernacular hypothesis
- **Key script for Occitan comparison**

### c09_morphological_merger.py
**Morphological class merging**
- Merges Latin morphological classes
- Creates many-to-one mappings
- Used in compression models

### Other compression scripts:
- `c05_smart_compression.py` - Smart compression algorithm
- `c06_proper_comparison.py` - Statistical comparison
- `c08_final_test.py` - Final compression testing
- `c11_occitan_proper_test.py` - Proper Occitan testing
- `c13_minimal_collapse.py` - Minimal compression model
- `c01_compare_compression.sh` - Shell script for token-level stats

## FSM Scripts

### p69_validate.py
**FSM grammar validation**
- Validates 109-rule FSM on held-out stems
- Calculates coverage and accuracy
- **Generates FSM performance metrics in manuscript**
- **Output:** `results/fsm/p69_rules_final.tsv`, `results/fsm/p69_summary.json`

### score_rulebook.py
**FSM rule scoring**
- Scores individual FSM rules
- Identifies high-performing patterns

## Master Analysis Script

### do_real_work.py (root directory)
**Main analysis pipeline**
- Loads all corpora (Voynich, Latin, Occitan)
- Extracts suffix distributions
- Runs bootstrap resampling (1,000 iterations)
- Computes chi-squared tests
- Calculates effect sizes
- Generates figures
- **This script orchestrates the full analysis**

## Running the Analysis

### Full Pipeline
```bash
python run_all_analyses.py
```

### Individual Components
```bash
# Morphology
python scripts/morphology/m01_extract_all_suffixes.py
python scripts/morphology/m08_stem_suffix_combinations.py

# Compression
python scripts/compression/c12_systematic_compression_tests.py
python scripts/compression/c14_tuned_collapse.py

# FSM
python scripts/fsm/p69_validate.py

# Master analysis
python do_real_work.py
```

### Verification Only
```bash
python run_all_analyses.py --verify
```

## Dependencies

All scripts require:
- Python 3.8+
- numpy
- pandas
- scipy
- matplotlib

Install with:
```bash
pip install -r requirements.txt
```

## Data Files

Scripts expect data in:
```
data/
├── voynich_tokens.txt
├── latin_abbrev_expanded.txt
├── occitan_medieval_stems.txt
└── enriched_translations.tsv
```

## Output Structure

```
results/
├── tables/              # CSV/TSV tables for manuscript
│   ├── m01_suffix_inventory.tsv
│   ├── m08_stem_suffix_combinations.tsv
│   └── ...
├── fsm/                 # FSM validation results
│   ├── p69_rules_final.tsv
│   └── p69_summary.json
└── hoax/                # Pre-computed hoax testing results
    ├── rugg_basic.tsv
    ├── rugg_markov.tsv
    └── ...
```

## Notes

- All scripts are from the original analysis conducted 2024-2025
- These are the ACTUAL scripts used to generate manuscript results
- No simulations or mock data - all real analyses
- Pre-computed results in `results/hoax/` are from earlier analysis runs
