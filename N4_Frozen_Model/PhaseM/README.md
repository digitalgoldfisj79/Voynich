# Phase M: Morphological Expansion

**Goal:** Complete morphological analysis of Voynichese without requiring semantic interpretation.

**Status:** PHASE 1 COMPLETE (2025-01-21)

---

## Progress Tracking

**Phase 1: Complete Suffix Analysis** ✅ COMPLETE
- [x] `m01_extract_all_suffixes.py` - Extract complete suffix inventory
- [x] `m02_suffix_by_section.py` - Frequency distributions by section
- [x] `m03_suffix_cooccurrence.py` - Which suffixes appear together
- [x] `m04_suffix_positions.py` - Positional constraints
- [x] `m05_suffix_productivity.py` - Type-token ratios, productive vs frozen

**Phase 2-5:** Not started

**Total Progress:** 5/25 scripts (20%)

---

## Key Findings - Phase 1

### Suffix Inventory
- **Only 9 unique suffixes** identified (extremely limited morphology)
- Top 3 cover 72% of corpus: `y` (38.7%), NULL (26.6%), `aiin` (8.5%)
- Type-token ratio: 0.0003 (very low diversity)

### Section-Specific Patterns
**Pharmaceutical section:**
- `ol` enriched 2.55× (20.3% vs 7.9% corpus-wide)
- `ody` enriched 2.63× 

**Astronomical section:**
- NULL (stem-only words) enriched 1.53× (38.7% vs 26.6%)
- `ody` enriched 2.50×

**Biological section:**
- `y` dominates at 53.9%

### Co-occurrence Patterns
- **No strong clustering or avoidance** detected
- Suffixes appear together at expected rates
- Suggests independent suffix usage

### Positional Patterns
- **All suffixes heavily medial** (~98-99%)
- No strong initial or final preferences
- Suggests suffixes are not positionally constrained

### Productivity Metrics
**Moderately productive:**
- `am`: 190 stems, TTR=0.34
- NULL: 1,872 stems, TTR=0.24
- `ody`: 193 stems, TTR=0.23

**Low productivity:**
- `aiin`: 316 stems, TTR=0.12 (most frozen)
- `ol`: 302 stems, TTR=0.13
- `y`: 2,011 stems, TTR=0.17

**Top stems per suffix:**
- NULL: `ol`, `aiin`, `ar` (standalone words)
- `aiin`, `ain`, `al`: frequently attach to `d`, `qok`, `ok`, `ot`
- `ol`, `or`: frequently attach to `ch`, `che`, `sh`
- `y`: frequently attaches to `ched`, `shed`, `che`

---

## Interpretation (Compressed Orthography Context)

Given the statistical evidence for compressed orthography from Padua:

1. **Limited suffix set (9)** suggests systematic abbreviation system
2. **Section-specific patterns** indicate different text types or scribal practices
3. **High medial positioning** consistent with running text compression
4. **Productivity variation** may reflect different abbreviation strategies

**Important:** These patterns document the compression system, not necessarily underlying linguistic structure.

---

## Publications & Outputs

### Completed Outputs (Phase 1)
- `m01_suffix_inventory.tsv` - Complete suffix inventory
- `m02_suffix_by_section.tsv` - Section-specific distributions
- `m02_suffix_section_matrix.tsv` - Pivot table view
- `m03_suffix_cooccurrence_matrix.tsv` - Co-occurrence patterns
- `m03_cooccurrence_ratio_matrix.tsv` - Matrix format
- `m04_suffix_positions.tsv` - Positional analysis
- `m05_suffix_productivity.tsv` - Productivity metrics

### Planned Publications
1. "Morphological Analysis of Voynichese Compressed Orthography" (main paper)
2. "Suffix Distribution Patterns in the Voynich Manuscript" (detailed study)

---

## Next Steps

**Options for continuation:**

**A) Proceed to Phase 2** (Word Formation Patterns)
- Analyze compound structures
- Morphological templates
- Complexity metrics

**B) Deeper Phase 1 Analysis**
- Statistical validation of section differences
- Comparison to known abbreviation systems
- Diachronic analysis (early vs late folios)

**C) Different Direction**
- Focus on stems instead of suffixes
- Analyze register differences (A vs B)
- Hand-specific morphology

---

## Change Log

- 2025-01-21: Phase M initiated, directory structure created
- 2025-01-21: Phase 1 complete (m01-m05 scripts executed)
- 2025-01-21: README updated with Phase 1 findings
