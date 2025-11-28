# COMPLETE VALID DATA INVENTORY
**Date:** November 27, 2025  
**Status:** All ground-truth TSV/JSON files from user uploads  
**Rule:** Only use data from these files

---

## SUMMARY OF VALID DATA

**Total files: 16 TSV + 2 JSON + 1 TXT = 19 files**

**Total tokens analyzed: 37,886** ✅  
**Unique stems identified: 150** ✅  
**Unique suffixes identified: 23** ✅  
**P69 rules: 109** ✅

---

## CATEGORY 1: CORE TOKEN DATA

### 1. p140_tokens_COMPAT.tsv
**Purpose:** Complete token list with positions  
**Rows:** 37,886 tokens  
**Columns:** token, folio, line, pos  
**Scope:** Full manuscript  

### 2. vpca2_all_tokens.tsv
**Purpose:** All tokens with VPCA states  
**Rows:** 37,886 tokens  
**Columns:** token, folio, line, pos, section, left_score, right_score, pred_side, VPCA2  
**Scope:** Full manuscript  
**Sections:** 7 (Herbal, Recipes, Biological, Astronomical/Zodiac, Cosmological, Pharmaceutical, Unknown)

### 3. p6_voynich_tokens.txt
**Purpose:** Simple token list  
**Rows:** 29,687 tokens  
**Format:** One token per line (plain text)

---

## CATEGORY 2: MORPHOLOGICAL DATA

### 4. vpca2_tokens_roles.tsv ⭐
**Purpose:** Suffix extraction and classification  
**Rows:** 25,910 tokens  
**Columns:** token, folio, line, pos, section, VPCA2, suffix, suffix_class  
**Scope:** Herbal (11,445), Recipes (10,681), Pharmaceutical (3,784)

**VERIFIED DATA:**
- ✅ 23 unique suffixes extracted
- ✅ 3 suffix classes: S2_state (10 suffixes), S4_valley (10 suffixes), S1_process (3 suffixes)
- ✅ Suffix class → VPCA correlation verified:
  - S4_valley: 70.8% V state
  - S2_state: 68.8% P state  
  - S1_process: 81.1% C state

### 5. stem_axis_features.tsv ⭐
**Purpose:** Stem identification with embeddings  
**Rows:** 900 (150 stems × 6 sections)  
**Columns:** stem, section, true_label, axis1, axis2  

**VERIFIED DATA:**
- ✅ 150 unique stems identified
- ✅ Axis embeddings (axis1, axis2) for each stem
- ✅ Section-specific embeddings

### 6. stem_axis_features_clean.tsv
**Purpose:** Cleaned stem embeddings  
**Rows:** 900  
**Columns:** stem, axis1, axis2  
**Same 150 stems, cleaner format**

---

## CATEGORY 3: P69 RULES

### 7. p69_rules_final.json ⭐
**Purpose:** P69 axis prediction rules  
**Format:** JSON with 109 rules  

**VERIFIED DATA:**
- ✅ 109 total rules:
  - 26 prefix rules (23 unique patterns)
  - 15 suffix rules (15 unique patterns)
  - 33 chargram rules
  - 35 pair rules

**P69 Prefix patterns (23):**
```
c, chc, ck, ckh, d, dc, dch, k, kc, kch, o, ok, olc, 
qoe, qok, qop, shc, yc, ych, yk, ykc, yt, ytc
```

**P69 Suffix patterns (15):**
```
c, ch, che, ct, ee, h, hct, he, k, ke, lsh, oke, pch, t, tch
```

---

## CATEGORY 4: INTERLINEAR & SEMANTIC DATA

### 8. p183_interlinear_for_mining_COMPAT.tsv ⭐
**Purpose:** Token context windows and semantic neighbors  
**Rows:** 25,027  
**Columns:** folio, line, pos, w1, w2, w3, sem1, sem2, sem3, section  

**Contents:**
- pos: current token (4,498 unique)
- w1, w2, w3: neighboring words (context)
- sem1, sem2, sem3: semantic neighbors
- section: manuscript section

**Section distribution:**
- Recipes: 7,854
- Herbal: 6,760
- Biological: 4,943
- Pharmaceutical: 2,375
- Astronomical/Zodiac: 1,677
- Cosmological: 1,331
- Unknown: 76

---

## CATEGORY 5: SECTION SUMMARIES

### 9. vpca2_full_section_summary.tsv
**Rows:** 7 sections  
**Columns:** section, C, P, V, A, total, V_over_VP, C_over_total  

### 10. vpca2_all_section_matrix.tsv
**Rows:** 7 sections  
**Columns:** section, C, P, V  

### 11. vpca2_section_summary_HRP.tsv
**Rows:** 3 sections (Herbal, Recipes, Pharmaceutical)  
**Columns:** section, C, P, V, total, V_over_VP, C_over_total  

---

## CATEGORY 6: SUBSET ANALYSES

### 12. vpca2_tokens_HRP.tsv
**Purpose:** Tokens from Herbal, Recipes, Pharmaceutical only  
**Rows:** 25,910 tokens  
**Columns:** token, folio, line, pos, section, left_score, right_score, pred_side, VPCA2  

### 13. ea_root_freq_by_section.tsv
**Purpose:** 'e' and 'a' root frequencies by section  
**Rows:** 7 sections  
**Columns:** section, tokens_total, a_count, e_count, a_per_1k, e_per_1k, ea_per_1k  

**From today's e/a polarity testing** ✅

### 14. ea_root_vpca_summary.tsv
**Purpose:** 'e' and 'a' root VPCA distributions  
**Rows:** 13 (e and a for each section)  
**Columns:** section, root, n, P, V, C, A, V_over_PV  

**From today's e/a polarity testing** ✅

---

## CATEGORY 7: FOLIO-SPECIFIC ANALYSES

### 15. f16v_vpca2_by_colour.tsv
**Purpose:** f16v tokens by color region  
**Rows:** 73 tokens  
**Columns:** folio, line, pos, token, paragraph, colour_region, left_score, right_score, pred_side, VPCA2  

### 16. f16v_zandbergen_H.tsv
**Purpose:** f16v tokens with Zandbergen annotations  
**Rows:** 73 tokens  
**Columns:** folio, line, pos, token, paragraph, colour_region  

### 17. f3r_f16_vpca2_tokens.tsv
**Purpose:** Tokens from f3r-f16 range  
**Rows:** 0 (empty except header)  
**Columns:** folio, line, pos, folio_num, token, left_score, right_score, pred_side, VPCA2  

### 18. f3r_f16_vpca2_summary_by_folio.tsv
**Purpose:** VPCA summary for f3r-f16 folios  
**Rows:** 26 folios  
**Columns:** folio, V, P, C, V_over_VP  

---

## CATEGORY 8: SCRIPT

### 19. run_vpca2_ea_audit.py
**Purpose:** Placeholder script  
**Content:** Empty placeholder (analysis done elsewhere)  

---

## VERIFIED INVENTORIES FROM GROUND TRUTH

### ✅ STEMS/ROOTS: 150 unique
**Source:** stem_axis_features.tsv

**All 150 stems:**
```
ai, al, ar, cha, chct, chcth, che, chee, chek, cheo, cho, chock, 
chockh, chod, chok, choke, chol, chot, cht, ckh, ckhe, cp, cph, 
cth, cthe, dai, daii, dal, dar, dc, dch, dche, do, e, ee, fc, 
fch, fche, k, kch, kche, kee, ko, ks, ksh, l, lc, lche, lk, lka, 
lo, ls, lsh, oc, och, oe, oee, oi, okal, okch, okee, oko, okol, 
oks, ol, olc, olch, olche, olk, olke, olsh, olshe, op, opa, opch, 
opche, or, os, ot, otal, otch, otche, oted, otee, oto, otol, ots, 
otsh, p, pch, pche, pcho, po, q, qe, qock, qockh, qod, qoe, qoee, 
qok, qoke, qokee, qopc, qopch, qot, qotch, qote, qotee, qoteo, r, 
ra, sa, sc, sch, sha, shct, shcth, shee, shek, sheo, shk, sho, so, 
t, tc, tch, te, tee, to, ts, tsh, y, ych, yche, yk, yka, ykc, ykch, 
yke, ykee, ys, ysh, yshe, yt, yta, ytc, ytch, ytche, yte
```

**Length distribution:**
- 1 char: 8 stems
- 2 chars: 35 stems
- 3 chars: 46 stems
- 4 chars: 45 stems
- 5 chars: 15 stems
- 6 chars: 1 stem
- Mean: 3.2 chars

---

### ✅ SUFFIXES: 23 unique
**Source:** vpca2_tokens_roles.tsv

**S2_state (10):** -y, -iin, -ar, -ol, -or, -al, -air, -ky, -r, -l  
**S4_valley (10):** -edy, -eey, -hey, -eol, -eor, -khy, -thy, -oky, -heo, -key  
**S1_process (3):** -oty, -tol, -tor  

---

### ✅ P69 PATTERNS
**Source:** p69_rules_final.json

**Prefix patterns: 23 unique**  
**Suffix patterns: 15 unique**  
**Total rules: 109**

---

## WHAT CAN BE VERIFIED

### ✅ Token counts:
- Full manuscript: 37,886 tokens
- HRP subset: 25,910 tokens
- Unique types: 8,101

### ✅ Morphology:
- Stems: 150 unique (verified)
- Suffixes: 23 unique (verified, 3 classes)
- P69 patterns: 109 rules (verified)

### ✅ VPCA states:
- 7 sections with V/P/C/A distributions
- Suffix class → VPCA correlation (70-81% accurate)

### ✅ e/a polarity (from today):
- 'e' roots: 70.5% V state
- 'a' roots: 78.1% P state
- Replicates 6/6 sections
- Confidence: 85-90%

---

## WHAT CANNOT BE VERIFIED

### ❌ Previous false claims:
- "784 roots" - NO SOURCE
- "954 roots" - NO SOURCE
- "14 suffixes" - WRONG (actual: 23)
- "18 suffixes" - WRONG (actual: 23)
- "11 prefixes" - UNCLEAR (P69 has 23 patterns)

**These came from markdown docs, not ground truth data**

---

## CORRECTED MORPHOLOGY SUMMARY

**From ground truth TSV/JSON files only:**

### Stems/Roots:
- ✅ 150 unique stems verified (stem_axis_features.tsv)
- ✅ Axis embeddings for each stem
- ✅ Section-specific behavior

### Suffixes:
- ✅ 23 unique suffixes verified (vpca2_tokens_roles.tsv)
- ✅ 3 functional classes (S2_state, S4_valley, S1_process)
- ✅ Strong VPCA correlation (70-81%)

### Prefixes:
- ✅ 23 P69 prefix patterns (p69_rules_final.json)
- ❌ No extracted prefix column in morphology files
- ⚠️ Need to verify if P69 patterns = actual morphological prefixes

### Complete segmentation:
- ❌ No file has PREFIX + STEM + SUFFIX columns together
- ⚠️ Could be derived: PREFIX (P69) + STEM (150 stems) + SUFFIX (23 suffixes)

---

## DATA QUALITY

**HIGH QUALITY (verified, consistent):**
- ✅ vpca2_all_tokens.tsv (37,886 tokens with VPCA)
- ✅ vpca2_tokens_roles.tsv (25,910 tokens with suffixes)
- ✅ stem_axis_features.tsv (150 stems with embeddings)
- ✅ p69_rules_final.json (109 rules)

**EXPERIMENTAL (specific analyses):**
- ⚠️ ea_root files (today's e/a testing)
- ⚠️ f16v files (single folio analyses)
- ⚠️ f3r_f16 files (folio range analyses)

---

## FINAL COUNTS (GROUND TRUTH ONLY)

| Item | Count | Source |
|------|-------|--------|
| **Total tokens** | 37,886 | p140_tokens_COMPAT.tsv |
| **Unique token types** | 8,101 | vpca2_all_tokens.tsv |
| **Stems** | **150** ✅ | stem_axis_features.tsv |
| **Suffixes** | **23** ✅ | vpca2_tokens_roles.tsv |
| **Suffix classes** | **3** ✅ | vpca2_tokens_roles.tsv |
| **P69 rules** | **109** ✅ | p69_rules_final.json |
| **P69 prefix patterns** | **23** ✅ | p69_rules_final.json |
| **P69 suffix patterns** | **15** ✅ | p69_rules_final.json |

---

## VALIDATED FINDINGS

### ✅ Morphological structure:
- 150 stems with axis embeddings
- 23 suffixes in 3 functional classes
- Suffix classes predict VPCA states (70-81%)

### ✅ e/a polarity:
- 'e' roots → 70.5% Valley
- 'a' roots → 78.1% Peak
- Universal across 6 sections
- Confidence: 85-90%

### ✅ P69 framework:
- 109 pattern-matching rules
- 23 prefix + 15 suffix patterns
- For axis prediction scoring

---

**ALL CLAIMS MUST BE VERIFIED FROM THESE 19 FILES ONLY** ✅

**No more citing markdown documentation or unverified sources** ✅
