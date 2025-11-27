# VPCA-SM: Semantic Decipherment Pipeline

**VPCA Semantic Mapping** - Systematic semantic analysis building on proven morphological structure.

---

## 🎯 Overview

This pipeline moves from **structural morphology** (proven χ²=464, p<10⁻¹⁰³) to **semantic decipherment** through controlled, testable hypotheses.

**Key Principle:** 
> We describe what VPCA states **DO** functionally, not what tokens **MEAN** lexically.

**NOT lexical translation** (phonetic/word-for-word)  
**BUT semantic reconstruction** (role-based/structural)

---

## 📊 Modules

### SM1: VPCA → Role Semantics ✅ COMPLETE
**File:** `vpca_sm1_role_semantics.py`

Maps VPCA morphological states (V/P/C/A) to functional roles per section.

**Input:**
- `data/vpca2_all_tokens.tsv` - Complete VPCA classifications (37,886 tokens)
- `data/vpca2_full_section_summary.tsv` - Section distributions
- `data/ea_root_vpca_summary.tsv` - Root polarity (e vs a)
- `data/f16v_vpca2_by_colour.tsv` - Zodiac seasonal data

**Output:**
- `results/sm1_vpca_role_map.json` - VPCA state → role mapping
- `results/sm1_role_descriptions.txt` - Human-readable descriptions

**Confidence Tiers:**
- **Tier 1:** Structural only (morphology proven, no semantic claim)
- **Tier 2:** Structural + domain (context-specific role behavior)
- **Tier 3:** Structural + domain + semantic (testable hypothesis, e.g., Zodiac)

**Example Output:**
```
Zodiac V-state: "winter/low-energy phase marker" (Tier 3, χ²=69, p<10⁻¹⁶)
Herbal V-state: "base/dormant state descriptor" (Tier 2)
```

**Run:**
```bash
python3 vpca_sm1_role_semantics.py
cat results/sm1_role_descriptions.txt
```

---

### SM2: Root & Affix Role Classes ❌ INVALID - SEE CORRECTION
**File:** `vpca_sm2_role_classes.py`
**Status:** **METHODOLOGY FLAW DISCOVERED** - See CRITICAL_METHODOLOGY_ERROR.md

**CRITICAL ISSUE:**
- Morpheme extraction does NOT conform to p69 validated rules
- Ad-hoc extraction created invalid "root" and "suffix" classifications
- Claims about R1/R2/R3 and S1/S2/S3 are NOT validated

**What IS Valid:**
- OT-containing tokens show 85-100% C-state (lexical pattern)
- VPCA distributions by section (based on p69)
- Statistical tests remain significant

**What is INVALID:**
- Morpheme-level classifications (roots, suffixes, prefixes)
- Claims about "OT-family suffixes" (not validated by p69)
- All SM2 classification schemes (R1/R2/R3, S1/S2/S3, P1/P2/P3)

**Needs:**
- Complete rebuild using p69 patterns directly (SM2b)
- Or: Abandon morpheme claims, use lexical grouping only

**See:** `CRITICAL_METHODOLOGY_ERROR.md` for full analysis

---

### SM3: Section-Specific Role Frames ✅ COMPLETE
**File:** `vpca_sm3_frame_templates.py`

Build semantic frame templates per section through sequence analysis.

**Input:**
- `data/vpca2_all_tokens.tsv` - Complete VPCA with sequences
- `results/sm1_vpca_role_map.json` - VPCA role mappings
- `results/sm2_role_lexicon.json` - Morpheme classifications

**Output:**
- `results/sm3_frame_patterns.json` - Frame templates per section
- `results/sm3_sequence_analysis.txt` - Sequence pattern analysis
- `results/sm3_bigram_transitions.tsv` - VPCA state transitions (32,679 total)

**Key Findings:**
- **V→C progression:** Ingredient→process pattern in Recipes/Pharma
- **P→P dominance:** 10,331 transitions (neutral state persists)
- **Section templates:** Each section shows distinct structural patterns
  - Zodiac: 53.7% single tokens (labels)
  - Biological: 33.7% descriptive (V-heavy)
  - Recipes: Higher C-state concentration

**Pattern Example:**
```
Recipe V→C: [ingredient tokens] → [OT-family suffix] → [result]
Herbal Descriptive: [V-heavy sequence] (ingredient lists)
```

**Run:**
```bash
python3 vpca_sm3_frame_templates.py
cat results/sm3_sequence_analysis.txt
```

---

### SM4: Proto-Glosses (Controlled) 🔜 PLANNED
**File:** `vpca_sm4_proto_glosses.py`

Limited proto-glosses with strict evidence requirements.

**Rules:**
- Only for extremely clear roles
- Only in constrained contexts
- With confidence tiers
- Full evidence documentation

**Example:**
```
OT-family: [TRANSFORMATION] (Tier 1: structural)
'e' in Zodiac: [WINTER/COLD] (Tier 2: structural+domain)
```

---

### SM5: Cross-Section Consistency 🔜 PLANNED
**File:** `vpca_sm5_consistency.py`

Test where proto-glosses break across sections.

---

### SM6: External Parallels 🔜 PLANNED
**File:** `vpca_sm6_external_parallels.py`

Compare role frames to medieval texts (structural patterns, not vocabulary).

---

## 🔬 Methodology

### What We CAN Claim:
✅ VPCA states map to functional roles  
✅ Roles vary by section (context-specific)  
✅ e/a roots show systematic polarity  
✅ Zodiac shows seasonal pattern (χ²=69, p<10⁻¹⁶)  
✅ Morphological structure is real (χ²=464, p<10⁻¹⁰³)  

### What We DON'T Claim:
❌ Specific word meanings ("daiin" = "water")  
❌ Phonetic values (how to pronounce)  
❌ Complete translation  
❌ Universal semantic mappings  

---

## 📈 Current Status

**Phase:** SM1 ✅ SM2 ❌ SM3 ✅ (1.5/3 valid modules)  
**CRITICAL:** SM2 methodology flaw discovered - see CRITICAL_METHODOLOGY_ERROR.md  
**Data:** 37,886 tokens with complete VPCA classifications  
**Sections:** 7 (Zodiac, Herbal, Pharma, Recipes, Bio, Cosmo, Unknown)  
**Transitions Analyzed:** 32,679 VPCA state transitions  
**Verified Finding:** OT-containing tokens = 85-100% C-state (lexical pattern, not morphological claim)  
**Invalidated:** SM2 morpheme classifications (not p69-conformant)  
**Confidence:** Tier 2-3 for Zodiac (SM1), Tier 1-2 for others, SM2 RETRACTED  

---

## 🎯 How This Differs from Past Attempts

**Past Attempts (Failed):**
- Started with semantic assumptions
- No statistical validation
- Global semantic mappings
- Cherry-picked evidence
- Claimed definitive meanings

**This Attempt (VPCA-SM):**
- Starts with proven morphology (p<10⁻¹⁰³)
- Statistical validation first
- Context-specific semantics
- Report negative results
- Claims limited to evidence
- Confidence tiers explicit

**This is Era 1 of semantic structural reconstruction, not Era 8 of the same mistakes.**

---

## 🚀 Running the Pipeline

```bash
# SM1: Role Semantics
python3 vpca_sm1_role_semantics.py

# View results
cat results/sm1_role_descriptions.txt
cat results/sm1_vpca_role_map.json

# (SM2, SM3, etc. coming soon)
```

---

## 📝 Citation

This work builds on:
- **Morphological Analysis:** p69 rulebook (109 rules, 79% coverage)
- **State System:** VPCA-2 classification
- **Statistical Validation:** χ²=464, p<10⁻¹⁰³ (manuscript-wide)
- **Zodiac Enhancement:** χ²=69, p<10⁻¹⁶ (seasonal mapping)

**Key Insight:** Voynichese is a templatic/compressed technical register, not phonetic alphabetic encoding.

---

## ⚠️ Important Notes

1. **This is NOT translation** - It's structural-semantic decipherment
2. **Roles ≠ Meanings** - We describe function, not content
3. **Context-specific** - Same VPCA state = different roles per section
4. **Conservative** - Claims match evidence only
5. **Falsifiable** - Every hypothesis is testable

---

**Last Updated:** 2024-11-27  
**Status:** SM1 Complete, SM2-8 In Development  
**Branch:** VPCA-SM  
