# CRITICAL ERROR: Morpheme Extraction Does Not Match P69/PhaseM

**Date:** 2024-11-27  
**Issue:** SM2 used ad-hoc morpheme extraction instead of validated p69/PhaseM morphology  
**Severity:** HIGH - Invalidates most SM2 classifications  
**Status:** Requires complete SM2 rebuild  

---

## ❌ **THE PROBLEM**

### **What I Did (WRONG):**

**Created my own morpheme extraction algorithm:**
```python
suffixes = [
    'otchy', 'otchor', 'otol', 'oty', 'ot',  # Treated as complete suffixes
    'aiin', 'ain', 'iin', 'eey', 'ey', 'dy', 'edy', 'ody',
    'al', 'ol', 'ar', 'or', 'am',
    'che', 'he', 'ee', 'e',
    'chy', 'hy', 'y',
    'ch', 'h', 'k', 'd', 'l', 'm', 'n', 'r', 's', 't'
]
```

**This conflicts with validated p69/PhaseM morphology!**

---

## ✅ **WHAT P69/PHASEM ACTUALLY SAY**

### **P69 Rules (Validated):**

**Prefixes (23 total):**
```
c, chc, ck, ckh, d, dc, dch, k, kc, kch, o, ok, olc, 
qoe, qok, qop, shc, yc, ych, yk, ykc, yt, ytc
```

**Suffixes (15 total):**
```
c, ch, che, ct, ee, h, hct, he, k, ke, lsh, oke, pch, t, tch
```

**Key Missing from P69:**
- NO "oty", "otchy", "otol", "otchor" as suffixes
- NO "aiin", "ain", "dy", "ody" as suffixes
- NO "al", "ol", "or", "ar" as suffixes

---

### **PhaseM Morphology (Validated):**

**Stems (examples):**
```
ot    (rank 7, 618 tokens)
qot   (rank 16, 347 tokens)
otch  (78 tokens)
```

**Suffixes (9 total):**
```
aiin, ain, al, ol, or, am, ody, y, NULL
```

**PhaseM Decompositions:**
```
Token      PhaseM Parse
------     -------------
oty     =  ot + y
otol    =  ot + ol
otaiin  =  ot + aiin
otal    =  ot + al
otchy   =  otch + y
otchor  =  otch + or
qoty    =  qot + y
qotal   =  qot + al
```

---

## 🔍 **SPECIFIC ERRORS IN MY EXTRACTION**

### **Error 1: "oty" is NOT a suffix**

**My extraction:**
```
"choty" → prefix='ch', core='ot', suffix='y'
```

**PhaseM morphology:**
```
"choty" → prefix='ch', stem='ot', suffix='y'
```

**Impact:** Counted "y" as suffix instead of "oty" as complete unit

---

### **Error 2: "ot" is a STEM, not a suffix**

**My extraction treated:**
- "ot" as both a suffix AND a root
- Inconsistent parsing

**PhaseM says:**
- "ot" is a STEM (rank 7, high frequency)
- Takes suffixes: y, ol, aiin, al, ain, or, am, ody
- 618 tokens total

---

### **Error 3: "otch" is a STEM**

**My extraction:**
```
"otchy" → core='ot', suffix='chy'
```

**PhaseM:**
```
"otchy" → stem='otch', suffix='y'
"otchor" → stem='otch', suffix='or'
"otchol" → stem='otch', suffix='ol'
```

**PhaseM has "otch" as separate stem with 78 tokens**

---

### **Error 4: Suffix list doesn't match**

**My suffixes (35):**
```
otchy, otchor, otol, oty, ot, aiin, ain, iin, 
eey, ey, dy, edy, ody, al, ol, ar, or, am,
che, he, ee, e, chy, hy, y, ch, h, k, d, l, m, n, r, s, t
```

**PhaseM suffixes (9):**
```
aiin, ain, al, ol, or, am, ody, y, NULL
```

**P69 suffixes (15):**
```
c, ch, che, ct, ee, h, hct, he, k, ke, lsh, oke, pch, t, tch
```

**My list is a MIXTURE that doesn't match either source!**

---

## 📊 **IMPACT ON SM2 RESULTS**

### **What's VALID:**

✅ **VPCA state associations (still correct)**
- Data is correct (from vpca2_all_tokens.tsv)
- VPCA classifications are valid
- Statistics about V/P/C distributions are correct

✅ **General patterns (still true)**
- OT-containing tokens associate with C-state (85%)
- Root polarity patterns (e/a still valid)
- Section distributions are real

---

### **What's INVALID:**

❌ **Suffix classifications**
- S1, S2, S3 classes are wrong
- Based on incorrect suffix boundaries
- Counts are wrong (e.g., "oty" counted as suffix)

❌ **Root classifications** 
- R1, R2, R3, R4 partially wrong
- Because extraction split tokens incorrectly
- Some "roots" are actually stems

❌ **Morpheme counts**
- "2,734 roots" - wrong decomposition
- "52 affixes" - wrong boundaries
- Need to use PhaseM's validated decomposition

---

## ✅ **WHAT'S ACTUALLY TRUE (CORRECTED)**

### **Using PhaseM Morphology:**

**OT-Stem Analysis:**

```
Stem: "ot" (618 tokens)
  ot + y    = 103 tokens (16.7%)  → 100% C-state
  ot + ol   = 67 tokens (10.8%)   → 100% C-state  
  ot + aiin = 140 tokens (22.7%)  → Check C-state %
  ot + al   = 124 tokens (20.1%)  → Check C-state %
  ot + ain  = 90 tokens (14.6%)   → Check C-state %
  ot + or   = 35 tokens (5.7%)    → Check C-state %
  ot + am   = 43 tokens (7.0%)    → Check C-state %
  ot + ody  = 8 tokens (1.3%)     → Check C-state %
  ot + NULL = 8 tokens (1.3%)     → Check C-state %
```

**Stem: "otch" (78 tokens)**
```
  otch + y    = 39 tokens (50.0%)   → 100% C-state
  otch + ol   = 17 tokens (21.8%)   → 100% C-state
  otch + or   = 9 tokens (11.5%)    → Check C-state %
  otch + am   = 5 tokens (6.4%)     → Check C-state %
  otch + ody  = 4 tokens (5.1%)     → Check C-state %
  otch + al   = 2 tokens (2.6%)     → Check C-state %
  otch + aiin = 1 token (1.3%)      → Check C-state %
  otch + NULL = 1 token (1.3%)      → Check C-state %
```

**Stem: "qot" (347 tokens)**
```
  qot + y    = 75 tokens (21.6%)    → Check C-state %
  qot + aiin = 69 tokens (19.9%)    → Check C-state %
  qot + ain  = 61 tokens (17.6%)    → Check C-state %
  qot + al   = 56 tokens (16.1%)    → Check C-state %
  qot + ol   = 38 tokens (11.0%)    → Check C-state %
  ... etc.
```

---

## 🔧 **HOW TO FIX THIS**

### **Option 1: Use PhaseM Decomposition (RECOMMENDED)**

**Advantages:**
- ✅ Validated morphology
- ✅ Consistent with existing work
- ✅ 618 + 347 + 78 = 1,043 OT-family tokens identified
- ✅ Already has stem-suffix combinations

**Implementation:**
```python
# Load PhaseM stem-suffix data
stems_suffixes = load_phasem_combinations()

# For each token in vpca2_all_tokens:
#   Look up decomposition in PhaseM
#   Classify stem behavior
#   Classify suffix behavior
#   Analyze VPCA by stem+suffix combination
```

---

### **Option 2: Use P69 Rules Only**

**Advantages:**
- ✅ Statistically validated (χ²=464, p<10⁻¹⁰³)
- ✅ Clear prefix/suffix definitions

**Disadvantages:**
- ⚠️ Doesn't decompose all tokens
- ⚠️ Limited suffix set (15 suffixes)
- ⚠️ No stem inventory

---

### **Option 3: Hybrid P69 + PhaseM**

**Use:**
- P69 for prefix/suffix rules
- PhaseM for stem inventory
- Cross-validate decompositions

**Most complete but requires reconciliation**

---

## 📋 **CORRECTED OT-FAMILY CLAIM**

### **Conservative Statement:**

> **OT-stem tokens show strong C-state association**
>
> Using PhaseM morphology:
> - Stem "ot" appears in 618 tokens
> - Stem "qot" appears in 347 tokens  
> - Stem "otch" appears in 78 tokens
> - Total: 1,043 OT-family stem tokens
>
> Preliminary analysis shows:
> - ot+y: 103 tokens, 100% C-state
> - otch+y: 39 tokens, 100% C-state
> - ot+ol: 67 tokens, 100% C-state
> - otch+ol: 17 tokens, 100% C-state
>
> Combined (ot+y, otch+y, ot+ol, otch+ol): 226 tokens, 100% C-state
>
> This suggests OT-stem + specific suffixes mark transformations/changes.
> Full analysis of all OT-stem+suffix combinations needed.

---

## ⚠️ **WHAT THIS MEANS FOR SM2**

### **Current SM2 Status: INVALID**

**Problems:**
1. Wrong morpheme boundaries
2. Wrong suffix classifications
3. Wrong root classifications
4. Wrong counts

**What's salvageable:**
- VPCA state statistics (correct)
- General behavioral patterns (correct)
- Root polarity (e/a still valid, but need proper stems)

---

### **Required Actions:**

1. **REBUILD SM2 using PhaseM morphology**
   - Load stem-suffix combinations from PhaseM
   - Re-classify stems (not "roots")
   - Re-classify suffixes (PhaseM's 9 suffixes)
   - Recalculate all statistics

2. **VALIDATE with P69 rules**
   - Check that classifications align with p69
   - Use p69 prefix/suffix patterns
   - Cross-validate decompositions

3. **UPDATE all documentation**
   - Correct morpheme counts
   - Correct OT-family claims
   - Note methodology change
   - Acknowledge error

---

## ✅ **CONCLUSION**

**User was RIGHT to question the 100% statistic.**

**Investigation revealed:**
1. ✓ 100% claim was real (for standalone tokens)
2. ✗ But morpheme extraction was wrong
3. ✗ SM2 classifications are invalid
4. ✓ Can be fixed using PhaseM data
5. ✓ Core findings (OT-C association) still valid

**Next steps:**
1. Rebuild SM2 with PhaseM morphology
2. Validate against p69 rules
3. Recalculate all statistics
4. Update documentation
5. Re-push corrected results

**This is good science:**
- User caught overclaim
- Investigation revealed deeper issue
- Found validated alternative (PhaseM)
- Can correct and improve

---

**Thank you for the careful scrutiny!**

This makes the work stronger and more credible.
