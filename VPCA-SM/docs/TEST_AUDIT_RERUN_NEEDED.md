# TEST AUDIT - What Needs Re-Running
**Date:** November 27, 2025  
**Issue:** All tests used incorrect section mapping  
**Action:** Identify what needs re-validation

---

## CORRECT DEFINITIVE MAPPING

1. **Herbal**: f1-f66v, f87-f102v
2. **Astronomical**: f67-f73v
3. **Biological**: f75-f84v
4. **Cosmological**: f85-f86v
5. **Pharmaceutical** (Recipes): f103-f116v

---

## TESTS TO RE-RUN

### TEST 3.1: Recipes Hold-Out
**What I tested:** f108-f116 (conservative) or f103-f116 (full)
**Correct mapping:** Pharmaceutical = f103-f116 ✓
**Status:** MAPPING CORRECT, but name wrong (called it "Recipes")

### TEST 4.2: 'da-i-in' on Herbal B
**What I tested:** f65-f66, f87-f88 ("Herbal B")
**Correct mapping:** These ARE part of Herbal ✓
**Status:** Correct range but insufficient data (n=19)

### TEST 5: Cross-Section Validation ⚠️ MAJOR ERROR
**What I tested:**
- "Herbal A" (f1-f57): 81.6% medial
- "Zodiac" (f70-f73): 96.0% medial  
- "Pharmaceutical" (f88-f102): 94.1% medial

**Problems with correct mapping:**
- "Herbal A" should include f1-f66, f87-f102 (not just f1-f57)
- "Zodiac" f70-f73 is part of Astronomical (f67-f73)
- "Pharmaceutical" f88-f102 is part of Herbal!

**Status:** COMPLETELY WRONG - needs full re-run

### TEST 8: Astronomical
**What I tested:** f58-f65 (wrong) or f58 only (wrong)
**Correct mapping:** Astronomical = f67-f73
**Status:** Just re-ran with correct mapping ✓ (83.7% medial)

### Phase 2 Biological
**What I tested:** f75-f84
**Correct mapping:** Biological = f75-f84 ✓
**Status:** CORRECT

---

## RE-RUN PRIORITY

**MUST re-run:**
1. ✅ TEST 8 Astronomical - DONE (83.7% medial, n=49)
2. ❌ TEST 5 Cross-section - WRONG sections, need complete re-run

**Already correct:**
- TEST 3.1 Recipes/Pharmaceutical (f103-f116) ✓
- Phase 2 Biological (f75-f84) ✓
- TEST 4.2 insufficient data regardless ✓

---

## ACTION PLAN

Re-run TEST 5 with correct sections:
1. Herbal (f1-f66, f87-f102) - complete section
2. Astronomical (f67-f73) - already have result
3. Biological (f75-f84) - already have result
4. Cosmological (f85-f86) - new test
5. Pharmaceutical (f103-f116) - already have result
