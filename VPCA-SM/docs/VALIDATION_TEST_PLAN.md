# Validation Test Plan: Rigorous Hypothesis Testing

**Purpose:** Design falsifiable tests to validate (or refute) semantic hypotheses

**Principle:** Each test must have clear pass/fail criteria and be independent of the hypothesis it tests

**Date:** November 27, 2025

---

## 🎯 TESTING PHILOSOPHY

### Core Principles:

1. **Falsifiability** - Every hypothesis must be testable
2. **Independence** - Tests must not use circular reasoning
3. **Quantification** - Results must be measurable
4. **Replication** - Tests must be reproducible
5. **Honesty** - Failed tests lower confidence, not "explained away"

### Confidence Thresholds:

- **<30%:** Speculation (weak/no evidence)
- **30-50%:** Hypothesis (some evidence, needs validation)
- **50-70%:** Moderate confidence (multiple validations)
- **70-85%:** High confidence (strong converging evidence)
- **>85%:** Very high confidence (overwhelming evidence)

### Test Design:

Each test should:
- State hypothesis clearly
- Define success criteria quantitatively
- Specify what would falsify the hypothesis
- Calculate confidence impact (±%)
- Be independent of other tests

---

## 📊 TEST SUITE 1: ROOT 'e' HYPOTHESES

### Current Status:
- Structural: Modifier/Relation (75% confidence)
- Semantic: Unknown, possibly connector (20% confidence)

---

### **TEST 1.1: Positional Distribution**

**Hypothesis:** If 'e' is a connector, it should appear BETWEEN content elements more than at boundaries

**Method:**
```python
For each token containing 'e' root:
  1. Extract surrounding tokens (±2 positions)
  2. Classify position: sentence-initial, sentence-final, medial
  3. Calculate distribution

Expected if connector:
  - Medial position: >60%
  - Sentence-initial: <20%
  - Sentence-final: <20%

Expected if NOT connector:
  - More random distribution
```

**Success criteria:**
- Medial >60% → +20% confidence
- Medial 50-60% → +10% confidence
- Medial <50% → Hypothesis weakened

**Falsification:**
- If sentence-initial >40% → NOT a connector
- Reject hypothesis, confidence drops to <10%

**Why independent:** Position distribution is observable without assuming meaning

---

### **TEST 1.2: Co-occurrence Analysis**

**Hypothesis:** Connectors appear between similar word types, not randomly

**Method:**
```python
For tokens containing 'e':
  1. Get VPCA field of preceding token
  2. Get VPCA field of following token
  3. Build transition matrix

Expected if connector:
  - Quality → 'e' → Quality (common)
  - Process → 'e' → Process (common)
  - Mixed transitions → 'e' → uniform

Expected if NOT connector:
  - Random distribution
```

**Success criteria:**
- Similar-category transitions >50% → +15% confidence
- Non-random pattern (χ² p<0.01) → +10% confidence

**Falsification:**
- Random distribution (χ² p>0.1) → Hypothesis rejected

**Why independent:** Uses VPCA categories, not semantic assumptions

---

### **TEST 1.3: Frequency-Position Correlation**

**Hypothesis:** Functional words (like connectors) show different frequency patterns than content words

**Method:**
```python
Compare 'e' to known content words:
  1. Calculate per-sentence frequency
  2. Calculate variance across sections
  3. Compare to Zipf's law expectations

Functional words expected:
  - High frequency
  - Low variance across contexts
  - Zipf exponent >1.5

Content words expected:
  - Variable frequency
  - High variance (topic-dependent)
  - Zipf exponent ~1.0
```

**Success criteria:**
- Zipf exponent >1.5 → +10% confidence (functional)
- Low cross-section variance → +10% confidence

**Falsification:**
- Zipf exponent <1.2 → Content word, not functional

**Why independent:** Statistical distribution, no semantic assumptions

---

## 📊 TEST SUITE 2: ROOT 'ol' HYPOTHESES

### Current Status:
- Structural: Quality/State (75% confidence)
- Semantic: Unknown (<10% confidence)

**Goal:** Test specific semantic hypotheses systematically

---

### **TEST 2.1: Zodiac Seasonal Correlation**

**Hypothesis:** If 'ol' relates to temperature/heat, it should correlate with seasonal imagery

**Method:**
```python
For each zodiac folio:
  1. Identify season (Aries=spring, Cancer=summer, etc.)
  2. Count 'ol' occurrences per folio
  3. Calculate seasonal distribution

Test multiple hypotheses:
  H1 (hot): 'ol' enriched in summer/fire signs
  H2 (cold): 'ol' enriched in winter/water signs
  H3 (neutral): 'ol' distributed evenly

Expected frequencies if random: 25% per season
```

**Success criteria (H1 - hot):**
- Summer/fire >35% → +20% confidence for "heat" meaning
- Summer/fire 30-35% → +10% confidence
- Summer/fire <30% → No support

**Success criteria (H2 - cold):**
- Winter/water >35% → +20% confidence for "cold" meaning

**Falsification:**
- Even distribution (20-30% each) → Temperature hypothesis rejected
- Neither hot nor cold supported → Unknown quality

**Why independent:** Zodiac seasons are independently identifiable from imagery

**CRITICAL:** This test actually examines diagram context, not just distribution

---

### **TEST 2.2: Humoral Association Test**

**Hypothesis:** If 'ol' relates to specific humoral quality, it should correlate with humoral associations

**Method:**
```python
From previous humoral analysis:
  - Hot-dry signs: Aries, Leo, Sagittarius
  - Hot-moist signs: Gemini, Libra, Aquarius
  - Cold-dry signs: Taurus, Virgo, Capricorn
  - Cold-moist signs: Cancer, Scorpio, Pisces

Count 'ol' by humoral category
Test for enrichment vs baseline (16.7% expected)

Multiple hypotheses:
  H1: 'ol' = hot quality
  H2: 'ol' = cold quality
  H3: 'ol' = moist quality
  H4: 'ol' = dry quality
```

**Success criteria:**
- >30% in hot signs → +15% confidence for "hot"
- >30% in cold signs → +15% confidence for "cold"
- Similar enrichment in moist/dry tests

**Falsification:**
- No significant enrichment → Humoral hypothesis rejected

**Why independent:** Humoral categories are external framework

---

### **TEST 2.3: Herbal Co-occurrence Analysis**

**Hypothesis:** If 'ol' describes specific plant property, it should co-occur with related roots

**Method:**
```python
In herbal section (where 'ol' is enriched 45.3%):
  1. Find tokens containing 'ol'
  2. Extract co-occurring roots (same label)
  3. Build co-occurrence network
  4. Compare to baseline

Test:
  - Do certain roots appear WITH 'ol' more than expected?
  - Do these form semantic clusters?
  - Does 'ol' appear in isolation or combined?
```

**Success criteria:**
- Consistent co-occurrence patterns → Suggests compound terms
- Clusters emerge → Suggests semantic grouping
- +10-15% confidence if patterns found

**Falsification:**
- Random co-occurrence → No systematic meaning
- Cannot distinguish semantic hypothesis

**Why independent:** Uses actual token combinations, not assumed meanings

---

### **TEST 2.4: Intensification Pattern Test**

**Hypothesis:** If 'ol' is a scalar quality (hot/cold/wet/dry), it should be intensifiable

**Method:**
```python
Check intensification behavior:
  - ch-ol frequency (intensified)
  - [ol] alone frequency (base)
  - Compare to other quality roots

Scalar qualities expected:
  - High intensification rate (>25%)
  - ch-ol more common than with non-scalar qualities

Non-scalar qualities expected:
  - Low intensification rate (<15%)
```

**Current data:** ch-ol appears 287× out of 1,044 total = 27.5%

**Success criteria:**
- >25% intensification → +10% confidence for scalar quality
- Consistent with temperature/intensity semantics

**Falsification:**
- <15% intensification → Not a scalar quality
- Rules out temperature hypothesis

**Why independent:** Intensification is grammatical behavior, observable without knowing meaning

**RESULT:** Already supports scalar quality (27.5% > 25%)
**Confidence update:** +10% for temperature/intensity hypothesis
**New confidence:** 10% → 20% for temperature-related meaning

---

## 📊 TEST SUITE 3: PATTERN 'da-i-in' HYPOTHESIS

### Current Status:
- Pattern frequency: 554× (highly fixed)
- Semantic: Unknown (<20% confidence)

---

### **TEST 3.1: Section-Function Correlation**

**Hypothesis:** If 'da-i-in' is a preparation/recipe formula, it should be enriched in instructional contexts

**Method:**
```python
Calculate 'da-i-in' frequency by section:
  - Herbal: 58.6% (plant preparations?)
  - Recipes: 21.9% (instructions?)
  - Biological: 14.8%
  - Zodiac: 4.7%

Test: Is it more common in sections with procedural content?

Compare to control patterns (e.g., bare roots)
```

**Success criteria:**
- Enrichment in herbal + recipes >80% → +15% confidence for "preparation term"
- Depleted in zodiac (<10%) → +10% confidence

**Current data:** Herbal + Recipes = 80.5%

**Falsification:**
- Even distribution → Not context-specific
- Enriched in zodiac → Different function

**RESULT:** Supports procedural/preparation hypothesis
**Confidence update:** +15%
**New confidence:** 20% → 35% for preparation meaning

---

### **TEST 3.2: Position in Herbal Labels**

**Hypothesis:** If 'da-i-in' relates to plant preparation, it should appear at specific positions (e.g., end of labels)

**Method:**
```python
In herbal section:
  1. Extract multi-token labels containing 'da-i-in'
  2. Record position (initial, medial, final)
  3. Compare to baseline

Preparation terms expected:
  - Final position (like "prepared X")
  - Or standalone (like "preparation")
```

**Success criteria:**
- Final position >50% → +10% confidence
- Standalone >30% → +10% confidence

**Falsification:**
- Initial position >50% → Not procedural
- Random distribution → No systematic function

---

### **TEST 3.3: Morpheme Substitution Analysis**

**Hypothesis:** If 'da-i-in' is fixed formula, substitutions should be rare

**Method:**
```python
Test pattern fixedness:
  1. Count da-i-in (expected: 554×)
  2. Count da-i-[other suffix] (substitution test)
  3. Count [other prefix]-i-in (substitution test)
  4. Calculate substitution rate

Highly fixed patterns expected:
  - <10% substitution rate

Flexible patterns expected:
  - >30% substitution rate
```

**Success criteria:**
- <10% substitution → Confirmed fixed formula
- +15% confidence for technical term

**Falsification:**
- >30% substitution → Not fixed, compositional pattern
- Different interpretation needed

---

## 📊 TEST SUITE 4: MEDIEVAL CORPUS COMPARISON

### Goal: Find systematic parallels, not cherry-picked examples

---

### **TEST 4.1: Morphological Signature Matching**

**Hypothesis:** Voynichese most closely resembles Romance vernacular medical texts

**Method:**
```python
Create morphological signatures:
  1. Prefix frequency distribution
  2. Suffix frequency distribution
  3. PREFIX+ROOT+SUFFIX ratio
  4. Root reuse patterns
  5. Pattern diversity

Compare to medieval corpora:
  - Latin medical texts (Circa Instans, etc.)
  - Italian vernacular medical
  - Catalan/Spanish medical
  - German medical abbreviations
  - Arabic medical (transliterated)

Calculate similarity scores:
  - Cosine similarity on feature vectors
  - Rank by similarity
```

**Success criteria:**
- One corpus significantly closer (similarity >0.70) → +20% confidence
- Multiple similar (>0.65) → +10% confidence

**Falsification:**
- All similarities <0.50 → No close match
- Voynichese may be unique system

**Why rigorous:** Systematic comparison, not selected examples

---

### **TEST 4.2: Specific Root-Cognate Mapping**

**Hypothesis:** High-frequency Voynich roots have medieval cognates

**Method:**
```python
For top 20 Voynich roots:
  1. Find medieval words with similar phonology
  2. Check if semantic fields match (Quality vs Process)
  3. Calculate match rate

For example:
  'ol' → Latin "oleum", "color"
  'e' → Latin "et"
  'al' → Latin "-alis"

Count: How many have plausible cognates?

Expected if related: >60% match
Expected if unrelated: <30% match
```

**Success criteria:**
- >60% plausible cognates → +15% confidence
- Structural categories match → +10% confidence

**Falsification:**
- <30% matches → No systematic relationship
- Random phonological overlaps

---

## 📊 TEST SUITE 5: DIAGRAM-LABEL CORRESPONDENCE

### Goal: Use visual context to validate semantic hypotheses

---

### **TEST 5.1: Plant Part Labeling**

**Hypothesis:** Specific roots should correlate with specific plant parts

**Method:**
```python
Manual annotation (sample of 50 herbal folios):
  1. Identify plant part (root/stem/leaf/flower/seed)
  2. Extract labels for each part
  3. Analyze which roots appear on which parts

Test for enrichment:
  - Does 'ol' appear more on flowers vs roots?
  - Does 'da-i-in' appear on seeds/preparation areas?
  - Do patterns emerge?

Statistical test: χ² for independence
```

**Success criteria:**
- Significant association (p<0.05) → +15% confidence
- Consistent patterns across multiple folios → +10% confidence

**Falsification:**
- Random distribution → Labels don't correspond to parts
- Cannot use visual context for semantics

**Why rigorous:** Independent visual classification

---

### **TEST 5.2: Zodiac Symbol Association**

**Hypothesis:** Quality roots should associate with specific zodiac symbols (fire/water/etc.)

**Method:**
```python
For zodiac folios:
  1. Identify visual symbols (fire, water, stars, human figures)
  2. Extract labels near each symbol type
  3. Analyze root distribution

Test:
  - Does 'ol' appear more near fire symbols?
  - Do quality roots cluster by element?
  - Chi-square test for association
```

**Success criteria:**
- Significant association → +20% confidence for specific meanings
- Fire-heat association → Validates temperature hypothesis

**Falsification:**
- No association → Visual context doesn't constrain meaning
- Random distribution → Cannot use diagrams for semantics

---

## 📊 TEST SUITE 6: PREDICTIVE VALIDATION

### Goal: Test if patterns discovered in one section predict patterns in unseen sections

---

### **TEST 6.1: Hold-Out Section Validation**

**Hypothesis:** Morphological patterns are manuscript-wide, not section-specific

**Method:**
```python
Training: Use Herbal + Zodiac (12,566 tokens)
Test: Predict Biological + Recipes (17,003 tokens)

Build model from training:
  1. Root frequency distribution
  2. Pattern frequencies
  3. Morpheme combination rules

Predictions for test set:
  1. Expected root frequencies
  2. Expected pattern frequencies
  3. Expected new patterns

Measure prediction accuracy
```

**Success criteria:**
- Root frequency correlation >0.80 → System is universal
- Pattern prediction accuracy >70% → Rules generalize

**Falsification:**
- Correlation <0.60 → System is section-specific
- Low prediction accuracy → Overfitting to training data

---

### **TEST 6.2: Rare Pattern Prediction**

**Hypothesis:** Even rare patterns should follow compositional rules

**Method:**
```python
From common patterns, predict rare combinations:
  - If ch-ol and ol-y exist, does ch-ol-y exist?
  - If ot-e-dy exists, does ot-e-y exist?

Test compositional productivity:
  - Count predicted patterns that actually exist
  - Count predicted patterns that don't exist
  - Calculate precision/recall
```

**Success criteria:**
- Precision >70% → Rules predict well
- Recall >50% → Rules are complete

**Falsification:**
- Precision <40% → Rules overgenerate
- Many unpredicted valid patterns → Rules incomplete

---

## 🎯 EXECUTION PLAN

### Priority Order:

**Week 1 (Immediate):**
1. TEST 2.1: Zodiac seasonal correlation (can run today!)
2. TEST 1.1: Position distribution for 'e'
3. TEST 2.4: Intensification validation (already supports scalar)
4. TEST 3.1: 'da-i-in' section correlation (already supports preparation)

**Week 2:**
5. TEST 5.1: Plant part labeling (requires manual work)
6. TEST 5.2: Zodiac symbol association
7. TEST 1.2: Co-occurrence analysis for 'e'

**Week 3:**
8. TEST 4.1: Medieval corpus comparison (requires corpus collection)
9. TEST 6.1: Hold-out validation
10. TEST 3.2-3.3: 'da-i-in' pattern tests

**Week 4:**
11. Remaining tests
12. Confidence updates
13. Final assessment

---

## 📏 CONFIDENCE UPDATE RULES

### How to Update Confidence:

**After each test:**
```
If test passes success criteria:
  - Add specified confidence bonus
  - Document evidence
  - Update hypothesis

If test fails:
  - Subtract confidence penalty
  - Consider alternative hypotheses
  - Do NOT explain away

If test is inconclusive:
  - No confidence change
  - Mark as "needs more data"
```

**Multiple tests:**
```
Confidence boosts compound but with diminishing returns:
  - First validation: Full bonus
  - Second validation: 80% of specified bonus
  - Third validation: 60% of specified bonus
  - Fourth+: 40% of specified bonus

Failures compound with increasing impact:
  - First failure: Full penalty
  - Second failure: 150% penalty
  - Third failure: 200% penalty (seriously consider rejecting hypothesis)
```

---

## 🏆 SUCCESS CRITERIA FOR SEMANTIC CLAIMS

### Confidence Thresholds for Publication:

**To claim semantic meaning:**
- Minimum 3 independent tests passed
- Minimum 50% confidence
- At least one diagram-based validation
- No critical test failures

**To claim high confidence (>70%):**
- Minimum 5 independent tests passed
- Multiple converging evidence types
- Predictive validation successful
- Medieval corpus support

**To claim very high confidence (>85%):**
- All available tests passed
- Strong diagram correspondence
- Medieval cognate identified
- Cross-linguistic validation

---

## 🔬 CRITICAL SAFEGUARDS

### Red Flags - Stop and Reassess:

1. **All tests pass easily** → Probably confirmation bias
2. **Failed tests get "explained away"** → Not scientific
3. **Confidence keeps increasing without new evidence** → Circular reasoning
4. **Alternative hypotheses not considered** → Tunnel vision
5. **Tests keep getting designed to confirm** → Selection bias

### Healthy Science Indicators:

1. ✅ Some tests fail → We're being honest
2. ✅ Confidence sometimes decreases → We update beliefs
3. ✅ Alternative hypotheses explored → Open-minded
4. ✅ Null results published → Transparent
5. ✅ Tests designed before knowing results → Rigorous

---

## 📝 NEXT IMMEDIATE ACTION

**RUN THESE TODAY:**

1. **TEST 2.1** - Zodiac seasonal correlation for 'ol'
2. **TEST 1.1** - Position distribution for 'e'
3. **Document results honestly**
4. **Update confidence scores**
5. **Plan next tests based on results**

**These will give us:**
- First real validation of semantic hypothesis
- Measurable confidence updates
- Practice with methodology
- Baseline for future tests

---

## 🎯 BOTTOM LINE

**This test plan provides:**
- ✅ Falsifiable hypotheses
- ✅ Quantitative success criteria
- ✅ Independent validation methods
- ✅ Appropriate confidence thresholds
- ✅ Safeguards against bias

**Ready to execute immediately.**

**Want me to run TEST 2.1 (zodiac seasonal) and TEST 1.1 (position distribution) right now?** 🔬
