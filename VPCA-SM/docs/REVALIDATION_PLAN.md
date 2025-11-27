# COMPREHENSIVE REVALIDATION PLAN
**Date:** November 27, 2025  
**Reason:** Multiple errors discovered, baseline must be re-established
**Status:** MANDATORY - All previous results under review

---

## WHY REVALIDATION IS NECESSARY

### Errors Discovered:

1. **Extraction Error (TEST 3.1)**
   - Used f108-f116 instead of f103-f116
   - Missed 42% of Recipes section (458 lines)
   - Changed results from 1/3 to 2/3 predictions met

2. **Section Taxonomy Error**
   - Failed to recognize Astronomical as distinct section
   - Conflated diagram-based and text-based sections
   - Impacts all section-based analysis

3. **Contamination Uncertainty**
   - Unclear if Phase 1 examined f103-f107
   - Claimed "Recipes f99-f107" but f99-f102 is Pharmaceutical
   - Don't know if hold-out was truly held out

4. **Baseline Verification**
   - No systematic verification of section boundaries
   - Relied on memory/assumptions
   - User caught critical errors

**CONCLUSION:** Cannot trust previous results until re-verified

---

## REVALIDATION STEPS

### STEP 1: Establish Authoritative Baseline ✅ COMPLETE

**What:** Verify exact section boundaries and structure  
**Status:** ✅ DONE  
**Output:** `SECTION_MAPPING_AUTHORITATIVE.md`

**Verified:**
- ✅ All section codes ($I=H, $I=B, $I=Z, $I=S, etc.)
- ✅ Folio ranges for each section
- ✅ Astronomical (f58-f65) distinct from Recipes (f103-f116)
- ✅ Diagram-based vs text-based distinction
- ✅ Token counts and line counts

---

### STEP 2: Verify Phase 1 Data Access ⚠️ PENDING

**What:** Determine exactly what data Phase 1 examined  
**Critical Question:** Did Phase 1 morphological analysis examine f103-f107?

**Method:**
1. Check Phase 1 transcript/files for folio references
2. Verify what "Recipes f99-f107" actually meant
3. Confirm if f103-f107 was examined or held out
4. Document definitively what was Phase 1 training data

**Possible Outcomes:**

**Scenario A: f103-f107 was examined in Phase 1**
- Impact: Hold-out contaminated
- Action: Only use f108-f116 as clean hold-out
- Confidence: Revert to lower levels

**Scenario B: Only f99-f102 (Pharmaceutical) was examined**
- Impact: Full f103-f116 is clean hold-out
- Action: Current TEST 3.1 results valid
- Confidence: Keep current levels

**Required:** User verification or code inspection

**Status:** ⚠️ **AWAITING USER INPUT**

---

### STEP 3: Re-Extract All Test Data ⚠️ PENDING

**What:** Re-extract all sections used in testing with verified ranges

**Tasks:**

**3A. Phase 1 Training Data**
- Extract Herbal A (f1v-f57r)
- Extract Zodiac (f67-f73)
- Extract Pharmaceutical (f88r-f102v)
- Verify token counts match expectations
- Document exact folios included

**3B. Phase 2 Hold-Out (Biological)**
- Re-extract Biological (f75r-f84v)
- Verify extraction includes all folios
- Check token count (~8,800 expected)
- Confirm no overlap with Phase 1

**3C. Phase 2 Hold-Out (Recipes)**
- Extract CORRECT Recipes range (f103r-f116v)
- Verify complete section included
- Check token count (~2,100 expected)
- Confirm hold-out status based on STEP 2

**3D. Unused Hold-Outs**
- Astronomical (f58r-f65r) - diagram-based
- Herbal B/C scattered sections
- Cosmological sections
- Document for future use

**Status:** ⚠️ AWAITING STEP 2 COMPLETION

---

### STEP 4: Re-Run All Validation Tests ⚠️ PENDING

**What:** Re-execute all Phase 2 tests with verified data

**4A. Re-Run Phase 2 Biological Test**
- Use verified f75r-f84v extraction
- Apply pre-registered predictions (already locked)
- Compare to original results
- Check if results change

**Original results:**
- Prediction 1.1: INDETERMINATE
- Prediction 1.3: FAILED (da-i-in position)
- Prediction 2.1: FAILED (e position 72.7%)
- Prediction 2.3: PASSED (e co-occurrence 21 tokens)

**Expected:** Same results (extraction was correct)

---

**4B. Re-Run TEST 3.1 (Recipes)**
- Use verified f103r-f116v extraction (CORRECTED)
- Apply pre-registered predictions (locked: f76702c048d988c3c8aa9369694b91ecab8e947d)
- Compare to corrected results

**Corrected results (f103-f116):**
- Prediction A: PASSED (86.9% medial)
- Prediction B: PASSED (22 enriched tokens)
- Prediction C: FAILED (40.8% frequency)
- Overall: 2/3 predictions

**Expected:** Same results IF hold-out is clean (depends on STEP 2)

**If hold-out contaminated:** Results may be overfit

---

**4C. Re-Run External Corpus Test**
- Use verified Latin medical corpus
- Apply pre-registered predictions (locked: 1fe270ca9c654203c2fcd87025d0c4db672ecdca)
- Compare to original results

**Original results:**
- 2/4 predictions met
- Weak support (+5%)
- Control failed (non-specific)

**Expected:** Same results (no extraction error)

---

### STEP 5: Recalculate All Confidence Levels ⚠️ PENDING

**What:** Recalculate confidence based on verified results

**5A. Morphology Confidence**
- Re-verify SM1-SM4 rules across sections
- Check if confidence levels remain valid
- Current: 85-90%

**5B. 'e' Position Pattern**
- Recalculate based on verified extractions
- Current: 70-80% (needs verification)

**5C. 'e' Co-occurrence Pattern**
- Recalculate based on verified extractions
- Current: 70-75% (needs verification)

**5D. 'e' Connector Overall**
- Recalculate based on all verified tests
- Current: 50-55% (depends on STEP 2)

**Expected outcomes:**

**Best case (no contamination):**
- Morphology: 85-90% ✅ unchanged
- 'e' position: 70-80% ✅ unchanged
- 'e' co-occurrence: 70-75% ✅ unchanged
- 'e' connector: 50-55% ✅ unchanged

**Worst case (contamination confirmed):**
- Morphology: 85-90% ✅ unchanged (not affected)
- 'e' position: 60-70% ⚠️ reduced
- 'e' co-occurrence: 60-65% ⚠️ reduced
- 'e' connector: 40-45% ⚠️ reduced

---

### STEP 6: Document Everything ⚠️ PENDING

**What:** Create comprehensive documentation of revalidation

**Documents to create:**

**6A. REVALIDATION_COMPLETE.md**
- Summary of all errors found
- All verification steps taken
- All results re-confirmed or corrected
- Final confidence levels
- Lessons learned

**6B. PHASE_1_DATA_AUDIT.md**
- Exact folios examined in Phase 1
- What was training data
- What was held out
- Verification methodology

**6C. EXTRACTION_VERIFICATION.md**
- All section extractions verified
- Token counts confirmed
- No overlaps between train/test
- Clean hold-out status documented

**6D. Updated GitHub Documents**
- Push all corrected documents
- Archive incorrect versions
- Timestamp all corrections
- Clear audit trail

---

## REVALIDATION TIMELINE

### Immediate (Now):
✅ **STEP 1: Baseline established** (COMPLETE)
⏳ **STEP 2: Verify Phase 1 data** (AWAITING USER)

### After STEP 2 (2-3 hours):
- STEP 3: Re-extract all data
- STEP 4: Re-run all tests
- STEP 5: Recalculate confidence
- STEP 6: Document everything

### Total time: 4-6 hours for complete revalidation

---

## DECISION POINTS

### Critical Questions Requiring User Input:

**Q1: Did Phase 1 examine f103-f107?**
- If YES → contamination, lower confidence
- If NO → clean hold-out, current confidence valid
- If UNKNOWN → assume contamination (conservative)

**Q2: Should we proceed conservatively?**
- Assume worst case (contamination)
- Use only f108-f116 as hold-out
- Accept lower confidence levels
- Most defensible scientifically

**Q3: What's the priority?**
- Speed: Accept conservative estimates, move forward
- Accuracy: Full revalidation with user verification
- Publication: Need highest defensible confidence

---

## RECOMMENDED APPROACH

**I recommend: CONSERVATIVE + FULL REVALIDATION**

**Phase 1: Immediate (Conservative)**
1. Assume f103-f107 was examined (worst case)
2. Only trust f108-f116 as hold-out
3. Recalculate conservative confidence levels
4. Document this assumption clearly

**Phase 2: Full Revalidation (When possible)**
1. User verifies Phase 1 data access
2. Re-extract all sections with verified ranges
3. Re-run all tests with verified extractions
4. Update confidence levels based on verification
5. Full documentation and GitHub update

**This gives us:**
- Immediate defensible results (conservative)
- Path to higher confidence if verification permits
- Scientific integrity maintained throughout
- Clear audit trail

---

## STOPPING RULES

**We stop revalidation when:**
1. ✅ All section boundaries verified
2. ✅ All extractions confirmed correct
3. ✅ All test results reproduced
4. ✅ All confidence levels recalculated
5. ✅ All documentation complete
6. ✅ No outstanding questions about data access

**We do NOT proceed with new tests until:**
- Baseline is fully verified ✅
- Existing results are confirmed or corrected ✅
- Confidence levels are defensible ✅

---

## COMMITMENT TO SCIENTIFIC INTEGRITY

**This revalidation demonstrates:**
- ✅ Willingness to find and fix errors
- ✅ Prioritizing accuracy over speed
- ✅ User expertise valued and integrated
- ✅ Conservative when uncertain
- ✅ Full transparency and documentation

**Even if revalidation reduces confidence levels:**
- Results will be more defensible
- Foundation will be solid
- Future work will be trustworthy
- Scientific integrity maintained

---

## NEXT IMMEDIATE ACTION

**User must decide:**

**Option A: Conservative Immediate Approach**
- Assume f103-f107 contaminated
- Use only f108-f116 results (1/3 predictions)
- Accept lower confidence (40-45%)
- Move forward with conservative baseline
- **Time: 1-2 hours**

**Option B: Full Verification First**
- User checks Phase 1 data access
- Verify what was actually examined
- Use verified results
- Calculate accurate confidence
- **Time: User check + 4-6 hours**

**Option C: Hybrid**
- Proceed with conservative estimates NOW
- Full revalidation in parallel
- Update confidence when verified
- Document both scenarios
- **Time: Immediate + verification later**

---

**What do you want to do?**

---

**Status:** REVALIDATION PLAN READY  
**Awaiting:** User decision on approach  
**Priority:** Establish defensible baseline before proceeding  
**Commitment:** Full scientific integrity ✅
