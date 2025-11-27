# Next Validation Tests: Batch 2

**Date:** November 27, 2025  
**Based on:** Lessons from TEST 1.1 and TEST 2.1  
**Priority:** High-impact tests that build on validated methodology

---

## 🎯 BATCH 2 OVERVIEW

**Goals:**
1. Continue validation of top frequency roots
2. Test alternative hypotheses for 'ol'
3. Validate 'da-i-in' fixed pattern hypothesis
4. Expand evidence for 'e' connector

**Timeline:** Weeks 1-3  
**Expected outcomes:** 4-6 additional validated hypotheses

---

## 📊 TEST 2.2: HUMORAL QUALITY CORRELATION FOR 'ol'

### Status
**Priority:** HIGH  
**Estimated time:** 2 hours  
**Dependencies:** Zodiac data loaded  
**Can run:** Immediately

### Hypothesis

**Since TEST 2.1 rejected temperature, test humoral qualities:**
- H1: 'ol' relates to DRY quality (opposite of moist)
- H2: 'ol' relates to MOIST quality
- H3: 'ol' relates to hot/dry combination
- H4: 'ol' relates to cold/dry combination

### Method

```python
Zodiac humoral assignments:
  Hot-Dry: Aries (f67), Leo (f71), Sagittarius
  Hot-Moist: Gemini (f69), Libra, Aquarius
  Cold-Dry: Taurus (f68), Virgo (f72), Capricorn
  Cold-Moist: Cancer (f70), Scorpio, Pisces

Calculate 'ol' frequency by humoral category:
  - Hot signs (Hot-Dry + Hot-Moist)
  - Cold signs (Cold-Dry + Cold-Moist)
  - Dry signs (Hot-Dry + Cold-Dry)
  - Moist signs (Hot-Moist + Cold-Moist)

Test for enrichment vs baseline (13.96% from TEST 2.1)
```

### Success Criteria

**H1 (DRY quality):**
- Dry signs >18% (30% above baseline) → +20% confidence
- Dry signs >16% (15% above baseline) → +15% confidence
- Moist signs <11% (20% below baseline) → Supporting evidence

**H2 (MOIST quality):**
- Moist signs >18% → +20% confidence
- Dry signs <11% → Supporting evidence

**Falsification:**
- No significant difference (all within ±10% of baseline) → Humoral hypothesis rejected

### Expected Outcome

**From TEST 2.1, Earth enrichment (+16%) suggests:**
- Earth = Cold-Dry traditionally
- Prediction: 'ol' should be enriched in Cold-Dry or Dry generally
- Target confidence: 30-40% for "dry quality" hypothesis

---

## 📊 TEST 2.3: 'ol' CO-OCCURRENCE ANALYSIS

### Status
**Priority:** HIGH  
**Estimated time:** 3 hours  
**Dependencies:** Herbal section data  
**Can run:** Immediately

### Hypothesis

If 'ol' describes a specific plant property, it should:
1. Co-occur with specific other quality roots (forming compound terms)
2. Show non-random association patterns
3. Cluster with semantically related roots

### Method

```python
In herbal section (where 'ol' is enriched 45.3%):
  1. Extract all labels containing 'ol'
  2. Extract co-occurring roots in same label
  3. Calculate co-occurrence frequency
  4. Compare to baseline (random co-occurrence rate)
  
Build co-occurrence network:
  - Which roots appear WITH 'ol' more than expected?
  - Do these form semantic clusters?
  - Does 'ol' combine with specific prefixes/suffixes?

Statistical test:
  - Chi-square for independence
  - PMI (Pointwise Mutual Information) scores
  - Network clustering analysis
```

### Success Criteria

**Pattern discovery:**
- Significant co-occurrence (χ² p<0.01) with 2+ roots → +10% confidence
- Consistent compounds (e.g., ol-X appears 50+ times) → +15% confidence
- Semantic clustering evident → +15% confidence

**Falsification:**
- Random co-occurrence (p>0.1) → 'ol' is independent, not part of compounds
- No clear patterns → Cannot infer meaning from co-occurrence

### Expected Outcome

**Possible findings:**
- 'ol' + specific roots = compound quality terms
- Position patterns (does 'ol' come first or second?)
- Prefix associations revealing semantic field

**Target confidence:** 15-25% for specific semantic field

---

## 📊 TEST 3.1: 'da-i-in' SECTION-FUNCTION CORRELATION

### Status
**Priority:** HIGH  
**Estimated time:** 2 hours  
**Dependencies:** All section data  
**Can run:** Immediately

### Hypothesis

If 'da-i-in' is a preparation/recipe/procedural term:
1. Should be enriched in herbal + recipes (instructional contexts)
2. Should be depleted in zodiac (descriptive/cosmological)
3. Should show position preferences (e.g., end of labels = "prepared X")

### Method

```python
Current data (from semantic triangulation):
  - Herbal: 58.6% of all 'da-i-in'
  - Recipes: 21.9%
  - Biological: 14.8%
  - Zodiac: 4.7%

Tests:
  1. Calculate enrichment: Herbal + Recipes = 80.5% vs expected
  2. Position analysis: Where does 'da-i-in' appear in labels?
  3. Context analysis: What precedes/follows it?
  4. Morpheme substitution: How fixed is the pattern?

Chi-square test for section distribution
Position distribution test (like TEST 1.1)
```

### Success Criteria

**Distribution test:**
- Herbal + Recipes >75% → +15% confidence for "preparation term"
- Zodiac <10% (depleted) → +10% confidence
- Chi-square p<0.01 → +10% confidence

**Position test:**
- Final position >40% → +15% confidence ("prepared X")
- Standalone >30% → +10% confidence ("preparation")

**Fixedness test:**
- Substitution rate <10% → +15% confidence (true formula, not compositional)
- Substitution rate >30% → Pattern is flexible, different interpretation

**Combined:**
- Multiple tests passed → 50-60% confidence for "preparation/process term"

### Expected Outcome

**Strong hypothesis:**
- 'da-i-in' is a technical term for plant/ingredient preparation
- Appears in procedural contexts (herbal/recipes)
- Fixed formula suggests lexicalization

**Target confidence:** 50-60% for "preparation term"

---

## 📊 TEST 1.2: 'e' CO-OCCURRENCE ANALYSIS

### Status
**Priority:** MEDIUM  
**Estimated time:** 3 hours  
**Dependencies:** All sections data  
**Can run:** After TEST 2.3 (uses similar methodology)

### Hypothesis

If 'e' is a connector, it should:
1. Connect similar word types (Quality + e + Quality, Process + e + Process)
2. Show symmetric behavior (X-e-Y = Y-e-X in meaning)
3. Not show strong lexicalization (should be productive, not fixed)

### Method

```python
For all 'e' pattern tokens (chey, shey, otey, etc.):
  1. Extract VPCA field of preceding token
  2. Extract VPCA field of following token
  3. Build transition matrix
  
Analyze:
  - Do connectors link similar fields? (Quality→e→Quality)
  - Or mixed fields? (Quality→e→Process)
  - Random distribution?

Test:
  - Chi-square for independence of transitions
  - Compare to random baseline
  - Directional asymmetry test
```

### Success Criteria

**Homogeneous connections (similar fields):**
- Quality→e→Quality >30% → +15% confidence (connects like with like)
- Process→e→Process >20% → +10% confidence

**Heterogeneous connections (mixed fields):**
- Mixed transitions >50% → Different interpretation (maybe not simple connector?)

**Productivity test:**
- Low lexicalization (<10% in fixed phrases) → +10% confidence (productive connector)
- High lexicalization (>30%) → May be part of compound words

**Target confidence:** 55-65% for "connector between similar word types"

### Expected Outcome

**Strong hypothesis:**
- 'e' connects semantically similar elements
- Behaves like Latin "et" or Romance "e/y"
- Productive, not lexicalized

---

## 📊 TEST 5.2: ZODIAC SYMBOL ASSOCIATION

### Status
**Priority:** MEDIUM  
**Estimated time:** 4 hours (requires manual annotation)  
**Dependencies:** Zodiac diagram images  
**Can run:** Week 2 (requires visual analysis)

### Hypothesis

Test alternative hypotheses for 'ol' and other quality roots by examining visual context:
1. Does 'ol' appear near specific zodiac symbols (stars, water, earth, etc.)?
2. Do quality roots cluster by visual element?
3. Can we infer meaning from diagram association?

### Method

```python
Manual annotation for f67-73:
  1. Identify visual symbols: fire, water, earth, air, stars, human figures, etc.
  2. Extract labels near each symbol type (<5 words distance)
  3. Calculate root distribution by symbol type
  
Statistical test:
  - Chi-square for symbol-root association
  - Enrichment analysis
  - Compare to random baseline
```

### Success Criteria

**For 'ol':**
- Strong association (>50% near one symbol type) → +20% confidence for that meaning
- Moderate association (>35%) → +15% confidence
- Even distribution → Cannot infer from visual context

**For other quality roots:**
- Discover new hypotheses from symbol associations
- Validate or falsify existing hypotheses

### Expected Outcome

**Possible findings:**
- 'ol' associates with earth/ground symbols (supports "dry/earth" hypothesis)
- Other quality roots show clear visual correlations
- Enables new hypothesis generation

**Target confidence:** 20-30% boost for alternative 'ol' hypotheses

---

## 📊 TEST 6.2: PATTERN PREDICTABILITY

### Status
**Priority:** LOW  
**Estimated time:** 3 hours  
**Dependencies:** Complete morphological rules  
**Can run:** Week 3

### Hypothesis

If morphological patterns are systematic (not memorized):
1. Rare combinations should follow compositional rules
2. Can predict valid vs invalid patterns
3. Overgeneration should be minimal

### Method

```python
From common patterns, generate predictions:
  - If ch-ol and ol-y exist → does ch-ol-y exist?
  - If ot-e and e-dy exist → does ot-e-dy exist?

Test:
  1. Generate all theoretically possible combinations
  2. Check which actually occur in manuscript
  3. Calculate precision (predicted exist / total predicted)
  4. Calculate recall (predicted exist / total exist)

Compare compositional vs memorization models:
  - Compositional: High precision, high recall
  - Memorized: Low precision (overgenerates), low recall (misses patterns)
```

### Success Criteria

**Compositional grammar:**
- Precision >70% → Rules predict well (+15% confidence)
- Recall >50% → Rules are complete (+10% confidence)
- Both high → Strong evidence for systematic grammar

**Memorization:**
- Precision <40% → Rules overgenerate (not systematic)
- Many valid patterns unpredicted → Rules incomplete

**Target:** Validate systematic morphology at 80-90% confidence

### Expected Outcome

**Strong hypothesis:**
- Voynichese has productive compositional morphology
- Not just memorized word list
- Systematic rules govern formation

---

## 🎯 EXECUTION PLAN

### Week 1 (Immediate)

**Day 1-2:**
- ✅ TEST 2.2: Humoral correlation
- ✅ TEST 3.1: 'da-i-in' distribution & position

**Day 3-4:**
- ✅ TEST 2.3: 'ol' co-occurrence
- ⏳ Results analysis & documentation

**Day 5:**
- ⏳ Update confidence scores
- ⏳ Prepare Week 2 tests

### Week 2

**Day 1-3:**
- ⏳ TEST 1.2: 'e' co-occurrence
- ⏳ TEST 5.2: Zodiac symbol annotation (start)

**Day 4-5:**
- ⏳ TEST 5.2: Analysis & validation
- ⏳ Results documentation

### Week 3

**Day 1-2:**
- ⏳ TEST 6.2: Pattern predictability
- ⏳ Additional tests as needed

**Day 3-5:**
- ⏳ Comprehensive analysis
- ⏳ Update all documentation
- ⏳ Plan Batch 3 tests

---

## 📈 EXPECTED OUTCOMES

### Confidence Improvements

**By end of Week 1:**
- 'ol' dry/earth: 5% → 30-40%
- 'da-i-in' preparation: 35% → 55-65%
- 'e' connector: 40% → 45-50%

**By end of Week 2:**
- 'e' connector: 45-50% → 60-65%
- Alternative 'ol' hypothesis: 40% → 50-60%

**By end of Week 3:**
- Systematic morphology: 90% → 95%
- 3-4 roots with >50% semantic confidence

### Validation Rate

**Current:** 2/100 roots tested (2%)  
**After Batch 2:** 6-7/100 roots tested (6-7%)  
**Target:** 10/100 roots by end of month (10%)

---

## 🔬 METHODOLOGICAL REFINEMENTS

### Lessons from Batch 1

**What worked:**
1. ✅ Clear quantitative thresholds
2. ✅ Falsifiable predictions
3. ✅ Large sample sizes
4. ✅ Independent measures

**Improvements for Batch 2:**
1. Multiple hypotheses per test (H1, H2, H3, H4)
2. Confidence boosts scaled by strength of result
3. Null result documentation (tests that don't pass/fail clearly)
4. Cross-validation between tests

### Statistical Rigor

**For all tests:**
- Report p-values (chi-square tests)
- Calculate effect sizes (not just significance)
- Use Bonferroni correction for multiple comparisons
- Report confidence intervals, not just point estimates

**Sample size requirements:**
- Minimum 100 tokens per category for chi-square
- Minimum 500 tokens for correlation analyses
- Document when sample size is insufficient

---

## 📝 SUCCESS CRITERIA SUMMARY

### Test Completion

**Batch 2 is successful if:**
- ≥4 tests executed ✅
- ≥2 new hypotheses validated (>40% confidence) ✅
- ≥2 hypotheses rejected or refined ✅
- All tests properly documented ✅

### Scientific Rigor

**Batch 2 demonstrates rigor if:**
- Mix of positive and negative results ✅
- Confidence changes justified by evidence ✅
- Alternative hypotheses considered ✅
- Limitations acknowledged ✅

### Progress Toward Publication

**Batch 2 advances publication if:**
- 3+ roots with >50% semantic confidence
- Systematic methodology demonstrated
- Replicable procedures documented
- Ready for peer review on methods

---

## 🎯 BATCH 3 PREVIEW (Weeks 4-6)

### Planned Tests

**TEST 4.1:** Medieval corpus comparison
- Systematic morpheme frequency matching
- Closest language family identification
- Cognate validation

**TEST 5.1:** Plant part diagram correspondence
- Manual annotation of plant drawings
- Label-part association analysis
- Quality descriptor validation

**TEST 6.1:** Hold-out validation
- Train on Herbal + Zodiac
- Test on Biological + Recipes
- Cross-section predictive accuracy

**Additional tests:** Based on Batch 2 results and emergent hypotheses

---

## 🏆 ULTIMATE GOALS

### Short-term (3 months)

- **10 roots** with >50% semantic confidence
- **3 roots** with >60% semantic confidence
- **1 root** with >70% semantic confidence
- Systematic methodology validated

### Medium-term (6 months)

- **20 roots** with >50% confidence
- **10 roots** with >60% confidence
- Medieval language family identified (65% confidence)
- Ready for academic publication

### Long-term (12 months)

- **50 roots** with >40% confidence
- **30 roots** with >60% confidence
- Translation templates for common patterns (40-60% confidence)
- Probabilistic glossary published

---

## 📊 RESOURCE ALLOCATION

### Time Investment

- **Per test:** 2-4 hours
- **Batch 2 total:** 15-20 hours
- **Documentation:** 5-8 hours
- **Analysis & refinement:** 5 hours

**Total Batch 2:** 25-33 hours over 3 weeks

### Technical Requirements

- Python scripts for each test ✅
- Statistical analysis tools (scipy, numpy) ✅
- Data visualization (matplotlib) ⏳
- Manual annotation tools (for TEST 5.2) ⏳

### Data Requirements

- All section transliterations ✅
- VPCA classifications ✅
- Morphological analysis ✅
- Zodiac diagram images ⏳

---

## ✅ READY TO EXECUTE

**All Batch 2 tests have:**
- Clear hypotheses ✅
- Defined methods ✅
- Success criteria ✅
- Falsification conditions ✅
- Expected outcomes ✅

**Can begin immediately:**
- TEST 2.2 (2 hours)
- TEST 3.1 (2 hours)
- TEST 2.3 (3 hours)

**Want to run these now?** 🚀

---

**Document prepared:** November 27, 2025  
**Status:** Ready for execution  
**Priority:** HIGH - Build on Batch 1 momentum
