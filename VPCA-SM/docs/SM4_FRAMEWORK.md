# SM4: Compositional Semantics - Framework

**Status:** 🚧 IN DEVELOPMENT  
**Dependencies:** SM1 (morphology), SM2 (semantic fields), SM3 (frame patterns)  
**Goal:** Understand how PREFIX + ROOT + SUFFIX → MEANING

---

## 🎯 OBJECTIVE

**Build compositional rules for how Voynichese morphemes combine to create meaning.**

Starting with validated components:
- **SM1:** 11 prefixes, 784 roots, 14 suffixes (95% confidence)
- **SM2:** 8 semantic fields, 62.8% coverage (80% confidence)
- **SM3:** Frame patterns, VPCA transitions (85% confidence)

**Goal:** Map morpheme combinations → medieval concepts → testable interpretations

---

## 🧪 METHODOLOGY

### Phase 1: Compositional Patterns (Week 1)

**Identify how morphemes combine:**

1. **Prefix Functions (from SM1)**
   - ch- = intensifier/modifier
   - ot- = transition/change
   - ok- = constituent/unit
   - sh-, qo-, da-, yk-, ol-, sa-, op-, do- = ?

2. **Root Semantics (from SM2)**
   - Modifier/Relation: e, ee, k (165×)
   - Quality/State: ol, al, l, eo (228×)
   - Process/Active: i, ir, ot (190×)
   - Entity/Object: ch (54×)

3. **Suffix Functions (from SM1)**
   - -ey = state marker (344×)
   - -dy = process marker (270×)
   - -in = nominal/substantive (234×)
   - -ar = agent/doer (129×)
   - -al = quality/attribute (124×)

**Analysis:**
- What patterns appear? (e.g., ch- + Quality root + -y)
- Are certain combinations preferred?
- Do combinations correlate with VPCA states?

---

### Phase 2: Medieval Parallels (Week 2)

**Map to medieval Latin/Arabic/Romance constructions:**

**Example Mappings:**

**Latin Medical Texts:**
```
intensus calor        = "intense heat"
ch-ol-y              = "intensifier + quality + state"
                     = "intensified quality state" → heat?

mutatio humoris      = "change of humor"  
ot-e-dy              = "transition + relation + process"
                     = "transitional relational process" → mixing?

pars corporis        = "part of body"
ok-ai-in             = "constituent + root + nominal"
                     = "constituent substantive" → body part?
```

**Arabic/Romance Parallels:**
- Intensification prefixes (Latin: in-, super-, Arabic: al-)
- Process markers (Latin: -tio, Romance: -ment)
- State markers (Latin: -tas, Romance: -té/-dad)

---

### Phase 3: Context Validation (Week 3)

**Test interpretations against context:**

**Zodiac Context:**
- Labels on diagrams (human figures, zodiac signs)
- Seasonal/astrological associations
- Body part correspondences

**Tests:**
1. **Diagram Correspondence:**
   - Do "body part" interpretations match anatomy drawings?
   - Do "seasonal" terms cluster in correct zodiac signs?
   - Do "quality" terms appear on descriptive labels?

2. **Cross-Reference with SM3:**
   - Do "process" terms appear in C-heavy frames?
   - Do "state" terms appear in V-heavy frames?
   - Do "transition" terms bridge VPCA states?

3. **Consistency Check:**
   - Does same morpheme have same meaning across contexts?
   - Are there systematic polysemy patterns?
   - Do meanings compose predictably?

---

### Phase 4: Translation Templates (Week 4)

**Build actual translation rules:**

**Template Types:**

**Type 1: Simple Composition**
```
PREFIX + ROOT + SUFFIX → MEANING

ch- + od + -y = intensifier + quality-state + state-marker
              = "intense quality"
              = Medieval: "intensus" / "forte"
```

**Type 2: Frame-Based**
```
V→C→P frame with:
  V-token: ok-ai-in (constituent + nominal) = "body part"
  C-token: ot-e-dy (transition + process) = "changing"
  P-token: ch-ol-y (intensifier + quality + state) = "becoming hot"

Frame meaning: "Body part undergoes heating transformation"
Medieval: "Pars corporis calescat" (Let the body part warm)
```

**Type 3: Context-Dependent**
```
Same morphemes, different contexts:

Zodiac: ch-ol-y = "hot quality" (referring to humoral heat)
Herbal: ch-ol-y = "strong property" (referring to plant potency)
Recipes: ch-ol-y = "intense stage" (referring to preparation)
```

---

## 📊 EXPECTED OUTPUTS

### 1. Compositional Rules Database
**File:** `sm4_compositional_rules.json`

```json
{
  "rules": [
    {
      "pattern": "ch- + Quality-root + -y",
      "function": "intensified_quality_state",
      "medieval_parallel": "Latin: intensus [quality]",
      "examples": ["choly", "chody", "chary"],
      "confidence": 0.75
    }
  ]
}
```

### 2. Medieval Concept Mapping
**File:** `sm4_medieval_mappings.tsv`

```
voynich_pattern     medieval_concept       latin_parallel      confidence
ch-ol-y            intense_heat           intensus_calor      0.75
ot-e-dy            transformation         mutatio             0.70
ok-ai-in           body_part             pars_corporis        0.65
```

### 3. Translation Templates
**File:** `sm4_translation_templates.json`

```json
{
  "templates": {
    "zodiac": {
      "V_state": "descriptive (body part, quality)",
      "C_state": "transformational (process, change)",
      "P_state": "resultative (final state, action)"
    }
  }
}
```

### 4. Validation Report
**File:** `sm4_validation_report.txt`

- Diagram correspondence tests
- Cross-section consistency
- Medieval parallel strength
- Overall confidence estimates

---

## 🚨 CRITICAL CONSTRAINTS

### Must NOT:
❌ **Claim definitive translations** (too uncertain)
❌ **Ignore context variation** (meanings shift by section)
❌ **Force medieval parallels** (may not always map cleanly)
❌ **Overclaim semantic precision** (many roots still unclear)

### Must DO:
✅ **Provide probability estimates** for each interpretation
✅ **Show alternative readings** where uncertain
✅ **Test against independent evidence** (diagrams, context)
✅ **Maintain epistemic humility** (this is hypothesis, not proof)

---

## 🎯 SUCCESS CRITERIA

**Minimum Viable SM4 (60% confidence):**
- [ ] 20+ compositional rules identified
- [ ] 50+ medieval parallels mapped
- [ ] 10+ translation templates created
- [ ] Context validation shows >70% consistency

**Strong SM4 (75% confidence):**
- [ ] 50+ compositional rules
- [ ] 100+ medieval parallels
- [ ] 25+ translation templates
- [ ] Context validation shows >80% consistency
- [ ] Cross-section replication confirmed

**Exceptional SM4 (85% confidence):**
- [ ] 100+ compositional rules
- [ ] 200+ medieval parallels
- [ ] Full translation framework
- [ ] Independent validation (non-zodiac sections)
- [ ] Predictive power demonstrated

---

## 📋 IMPLEMENTATION PLAN

### Week 1: Pattern Analysis
**Script:** `sm4_compositional_patterns.py`
- Load SM1 morphemes + SM2 semantic fields
- Identify common PREFIX+ROOT+SUFFIX combinations
- Correlate with VPCA states (SM3)
- Output: compositional pattern database

### Week 2: Medieval Mapping
**Script:** `sm4_medieval_parallels.py`
- Load Latin/Arabic medical texts
- Match Voynich patterns to medieval constructions
- Calculate parallel strength scores
- Output: medieval concept mapping

### Week 3: Context Validation
**Script:** `sm4_context_validation.py`
- Test interpretations against diagrams
- Check cross-section consistency
- Validate seasonal/humoral associations
- Output: validation report with confidence scores

### Week 4: Translation Templates
**Script:** `sm4_translation_templates.py`
- Build frame-specific translation rules
- Create section-specific templates
- Generate example translations
- Output: translation template database

---

## 🔬 EXAMPLE: WORKED ANALYSIS

### Token: "chody"

**SM1 Decomposition:**
- Prefix: ch- (intensifier)
- Root: od
- Suffix: -y (state marker)

**SM2 Semantic Field:**
- Root 'od' not in top semantic fields
- Check broader patterns: 'o' roots → Quality/State (48×)
- Hypothesis: 'od' = quality-related root

**SM3 Frame Context:**
- Most common in C-state (change/transformation)
- Appears in C→P transitions
- Suggests: transitional quality

**Medieval Parallel:**
- Latin: "mutatus" (changed/altered)
- Or: "intensus" (intensified)
- Or: "fortis" (strong)

**Compositional Interpretation:**
```
ch- (intensifier) + od (quality?) + -y (state)
= "intensified quality state"

Context options:
- Zodiac: "intense heat" (calor intensus)
- Herbal: "strong property" (virtus fortis)
- Recipe: "concentrated stage" (gradus concentratus)
```

**Confidence:** ~65%
- Morphology: validated (95%)
- Semantic field: inferred (60%)
- Medieval parallel: plausible (70%)
- **Overall: moderate confidence**

---

## ⚠️ KNOWN CHALLENGES

### Challenge 1: Root Polysemy
**Problem:** Roots may have multiple meanings depending on context.

**Solution:** 
- Document context-dependent meanings
- Use frame patterns (SM3) to disambiguate
- Maintain probability distributions, not single translations

### Challenge 2: Medieval Concept Gaps
**Problem:** Some Voynich patterns may not map cleanly to medieval concepts.

**Solution:**
- Allow for novel combinations
- Consider vernacular/regional variations
- Don't force parallels where unclear

### Challenge 3: Validation Difficulty
**Problem:** Hard to independently verify semantic interpretations.

**Solution:**
- Use diagram correspondence as proxy
- Test cross-section consistency
- Look for predictive power (can we guess meanings in new contexts?)

### Challenge 4: Circularity Risk
**Problem:** Risk of confirmation bias (finding what we expect).

**Solution:**
- Pre-register predictions before testing
- Use blind validation (test on unseen data)
- Require multiple independent lines of evidence

---

## 🎯 FIRST STEPS (This Week)

### Immediate Actions:

1. **Script 1:** `sm4_pattern_analyzer.py`
   - Load SM1/SM2 data
   - Count PREFIX+ROOT+SUFFIX combinations
   - Identify 20 most common patterns
   - Correlate with VPCA states

2. **Script 2:** `sm4_medieval_matcher.py`
   - Load Latin medical corpus
   - Extract morphological patterns
   - Match to Voynich patterns
   - Score parallel strength

3. **Documentation:** `SM4_PROGRESS.md`
   - Track weekly progress
   - Document findings
   - Maintain confidence estimates
   - Flag uncertainties

---

## 📖 READING MATERIALS

**Medieval Latin Medical Texts:**
- Circa Instans (herbal properties)
- Tacuinum Sanitatis (health handbook)
- Macer Floridus (botanical descriptions)

**Morphological Resources:**
- Latin morphology databases
- Romance language etymologies
- Arabic medical terminology

**Methodology:**
- Compositional semantics theory
- Historical linguistics methods
- Bayesian probability for uncertainty

---

## ✅ SUMMARY

**SM4 Goals:**
- Understand how morphemes combine → create meaning
- Map to medieval concepts
- Build translation templates
- Validate against context

**Approach:**
- Conservative (probability-based)
- Evidence-driven (multiple validations)
- Transparent (document uncertainties)
- Falsifiable (testable predictions)

**Timeline:**
- Week 1: Pattern analysis
- Week 2: Medieval parallels
- Week 3: Context validation
- Week 4: Translation templates

**Expected Confidence:** 60-75% (lower than SM1/SM2, inherently more uncertain)

---

**Ready to start SM4 implementation?** 🚀
