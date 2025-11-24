
# Table S2: Complete Suffix Mapping Rules for All Compression Models

## Model 1: Minimal Collapse
**Strategy:** Preserve maximum diversity; gentle 1:1 mapping

| Latin Suffix | Voynich Suffix | Rationale |
|--------------|----------------|-----------|
| us           | ol             | Nominative base form |
| um           | am             | Accusative neuter |
| em           | am             | Accusative masculine |
| is           | ol             | Genitive/dative |
| as           | al             | Accusative plural feminine |
| os           | or             | Accusative plural masculine |
| ae           | y              | Genitive/dative feminine |
| a            | y              | Nominative feminine (most common) |
| e            | ain            | Various (3rd decl, verbal) |
| i            | aiin           | Genitive/locative |
| o            | ody            | Ablative/dative |
| u            | ody            | Rare endings |
| er           | or             | Infinitive |
| ar           | or             | Infinitive |
| ir           | ain            | Infinitive |
| or           | or             | Agent noun |

**Result:** 9 types, entropy 2.968 bits

---

## Model 2: Aggressive Collapse
**Strategy:** Many-to-one; maximize compression

| Latin Suffix | Voynich Suffix | Rationale |
|--------------|----------------|-----------|
| a, ae, as, arum | y           | ALL feminine → y |
| us, um, o, os, orum | y       | ALL masculine/neuter → y |
| e, i | y                       | Short vowels → y |
| are, ere, ire | or            | ALL infinitives → or |
| or, ur, er, ar, ir | or       | Agent/infinitive → or |
| at, et, it, atum, atus | am   | Participles → am |
| is, bus, on | ol              | Plural/dative → ol |
| ment, atge | al               | Abstract → al |
| nt, an, en | ain              | Continuous verbal → ain |
| ntur, ndo, endo | aiin        | Gerunds → aiin |
| etz, u | ody                  | Rare → ody |

**Result:** 8 types, entropy 1.550 bits (over-compressed)

---

## Model 3: Tuned Collapse
**Strategy:** Optimize specifically for y-suffix = 38%

| Latin Suffix | Voynich Suffix | Rationale |
|--------------|----------------|-----------|
| a, ae, am, as | y             | Maximize y (target 38%) |
| us, um, e, i | y              | Add more to y |
| is, o | ol                     | Keep ol moderate |
| or, er, ar | or                | Keep or small |
| em, at | am                    | Keep am small |
| ir, en, an | ain               | Distribute remainder |
| u, etz | ody                   | Distribute remainder |
| bus | al                       | Minimal al |

**Result:** 7 types, entropy 2.086 bits, y = 38.6% (perfect!)
**Problem:** ol exploded to 28.5%, aiin/ody disappeared

---

## Model 4: Hybrid System
**Strategy:** Mix 70% Latin + 30% Occitan before compression

**Phase 1: Mix corpora**
- 9,240 Latin tokens (70%)
- 3,960 Occitan tokens (30%)

**Phase 2: Apply aggressive collapse to mixture**
(Same mappings as Model 2)

**Result:** 9 types, entropy 1.738 bits
**Benefit:** Slightly better distribution than pure Latin
**Problem:** Still rejected (χ² = 1,823, p < 0.001)

---

## Model 5: Context-Dependent
**Strategy:** Different rules for Currier A (formal) vs B (informal)

**Currier A rules (40% of corpus):**
| Latin Suffix | Voynich Suffix |
|--------------|----------------|
| a, us, um | y              |
| are, ere | or              |
| is, bus | ol               |
| nt | ain                  |
| Other | NULL               |

**Currier B rules (60% of corpus - more aggressive):**
| Latin Suffix | Voynich Suffix |
|--------------|----------------|
| a, ae, e, i, o, u, us, um, os | y | (Extreme vowel collapse)
| are, ere, ire, or | or  |
| at, et | am              |
| is, bus | ol             |
| nt, an | ain            |
| Other | NULL            |

**Result:** 6 types, entropy 1.526 bits
**Problem:** Lost too many types, over-collapsed

---

## Model 6: Ultra-Aggressive
**Strategy:** Maximize dominant suffix at all costs

| Latin Suffix | Voynich Suffix | Rationale |
|--------------|----------------|-----------|
| a, ae, am, as, arum, us, um, o, os, orum, e, i, em, es, is | y | EVERYTHING nominal → y |
| are, ere, ire | or            | Only infinitives distinct |
| nt | ain                       | Only one verbal form |
| bus | ol                       | Only one plural form |
| ment | al                      | Only one abstract |
| at | am                        | Only one participle |
| Other | NULL                   | Rest undifferentiated |

**Result:** 6 types, entropy 0.903 bits, y = 78.3%
**Problem:** Catastrophic over-compression, lost all diversity

---

## Summary

| Model | Types | Entropy | y% | Best Feature | Fatal Flaw |
|-------|-------|---------|----|--------------| -----------|
| Minimal | 9 | 2.968 | 13.5% | Preserves diversity | y too low |
| Aggressive | 8 | 1.550 | 67.1% | High compression | y too high, entropy too low |
| Tuned | 7 | 2.086 | 38.6% | Perfect y match! | Lost aiin/ody, ol exploded |
| Hybrid | 9 | 1.738 | 58.2% | Best corpus mix | Still fails distribution |
| Context | 6 | 1.526 | 51.0% | Models register | Lost too many types |
| Ultra | 6 | 0.903 | 78.3% | Maximum compression | Destroyed all structure |

**Key finding:** No model satisfies all constraints simultaneously.
**Interpretation:** Entropy-diversity tradeoff is robust across model space.
