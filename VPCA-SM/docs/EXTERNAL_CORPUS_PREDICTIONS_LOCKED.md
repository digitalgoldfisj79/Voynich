# EXTERNAL CORPUS VALIDATION - PRE-REGISTERED PREDICTIONS
**Date:** November 27, 2025  
**Status:** PREDICTIONS LOCKED BEFORE EXAMINING DATA  
**Corpus:** De materia medica (Dioscorides, Latin translation)

---

## CRITICAL: THESE PREDICTIONS ARE LOCKED

**I commit to:**
1. ✅ Testing these exact predictions on De materia medica
2. ✅ Not modifying predictions after seeing data
3. ✅ Reporting all results (including failures)
4. ✅ Not mining corpus for patterns that "look like 'e'"
5. ✅ Using pre-specified success criteria only

**Any deviations will be clearly marked as post-hoc and confidence penalties applied**

---

## PURPOSE: AVOID CIRCULAR REASONING

**WRONG approach (circular):**
- Look at corpus and find tokens with similar distribution to 'e'
- Claim these "validate" 'e' pattern
- Problem: We're mining for patterns that match our target

**CORRECT approach (independent validation):**
- Test whether KNOWN connectors (defined by linguistics) behave certain way
- Connectors defined independently of Voynichese
- Compare their behavior to 'e' behavior
- Could fail if Latin connectors don't match predictions

---

## INDEPENDENT DEFINITIONS (BEFORE EXAMINING DATA)

### Known Latin Connectors:

**Primary test set:**
1. **"et"** - coordinating conjunction (and)
2. **"cum"** - preposition/conjunction (with)
3. **"de"** - preposition (of, from, concerning)
4. **"atque"** - coordinating conjunction (and also)
5. **"vel"** - coordinating conjunction (or)
6. **"sive"** - coordinating conjunction (or if)

**Source:** Standard Latin grammar (not derived from Voynichese patterns)

**Why these:** Known connectors in Latin medical/scientific texts

---

### Control Set (Non-Connectors):

**Common nouns (should NOT match pattern):**
1. **"herba"** - herb
2. **"radix"** - root
3. **"folia"** - leaves
4. **"aqua"** - water
5. **"flos"** - flower

**Purpose:** Demonstrate specificity - if non-connectors also show pattern, test is non-specific

---

## PRE-REGISTERED PREDICTIONS

### PREDICTION EXT-1: Medial Position Dominance

**Claim:** Latin connectors will appear **>75% in medial position** within sentences

**Rationale:** 
- Connectors join elements, so appear between them
- General linguistic principle, not specific to 'e'
- Should be true for known connectors regardless of Voynichese

**Test method:**
- Classify each connector occurrence as: initial (first word of sentence), medial (middle), final (last word before period)
- Calculate % medial for each connector
- Average across all connectors

**Success criterion:** Average medial position >75%

**Statistical test:** Chi-square vs random baseline (~60% medial expected)

---

### PREDICTION EXT-2: High Frequency in Text

**Claim:** Connectors will appear in **30-40% of sentences**

**Rationale:**
- Medical texts list ingredients/steps requiring connection
- High connector usage expected in procedural/descriptive texts
- Compare to: 'e' appears in ~30% of Voynich lines

**Test method:**
- Count sentences
- Count sentences containing at least one connector
- Calculate percentage

**Success criterion:** 30-40% of sentences contain connectors

---

### PREDICTION EXT-3: Initial Position Rare

**Claim:** Connectors will show **<5% initial position**

**Rationale:**
- Connectors typically don't start sentences in Latin
- "Et" can start sentences but is minority usage
- Other connectors very rare initially

**Test method:**
- Count connector occurrences at sentence-initial position
- Calculate % of total connector occurrences

**Success criterion:** <5% initial position (averaged across connectors)

---

### PREDICTION EXT-4: Final Position Rare

**Claim:** Connectors will show **<10% final position**

**Rationale:**
- Connectors join elements, so don't end sentences
- Some flexibility for Latin word order but still rare
- Compare to: 'e' is 2.8% final in Biological

**Test method:**
- Count connector occurrences at sentence-final position
- Calculate % of total connector occurrences

**Success criterion:** <10% final position (averaged across connectors)

---

## CONTROL PREDICTIONS

### CONTROL 1: Non-Connector Position Distribution

**Prediction:** Non-connectors ("herba", "radix", "folia", "aqua", "flos") will NOT show >75% medial

**Expected:** More even distribution across positions

**Purpose:** Shows our test is specific to connectors

---

### CONTROL 2: Overall Baseline

**Prediction:** All words in corpus will show ~40-60% medial (natural prose baseline)

**Purpose:** Shows connectors are ENRICHED for medial position vs baseline

---

## SUCCESS CRITERIA (PRE-SPECIFIED)

### Confidence Update for 'e' Connector Hypothesis:

| Predictions Met | Interpretation | Confidence Change | New Confidence |
|----------------|----------------|-------------------|----------------|
| 4/4 + controls pass | Strong support | +20% | → 50-55% |
| 3/4 + controls pass | Moderate support | +15% | → 45-50% |
| 2/4 | Weak support | +5% | → 35-40% |
| <2/4 | No support | 0% | → 30-35% |
| Connectors match but controls also match | Non-specific | -5% | → 25-30% |

**Current 'e' confidence:** 30-35%  
**Post-validation range:** 25-55%

---

## COMPARISON PROTOCOL (AFTER PREDICTIONS TESTED)

**ONLY after testing all predictions above, we compare:**

| Behavior | Latin Connectors | Voynichese 'e' | Assessment |
|----------|------------------|----------------|------------|
| **Medial %** | [Result] | 72.7% (Bio), 91.8% (other) | Similar? |
| **Frequency** | [Result] | ~30% lines | Similar? |
| **Initial %** | [Result] | 24.6% (Bio), 2.2% (other) | Similar? |
| **Final %** | [Result] | 2.8% | Similar? |

**If behaviors match:** Supports connector hypothesis  
**If behaviors differ:** Weakens connector hypothesis

---

## WHAT WE CANNOT DO (LOCKED)

❌ Look for Latin words with similar frequency distribution to 'e'  
❌ Mine corpus for patterns that "look like" 'e' patterns  
❌ Adjust predictions after seeing data  
❌ Cherry-pick successful comparisons  
❌ Add new predictions mid-analysis  
❌ Ignore failed predictions  
❌ Change connector definitions post-hoc  

---

## ANALYSIS PROCEDURE (LOCKED)

```
1. Load De materia medica tokenized corpus
2. Identify sentence boundaries
3. For each connector word:
   a. Find all occurrences
   b. Classify position: initial, medial, final
   c. Calculate percentages
4. Test all 4 predictions
5. Test both control predictions
6. Calculate results for each
7. Report ALL results (including failures)
8. Apply pre-specified confidence update
9. THEN compare to 'e' behavior
10. Document any unexpected findings but don't use for confidence
```

**No deviations from this procedure permitted**

---

## STATISTICAL FRAMEWORK

**All tests will use:**
- Chi-square for position distributions
- p<0.05 significance threshold
- Sample size: all connector occurrences in corpus
- Effect size: enrichment ratios

**Baseline calculation:**
- Sample 1000 random non-connector words
- Calculate their position distribution
- Use as expected values for chi-square

---

## TRANSPARENCY COMMITMENT

**I commit to:**
1. ✅ Following exact pre-registered predictions
2. ✅ Not modifying after seeing corpus
3. ✅ Reporting all results honestly (including failures)
4. ✅ Using conservative confidence updates
5. ✅ Acknowledging if test fails
6. ✅ Not mining for additional patterns
7. ✅ Making all code and data available

---

## EXPECTED OUTCOMES (REALISTIC)

### Best Case (40% probability):
- All 4 predictions pass
- Controls confirm specificity
- Latin connectors match 'e' behavior
- 'e' → 50-55% confidence
- Strong support for connector hypothesis

### Expected Case (40% probability):
- 2-3 predictions pass
- Some similarities to 'e'
- 'e' → 35-45% confidence  
- Moderate support

### Worst Case (20% probability):
- <2 predictions pass
- Latin connectors don't behave like 'e'
- 'e' → 30-35% (no change or decrease)
- Connector hypothesis weakened
- But: Still valuable - learned 'e' is NOT like known connectors

**All outcomes are scientifically valuable**

---

## WHY THIS PROTOCOL IS ROBUST

✅ **Tests independently defined categories** (Latin connectors from linguistics)  
✅ **Pre-registered predictions** (locked before data)  
✅ **Falsifiable** (could fail and weaken hypothesis)  
✅ **Not circular** (not mining corpus for 'e'-like patterns)  
✅ **Has controls** (non-connectors, baseline)  
✅ **Clear success criteria** (quantitative, pre-specified)  
✅ **Transparent** (will report all results)

**This compares two independent observations:**
1. How known Latin connectors behave (test this)
2. How 'e' behaves in Voynichese (already observed)

**NOT:**
- Mining De materia medica for patterns resembling 'e'

---

## CORPUS REQUIREMENTS

**De materia medica specifications:**
- Latin translation (medieval or Renaissance)
- Tokenized format
- Sentence boundaries identifiable
- Minimum ~10,000 words for statistical power
- Medical/herbal content (appropriate comparison domain)

---

## TIMESTAMP AND LOCK

**Predictions locked:** November 27, 2025  
**Time:** [To be added with GitHub commit]  
**SHA hash:** [To be added]

**These predictions are now IMMUTABLE**

**Data has NOT been examined yet - predictions made independently**

**Ready to test on De materia medica when corpus is provided**

---

**Status:** PREDICTIONS LOCKED ✅  
**Data examined:** NO ✅  
**Ready for testing:** YES ✅  
**Protocol robust:** YES ✅  
**Avoids circularity:** YES ✅

---

**This is proper independent validation using external corpus with pre-registered predictions.**
