# Phase 2: Confirmatory Validation Study - DESIGN
**Date:** November 27, 2025  
**Status:** PRE-REGISTERED STUDY DESIGN  
**Purpose:** Independent validation of Phase 1 exploratory hypotheses

---

## STUDY OVERVIEW

**Objective:** Test Phase 1 hypotheses on independent held-out data

**Design:** Pre-registered hold-out validation + external corpus validation

**Timeline:** 3-4 weeks

**Success Criteria:** Pre-specified, quantitative, falsifiable

---

## DATA PARTITIONING

### Training Set (Used in Phase 1):
**Already examined - cannot use for validation:**
- Herbal A: f1-f57 (~16,000 tokens)
- Zodiac: f67-f73 (~3,300 tokens)
- Recipes A: f99-f107 (~3,700 tokens)
- **Total: ~23,000 tokens (78%)**

### Test Set (Reserved for Phase 2):
**Locked - not examined until predictions registered:**
- **Biological: f75-f86** (~6,000 tokens) ⭐ PRIMARY
- **Herbal B: f58-f66** (~2,500 tokens)
- **Recipes B: f108-f116** (~2,000 tokens)
- **Total: ~10,500 tokens (36%)** ✅

**Test set is sufficient for independent validation**

---

## PRE-REGISTERED HYPOTHESES

### Hypothesis 1: 'da-i-in' = Preparation/Process Term

**Phase 1 Observation:**
- 80.5% in procedural contexts (herbal + recipes)
- 1.78x enrichment in herbal
- 4.7% in zodiac

**Phase 2 Prediction (LOCKED):**
1. Biological section: 'da-i-in' will be 60-80% in procedural contexts
2. Herbal B: 'da-i-in' enrichment >1.5x vs baseline
3. Position: 'da-i-in' will be >35% label-final (nominalization pattern)

**Success Criteria:**
- ≥2 of 3 predictions met → Hypothesis SUPPORTED (+30% confidence)
- 3 of 3 predictions met → Hypothesis STRONGLY SUPPORTED (+40% confidence)
- <2 predictions met → Hypothesis REJECTED (confidence →10%)

**Current confidence:** 15-20%  
**Post-validation range:** 10% (rejected) to 55-60% (strongly supported)

---

### Hypothesis 2: 'e' = Connector Element

**Phase 1 Observation:**
- 91.8% medial position
- 40 compound patterns
- Strong co-occurrence clustering

**Phase 2 Predictions (LOCKED):**

**Test 2a: Hold-Out Position**
- Biological section: 'e' will be >85% medial position

**Test 2b: External Medieval Corpus**
- Latin "et/cum/de" will show >80% medial position in similar texts
- 'e' frequency (~30%) comparable to Latin connector frequency (25-35%)

**Test 2c: Hold-Out Co-occurrence**
- Biological: 'e' will show ≥20 enriched co-occurring tokens

**Success Criteria:**
- 2 of 3 tests pass → SUPPORTED (+25% confidence)
- 3 of 3 tests pass → STRONGLY SUPPORTED (+35% confidence)
- <2 tests pass → INCONCLUSIVE (+10% confidence)

**Current confidence:** 20-25%  
**Post-validation range:** 30-35% (weak) to 55-60% (strong)

---

### Hypothesis 3: 'ol' = Earth/Terrestrial Property

**Phase 1 Observation:**
- Modest zodiac element correlation (p<0.001)
- Post-hoc hypothesis adjustment
- Fails strict Bonferroni

**Phase 2 Decision:** **DEPRIORITIZE**

**Rationale:**
- Likely overfit in Phase 1
- Need truly independent test (diagram correspondence)
- Insufficient confidence to warrant hold-out validation yet

**Alternative:** If time permits, test on diagram-label correspondence (fully independent data)

**Current confidence:** 10%  
**Will not test in Phase 2 unless independent method available**

---

## TEST PROTOCOLS

### Protocol 1: Hold-Out Distributional Testing

**For: Hypothesis 1 ('da-i-in')**

```
INPUT: Biological section (f75-f86)
METHOD:
1. Calculate 'da-i-in' frequency by context type
2. Determine procedural percentage
3. Calculate enrichment ratios
4. Compare to Phase 1 predictions

OUTPUT: Pass/Fail for each criterion
STATISTICAL TEST: Chi-square, p<0.05 threshold
```

---

### Protocol 2: Position Analysis

**For: Hypothesis 1 ('da-i-in') and Hypothesis 2 ('e')**

```
INPUT: Biological section
METHOD:
1. Identify all occurrences of pattern
2. Classify position: Initial, Medial, Final
3. Calculate position percentages
4. Compare to Phase 1 predictions

OUTPUT: Position distribution
STATISTICAL TEST: Chi-square vs expected
```

---

### Protocol 3: External Medieval Corpus

**For: Hypothesis 2 ('e')**

```
INPUT: 
- Latin medical texts (13th-15th century)
- ~50,000 tokens minimum
- Similar domain (herbal/medical)

METHOD:
1. Identify Latin connectors: "et", "cum", "de", "atque"
2. Calculate position distribution
3. Calculate frequency as % of text
4. Compare to Voynichese 'e' patterns

OUTPUT: Comparative statistics
VALIDATION: Independent data (not from Voynich)
```

**Sources:**
- Circa Instans (Platearius, 12th c.)
- Liber de Simplici Medicina (Matthaeus Platearius)
- Tractatus de Herbis (multiple 13th-15th c. manuscripts)

---

### Protocol 4: Co-occurrence Analysis (Hold-Out)

**For: Hypothesis 2 ('e')**

```
INPUT: Biological section
METHOD:
1. Extract all labels containing 'e'
2. Calculate token enrichment
3. Count enriched tokens (>1.5x)
4. Compare to Phase 1 (40 compounds)

OUTPUT: Enrichment list
CRITERION: ≥20 enriched tokens
```

---

## PRE-REGISTRATION TIMESTAMP

**Predictions locked:** November 27, 2025  
**GitHub commit:** [To be added]  
**SHA hash:** [To be added]

**All predictions above are LOCKED before examining test set**

**No changes permitted after examining hold-out data**

---

## STATISTICAL FRAMEWORK

### Significance Testing:
- All tests: p<0.05 threshold
- Chi-square for distributional analyses
- Bonferroni correction: p<0.025 (2 primary hypotheses)

### Confidence Updates:
- Based on pre-specified criteria only
- No post-hoc adjustments
- Conservative estimates default

### Null Results:
- Will be reported fully
- No selective reporting
- Failed predictions reduce confidence

---

## EXECUTION TIMELINE

### Week 1: External Validation
**Days 1-3:** Medieval corpus analysis
- Compile Latin texts
- Analyze connector patterns
- Compare to Voynichese 'e'

**Days 4-5:** Analysis and write-up
- Statistical comparisons
- Preliminary conclusions

### Week 2: Hold-Out Preparation
**Days 1-2:** Final prediction review
- Verify predictions clear
- Check pre-registration complete
- Lock GitHub commit

**Days 3-5:** Hold-out analysis
- Test Hypothesis 1 ('da-i-in')
- Test Hypothesis 2 ('e') position/co-occurrence
- Statistical testing

### Week 3: Analysis and Write-Up
**Days 1-3:** Results analysis
- Compare predictions to observations
- Calculate confidence updates
- Statistical significance

**Days 4-5:** Documentation
- Full results report
- Updated confidence table
- Publication preparation

### Week 4: Buffer
- Additional analysis if needed
- Manuscript preparation
- Response to unexpected findings

---

## SUCCESS DEFINITIONS

### Best Case:
- Both hypotheses strongly supported
- 'da-i-in' → 55-60% confidence (publication threshold approached)
- 'e' → 55-60% confidence
- 2 roots with validated patterns

### Expected Case:
- One hypothesis supported, one inconclusive
- 'da-i-in' → 45-50% OR 'e' → 45-55%
- Clear direction for next steps
- 1 root approaching validation

### Worst Case:
- Both hypotheses fail
- All confidence → 10-15%
- But: Valuable null result
- Learned patterns are spurious
- Can publish "why it failed" (important!)

### All outcomes are valuable scientific results

---

## QUALITY CONTROL BUILT IN

### Pre-Test QC:
✅ Predictions pre-registered  
✅ Test set locked  
✅ Success criteria quantitative  
✅ Statistical framework defined  
✅ Will report all results

### During-Test QC:
✅ No peeking at test set before predictions locked  
✅ No post-hoc hypothesis adjustments  
✅ Follow protocols exactly  
✅ Document any deviations

### Post-Test QC:
✅ Report null results fully  
✅ Conservative confidence updates  
✅ Honest assessment  
✅ Limitations acknowledged

---

## DEVIATIONS PROTOCOL

**If predictions need revision:**
1. Document reason for revision
2. Timestamp revision
3. Mark as "post-hoc" in analysis
4. Reduce confidence for revised predictions
5. Report transparently in publication

**Goal:** No revisions - follow original predictions

---

## PUBLICATIONS FROM PHASE 2

### If Successful:

**Paper 1: Validated Findings**
> "Hold-Out Validation of Distributional Patterns in Voynichese"
- Reports validation results
- Confidence levels post-validation
- First validated semantic claims

**Paper 2: External Comparison**
> "Comparative Analysis of Voynichese and Medieval Latin Connector Elements"
- Medieval corpus results
- Cross-linguistic patterns
- Independent validation

### If Null Results:

**Paper: Null Findings**
> "Why Exploratory Patterns Failed Validation: A Case Study in Undeciphered Script Analysis"
- Reports failed predictions honestly
- Discusses spurious pattern detection
- Methodological lessons
- **Equally valuable scientifically**

---

## COMMITMENT TO TRANSPARENCY

**We commit to:**
1. ✅ Publishing all results (positive and negative)
2. ✅ Following pre-registered protocol
3. ✅ Reporting confidence honestly
4. ✅ No selective reporting
5. ✅ Acknowledging limitations
6. ✅ Making data and code available

**This is proper confirmatory research**

---

## EXPECTED OUTCOMES

### Realistic Expectations:

**'da-i-in' validation:**
- 60% chance of support
- 20% chance of strong support
- 20% chance of failure
- If supported: 45-60% confidence (approaching publication)

**'e' validation:**
- 70% chance of support (external validation helps)
- 30% chance of inconclusive
- 10% chance of failure
- If supported: 50-60% confidence

**Overall:**
- 50% chance at least one strong validation
- 30% chance both supported
- 20% chance mixed/null results

**All outcomes advance knowledge**

---

## COMPARISON TO PHASE 1

| Aspect | Phase 1 | Phase 2 |
|--------|---------|---------|
| Data | Training | Independent test |
| Analysis Type | Exploratory | Confirmatory |
| Hypotheses | Generated | Tested |
| Predictions | Post-hoc | Pre-registered |
| Confidence | 15-25% | 10-60% (based on results) |
| Publication | Structural only | Semantic possible |

---

## BOTTOM LINE

**Phase 2 Design: RIGOROUS CONFIRMATORY STUDY**

**Features:**
✅ Pre-registered predictions  
✅ Independent test set  
✅ External validation  
✅ Quantitative criteria  
✅ Will report all results  
✅ Built-in QC

**Timeline:** 3-4 weeks  
**Cost:** ~40-60 hours total  
**Value:** First properly validated Voynich semantic claims (if successful)

**This is the proper way to validate exploratory findings**

---

**Design Status:** COMPLETE ✅  
**Pre-registration:** Ready for timestamp ✅  
**Test Set:** Locked ✅  
**Predictions:** Specified ✅  
**Ready to Execute:** YES ✅
