# FSM Rules Quick Reference Guide

## Files Provided

### 1. SUPPLEMENT_S6_FSM_RULES.md
- **Purpose:** Human-readable documentation
- **Content:** 
  - Complete explanation of rule format
  - Validation statistics
  - Annotated examples
  - Usage instructions
  - Reproducibility information
- **Audience:** Researchers and reviewers
- **Format:** Markdown document (~12 pages)

### 2. DATA_S1_FSM_RULES_109.tsv
- **Purpose:** Machine-readable rule specification
- **Content:** All 109 rules in tabular format
- **Columns:**
  1. rule_id (unique identifier)
  2. kind (chargram/suffix/prefix/pair)
  3. pattern (token/character sequence)
  4. position (left/right)
  5. base_weight (0-10 scale)
  6. allow_sections (semicolon-separated)
  7. deny_sections (semicolon-separated)
  8. weight_herbal (0.0-1.0)
  9. weight_biological (0.0-1.0)
  10. weight_recipes (0.0-1.0)
  11. weight_pharmaceutical (0.0-1.0)
  12. weight_astronomical (0.0-1.0)
  13. weight_unassigned (0.0-1.0)
- **Audience:** Computational researchers
- **Format:** Tab-separated values

### 3. p69_rules_final.json (original)
- **Purpose:** Complete rule specification with nested structure
- **Content:** Full JSON with all parameters
- **Audience:** Developers implementing FSM
- **Format:** JSON

---

## Rule Statistics Summary

**Total Rules:** 109

**By Category:**
- Chargram: 33 (character n-gram patterns)
- Suffix: 15 (word endings)
- Prefix: 26 (word beginnings)
- Pair: 35 (token co-occurrence)

**By Position:**
- Left-position rules: 56
- Right-position rules: 53

**Validation Performance:**
- Coverage: 79.3% (714/900 validation stems)
- Accuracy: 72.4% (on covered stems)
- Combined: 57.4% (overall success rate)

---

## Example Rules

### High-Weight Left Rule
```
Rule: suffix:he:left
Pattern: ends with "he"
Position: LEFT preference
Weight: 18.0 (highest in dataset)
Active: Biological, Herbal, Recipes
Blocked: Astronomical, Pharmaceutical, Unassigned
Interpretation: Strong left-position marker
```

### High-Weight Right Rule
```
Rule: suffix:y:right
Pattern: ends with "y"
Position: RIGHT preference
Weight: 8.0
Active: All sections
Interpretation: Dominant suffix with consistent right bias
Frequency: 38.4% of corpus (11,400 tokens)
```

### Context-Dependent Rule
```
Rule: chargram:he:left
Pattern: contains "he"
Position: LEFT preference
Weight: 6.0
Section weights: Herbal=0.9, Recipes=0.76, Biological=0.76
Interpretation: Variable strength across contexts
```

---

## How to Use

### For Paper Review
Read **SUPPLEMENT_S6_FSM_RULES.md** for:
- Understanding rule structure
- Validation methodology
- Performance interpretation
- Comparison to natural language

### For Computational Replication
Use **DATA_S1_FSM_RULES_109.tsv** for:
- Loading rules into analysis software
- Implementing FSM scoring algorithm
- Validating against test data
- Comparing to other systems

### For Software Integration
Use **p69_rules_final.json** for:
- Direct JSON parsing
- Full parameter access
- Complex rule matching
- Section-specific weighting

---

## Citation

When referencing these rules:

```
[Authors]. (2025). Complete FSM rule specification for Voynichese 
grammar. Supplement S6 and Data S1. DOI: [to be assigned]
```

When using rules computationally:

```python
import json
import pandas as pd

# Load JSON version
with open('p69_rules_final.json', 'r') as f:
    rules = json.load(f)

# Load TSV version
rules_df = pd.read_csv('DATA_S1_FSM_RULES_109.tsv', sep='\t')

# Access specific rule
rule_1 = rules['rules'][0]
print(f"Rule: {rule_1['rule_id']}")
print(f"Pattern: {rule_1['pattern']}")
print(f"Position: {rule_1['pred_side']}")
```

---

## Checksums (for verification)

**p69_rules_final.json:**
- SHA-256: [to be computed from final file]
- Size: ~15 KB

**DATA_S1_FSM_RULES_109.tsv:**
- SHA-256: [to be computed from final file]
- Size: ~12 KB

**Validation Data:**
- Input segments SHA-256: 9aa399f275133102a7dd554a8ecc3d7310aecaa4f81199b489f2329815f361de

---

## Contact

Questions about rule interpretation, usage, or replication:
- See main manuscript Methods section  
- Consult SUPPLEMENT_S6_FSM_RULES.md documentation
- Access full repository: [URL to be provided]
- Contact corresponding author: [email to be provided]

---

## Version History

**v1.0 (2025):** Initial publication with manuscript
- 109 validated rules
- Coverage: 79.3%
- Accuracy: 72.4%

Future updates (if any) will be versioned and deposited in repository with change documentation.
