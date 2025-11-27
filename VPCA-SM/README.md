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

### SM2: Root & Affix Role Classes ✅ COMPLETE
**File:** `vpca_sm2_role_classes.py`

Classify stems and suffixes into semantic role families.

**Input:**
- `data/vpca2_all_tokens.tsv` - Complete VPCA classifications
- Morpheme extraction algorithm

**Output:**
- `results/sm2_role_lexicon.json` - Complete role lexicon
- `results/sm2_classification_report.txt` - Classification report
- `results/sm2_root_classes.tsv` - Root classifications (2,734 roots)
- `results/sm2_affix_classes.tsv` - Affix classifications (52 affixes)

**Classifications:**
- **R1:** 100 ingredient-like roots (V-heavy, e.g., 'e', 'k', 'ch')
- **R2:** 4 process-like roots (C-heavy, e.g., 'ot', 'q')  
- **R3:** 111 state-like roots (P-heavy, e.g., 'a', 'o', 'ok')
- **S1:** 5 OT-family suffixes (100% C-state transformation markers!)
- **P1:** 5 Valley-inducing prefixes (e.g., 'ch', 'qok', left-biased)

**Key Finding:** OT-family suffixes show 100% C-state association (oty, otchy, otol, etc.)

**Run:**
```bash
python3 vpca_sm2_role_classes.py
cat results/sm2_classification_report.txt
```

---

### SM3: Section-Specific Role Frames 🔜 PLANNED
**File:** `vpca_sm3_role_frames.py`

Build semantic frame templates per section.

**Goal:** Identify structural patterns:
- Herbal: `[BASE] + [PROCESS] + [PEAK]`
- Recipe: `[INGREDIENTS] + [C-SEQUENCE] + [RESULT]`
- Zodiac: `[V] → [C] → [A]` cycle

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

**Phase:** SM1-SM2 Complete, SM3 In Development  
**Data:** 37,886 tokens with complete VPCA classifications  
**Sections:** 7 (Zodiac, Herbal, Pharma, Recipes, Bio, Cosmo, Unknown)  
**Morphemes Classified:** 2,734 roots + 52 affixes  
**Key Discovery:** OT-family suffixes = 100% C-state (transformation markers)  
**Confidence:** Tier 2-3 for Zodiac, Tier 1-2 for others  

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
