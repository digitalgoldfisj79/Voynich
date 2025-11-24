# Phase 2: Statistical Validation

**Goal:** Add statistical rigor to Phase 1/1B findings to make them publication-ready.

**Status:** IN PROGRESS (2025-01-21)

---

## Phase 2 Scripts

### V01: Bootstrap Confidence Intervals
- Generate confidence intervals for suffix/stem frequencies
- Bootstrap resampling (1000 iterations)
- 95% confidence intervals for all key statistics

### V02: Section Enrichment Significance Tests
- Permutation tests for section-specific enrichment
- Correct for multiple comparisons (Bonferroni)
- Identify truly significant patterns vs. noise

### V03: Morphological Pattern Validation
- Test stem-suffix combination rules against random baseline
- Validate morphological classes statistically
- Chi-square tests for association

### V04: Stability Metric Validation
- Validate stability scores against shuffled data
- Test if stable stems are truly non-random
- Cross-validation of classification

### V05: Publication Summary Statistics
- Generate all statistics needed for publication
- Effect sizes (Cohen's d, Cramér's V)
- Publication-ready tables and figures

---

## Outputs

All outputs will include:
- Point estimates
- Confidence intervals
- P-values (with corrections)
- Effect sizes
- Publication-ready formatting

---

## Timeline

Estimated completion: 1-2 hours of runtime
