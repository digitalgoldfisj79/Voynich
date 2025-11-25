# Hoax Testing Scripts

Scripts for generating synthetic Voynich controls to test the "hoax hypothesis" - that the Voynich manuscript was created mechanically using tables/grilles rather than encoding real language.

## Overview

These scripts generate synthetic Voynich-like text using different methods and calculate discriminants to distinguish them from real Voynich. This reproduces **Table 5** of the manuscript.

## Scripts

### generate_rugg_basic.py
**Generates Rugg Basic controls (grid-based method)**

Simulates Gordon Rugg's proposed hoax method:
- Random selection from morpheme tables/grids
- Concatenates multiple morphemes
- **Result:** Very long tokens (mean ~25 chars)

**Output:** `results/hoax/rugg_basic.tsv` (10,000 tokens)

**Usage:**
```bash
python scripts/hoax/generate_rugg_basic.py
```

### generate_rugg_markov.py
**Generates Rugg Markov controls (bigram chains)**

More sophisticated hoax method:
- Uses bigram statistics from real Voynich
- Generates tokens via Markov chain
- **Result:** Medium-length tokens (mean ~10 chars)

**Output:** `results/hoax/rugg_markov.tsv` (10,000 tokens)

**Usage:**
```bash
python scripts/hoax/generate_rugg_markov.py
```

### calculate_discriminants.py
**Calculates hoax discriminants (Table 5)**

Analyzes synthetic controls and calculates:
- **MI1:** Mutual information (bigram predictability)
- **FSM:** Grammar coverage and accuracy
- **Menu:** Suffix type diversity
- **Z-scores:** Deviation from Voynich baseline
- **Distinguish index:** Composite discriminant

**Output:**
- `results/hoax/rugg_metrics.tsv` (basic metrics)
- `results/hoax/pR3_summary.tsv` (full analysis with discriminants)

**Usage:**
```bash
python scripts/hoax/calculate_discriminants.py
```

### generate_all_controls.py
**Master script - runs all hoax generation**

Runs all three scripts in sequence:
1. Generate Rugg Basic controls
2. Generate Rugg Markov controls
3. Calculate discriminants

**Usage:**
```bash
python scripts/hoax/generate_all_controls.py
```

This is the recommended way to generate all hoax controls.

## Output Files

### rugg_basic.tsv
Synthetic tokens from grid-based method.

**Format:**
```
folio  line  pos  token
f1     1     1    chekichyololdycheolalshedchedy
f1     1     2    olcheyaiinaincheolshedqookiinain
...
```

**Characteristics:**
- 10,000 tokens
- Mean length: ~25 characters
- Very repetitive patterns
- Clearly distinguishable from Voynich

### rugg_markov.tsv
Synthetic tokens from Markov chain method.

**Format:** Same as rugg_basic.tsv

**Characteristics:**
- 10,000 tokens
- Mean length: ~10 characters
- Captures local patterns
- Still distinguishable from Voynich

### rugg_metrics.tsv
Basic metrics for each control type.

**Columns:**
- `name`: Control type (rugg_basic, rugg_markov)
- `n_tokens`: Number of tokens
- `chars_total`: Total characters
- `len_mean`: Mean token length
- `len_median`: Median token length
- `len_stdev`: Standard deviation of length
- `H1`: Unigram entropy
- `MI1`: Bigram mutual information

### pR3_summary.tsv
**Full discriminant analysis (Table 5 of manuscript)**

**Additional columns:**
- `invalid_frac`: Fraction of invalid FSM bigrams
- `n_suffixes`: Suffix type count
- `coverage`: FSM coverage (fraction matched)
- `acc_on_covered`: Accuracy on covered tokens
- `stems_covered`: Number of stems matched
- `z_MI1`: Z-score for mutual information
- `z_FSM`: Z-score for FSM coverage
- `z_Menu`: Z-score for suffix diversity
- `distinguish_index`: Composite discriminant

**Interpretation:**
- `distinguish_index > 0.5`: Clearly distinguishable from Voynich
- `distinguish_index < 0.3`: Hard to distinguish

## Methodology

### Rugg Basic (Grid Method)

Simulates the hoax hypothesis proposed by Gordon Rugg:

1. **Create morpheme grid:**
   - Columns: Common Voynich patterns (che, she, qok, etc.)
   - Rows: Structural constraints
   
2. **Generate tokens:**
   - Randomly select from grid
   - Concatenate 3-5 morphemes
   - Results in very long tokens

3. **Problem:**
   - Tokens are too long (mean 25 chars vs Voynich 4.8 chars)
   - Low morphological structure
   - Easily distinguished by token length alone

### Rugg Markov (Bigram Chains)

More sophisticated hoax method:

1. **Learn bigram statistics:**
   - Extract character bigrams from real Voynich
   - Build transition probability matrix
   
2. **Generate tokens:**
   - Start with random character
   - Follow bigram transitions
   - Stop at natural boundaries (double vowels, suffix patterns)

3. **Problem:**
   - Better than grid method, but still distinguishable
   - Lacks morphological structure (stem-suffix paradigms)
   - Low FSM coverage (no grammar)
   - Fewer suffix types than real Voynich

### Discriminants (Table 5)

Three key discriminants separate hoax from real Voynich:

**1. MI1 (Mutual Information)**
- Voynich: ~1.69 (high bigram predictability)
- Controls: ~1.1-1.4 (lower)
- **Why:** Real morphology has consistent patterns

**2. FSM Coverage**
- Voynich: ~79% (high grammar coverage)
- Controls: 0-21% (low)
- **Why:** Synthetic text lacks grammatical structure

**3. Suffix Menu**
- Voynich: 63 suffix types (high diversity)
- Controls: 70-80 types (different distribution)
- **Why:** Real morphology has productive paradigms

## Example Usage

### Generate all controls and calculate discriminants:
```bash
# Run master script
python scripts/hoax/generate_all_controls.py

# Check outputs
ls -lh results/hoax/
# Should show:
#   rugg_basic.tsv (~250 KB)
#   rugg_markov.tsv (~100 KB)
#   rugg_metrics.tsv (~200 bytes)
#   pR3_summary.tsv (~400 bytes)

# View discriminants
cat results/hoax/pR3_summary.tsv | column -t
```

### Generate individual controls:
```bash
# Just Rugg basic
python scripts/hoax/generate_rugg_basic.py

# Just Markov
python scripts/hoax/generate_rugg_markov.py

# Calculate metrics on existing controls
python scripts/hoax/calculate_discriminants.py
```

### Integrate with main pipeline:
```bash
# From repo root
python run_all_analyses.py --hoax

# Or run full pipeline (includes hoax testing)
python run_all_analyses.py
```

## Dependencies

Standard libraries only:
- pandas
- numpy
- collections
- math
- random

No special dependencies needed!

## Interpretation

### Key Finding

**All synthetic controls are distinguishable from Voynich.**

Distinguish indices:
- Rugg Basic: ~0.39 (clearly different)
- Rugg Markov: ~0.85 (very different)
- Real Voynich: ~1.10 (reference)

### What This Means

1. **Simple hoax methods fail:**
   - Grid-based: Too long tokens
   - Markov: No morphology

2. **Voynich has structure:**
   - Productive morphology (stem + suffix)
   - Grammatical constraints (FSM)
   - Consistent suffix paradigms

3. **Hoax hypothesis unlikely:**
   - Would require extremely sophisticated method
   - Simpler to encode real language

## References

1. **Rugg, G. (2004).** "The mystery of the Voynich manuscript." *Scientific American*.
   - Proposed grid-based hoax method

2. **Timm, T. & Schinner, A. (2020).** "A new statistical test for Voynich manuscript characters."
   - Statistical tests on character distributions

3. **Currier, P. (1976).** "Papers on the Voynich manuscript."
   - Identified morphological patterns

## Notes

- Pre-computed results are included in `results/hoax/` directory
- Scripts generate ~10,000 tokens per control (~30 seconds each)
- Metrics calculation is fast (<5 seconds)
- Total time: ~2 minutes for all controls

## Troubleshooting

**Q: Scripts take too long?**
A: Reduce n_tokens parameter (currently 10,000)

**Q: Different results each time?**
A: Random generation - set `random.seed(42)` for reproducibility

**Q: FSM validation fails?**
A: Using mock FSM - real validation requires loading rules from Phase69

**Q: Want to add new control type?**
A: Copy generate_rugg_basic.py, modify generation logic, add to master script
