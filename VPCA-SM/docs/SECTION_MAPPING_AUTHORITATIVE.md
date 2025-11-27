# Voynich Manuscript Section Mapping - AUTHORITATIVE
**Source:** transliteration.txt (EVA transcription with $I section codes)  
**Date Verified:** November 27, 2025

---

## SECTION CODES ($I)

- **$I=H** - Herbal (plant illustrations with text)
- **$I=B** - Biological (circular diagrams with human figures)
- **$I=Z** - Zodiac (zodiac circle diagrams)
- **$I=S** - Stars/Recipes (⚠️ COVERS TWO DISTINCT SECTIONS - see below)
  - **ASTRONOMICAL** (f58r-f65r): Star diagrams with circular layout
  - **RECIPES** (f103r-f116v): Continuous procedural text
- **$I=P** - Pharmaceutical (jars and containers)
- **$I=C** - Cosmological (circular diagrams)
- **$I=A** - Astrological (zodiac-related)
- **$I=T** - Text (title pages, scattered text sections)

**CRITICAL NOTE:** The $I=S code is used for TWO completely different section types:
1. Diagram-based Astronomical pages (early)
2. Text-based Recipe pages (late)
These must be treated as separate sections for analysis.

---

## MAJOR SECTIONS (Continuous Ranges)

### HERBAL (Primary) - $I=H
**Range:** f1v - f57r  
**Count:** ~113 folios (majority of section)  
**Description:** Plant illustrations with descriptive text  
**Text Type:** Descriptive, possibly botanical/medical

### COSMOLOGICAL - $I=C
**Range:** f57v - f58r (transition section)  
**Count:** Small section  
**Description:** Circular diagrams

### ASTRONOMICAL - $I=S (Early)
**Range:** f58r - f65r  
**Count:** ~7 folios  
**Description:** Circular star diagrams with labels around circles  
**Text Type:** Diagram labels (similar to Zodiac/Biological)  
**Structure:** Diagram-based (NOT text-based)  
**Note:** Different from Recipes despite sharing $I=S code

### HERBAL (Scattered) - $I=H
**Range:** f65r - f66r, f66v - f67r1  
**Count:** Small sections  
**Description:** Continuation of herbal material

### ASTROLOGICAL/ZODIAC - $I=A, $I=Z
**Range:** f67r1 - f73v (mixed $I=A and $I=Z)  
**Count:** ~12 folios  
**Description:** Zodiac circles with symbols and text  
**Text Type:** Labels on zodiac diagrams

### BIOLOGICAL - $I=B  
**Range:** f75r - f84v (with brief interruptions at f76r, f85r1)  
**Count:** ~19 folios  
**Description:** Circular diagrams with human figures (often female)  
**Text Type:** Diagram labels, different structure than herbal

### COSMOLOGICAL (Late) - $I=C
**Range:** f85r2 - f86v6  
**Count:** Small section  
**Description:** Circular diagrams

### HERBAL (Late) - $I=H
**Range:** f87r - f88r  
**Count:** Small section

### PHARMACEUTICAL - $I=P
**Range:** f88r - f90r1, f99r - f102v  
**Count:** ~16 folios  
**Description:** Drawings of jars, containers, labeled

### RECIPES - $I=S (Late) ⭐
**Range:** f103r - f116v  
**Count:** ~14 folios (28 pages)  
**Description:** Dense continuous text, procedural/instructional  
**Text Type:** Text-based (similar to Herbal, NOT diagram-based)  
**Structure:** Continuous prose, procedural format  
**Note:** Different from Astronomical despite sharing $I=S code  
**Critical:** This is TEXT-BASED, not diagram-based

---

## HOLD-OUT DATA STATUS (For Validation Testing)

### Phase 1 (Training Data - Examined):
- ✅ Herbal A: f1v-f57r (~16,000 tokens)
- ✅ Zodiac: f67-f73 (~3,300 tokens)
- ✅ Pharmaceutical: f88-f102 (examined for some patterns)

### Phase 2 Hold-Out (Test Data):
- ✅ **Biological: f75r-f84v** (~8,800 tokens) - TESTED in Phase 2
- ✅ **Recipes: f103r-f116v** (~2,000+ tokens) - TESTED in TEST 3.1
- ⚠️ Herbal B: f58r-f66v (scattered, mixed with stars)
- ⚠️ Stars: f58r-f65r (~1,000 tokens) - could be hold-out

### Not Yet Used:
- Cosmological sections (f57v, f85r2-f86v6)
- Late Herbal (f87r-f88r)
- Stars (f58r-f65r)

---

## CRITICAL CORRECTIONS FROM TESTING

### ❌ ERROR: TEST 3.1 Initial Extraction
**What I did:** Tested f108-f116 (627 lines)  
**What was wrong:** Missed f103-f107 (458 lines)  
**Impact:** Underestimated by 42% of section

### ✅ CORRECTED: TEST 3.1 
**Correct range:** f103-f116 (1,085 lines)  
**Status:** Now accurately represents full Recipes section  
**Results:** Changed from 1/3 predictions to 2/3 predictions met

---

## SECTION SIZES (Approximate)

| Section | Folio Range | Token Count (est.) | Type | Status |
|---------|-------------|-------------------|------|--------|
| **Herbal A** | f1v-f57r | ~16,000 | Text | Phase 1 (used) |
| **Astronomical** | f58r-f65r | ~1,000 | Diagram | Hold-out (unused) ⭐ |
| **Herbal B** | f65r-f66v | ~500 | Text | Scattered (mixed) |
| **Zodiac** | f67-f73 | ~3,300 | Diagram | Phase 1 (used) |
| **Biological** | f75r-f84v | ~8,800 | Diagram | Phase 2 (tested) ✅ |
| **Herbal C** | f87r-f88r | ~300 | Text | Hold-out (unused) |
| **Pharmaceutical** | f88r-f102v | ~3,700 | Labels | Phase 1 (used) |
| **Recipes** | f103r-f116v | ~2,100 | Text | Phase 2 (tested) ✅ |

**Total manuscript:** ~36,000 tokens  
**Phase 1 (examined):** ~23,000 tokens (64%)  
**Phase 2 (hold-out tested):** ~10,900 tokens (30%)  
**Unused:** ~2,100 tokens (6%) - Astronomical + scattered sections

**CRITICAL DISTINCTION:**
- **Diagram-based:** Astronomical, Zodiac, Biological (lower medial %, ~72-73%)
- **Text-based:** Herbal, Recipes (higher medial %, ~87-92%)
- **Labels:** Pharmaceutical (intermediate)

---

## FOLIO NUMBERING NOTES

- Some folios have multiple subdivisions (e.g., f67r1, f67r2)
- Some folios are missing from the physical manuscript
- Recto (r) = front of page, Verso (v) = back of page
- File uses standard EVA (Extended Voynich Alphabet) transcription

---

## SECTION CHARACTERISTICS

### Text-Based Sections:
- **Herbal** (f1v-f57r): Descriptive text with plant illustrations
- **Recipes** (f103r-f116v): Continuous procedural text
- **Pharmaceutical** (f88r-f102v): Labels on containers

**Characteristics:** Longer labels, continuous text flow, higher word variety

### Diagram-Based Sections:
- **Astronomical** (f58r-f65r): Star diagrams with circular labels ⭐
- **Biological** (f75r-f84v): Circular diagrams with labels
- **Zodiac** (f67-f73): Zodiac circles with symbol labels

**Characteristics:** Shorter labels, repetitive structure, more formulaic

### CRITICAL: Why Astronomical ≠ Recipes

**Despite sharing $I=S code, these are COMPLETELY DIFFERENT:**

| Aspect | Astronomical (f58-f65) | Recipes (f103-f116) |
|--------|------------------------|---------------------|
| **Structure** | Circular diagrams | Continuous text |
| **Label type** | Short, around circles | Long, procedural |
| **Similar to** | Zodiac, Biological | Herbal |
| **Expected 'e' medial %** | ~72-73% (diagram) | ~87-92% (text) |
| **Text density** | Low (41 lines/folio) | High (54 lines/folio) |

**This distinction is critical for validation testing because:**
- Diagram sections and text sections have different linguistic properties
- Lumping them together masks important patterns
- Astronomical is an unused hold-out that could validate diagram patterns

---

## VALIDATION IMPLICATIONS

### Why Section Type Matters:

1. **Position patterns vary:**
   - Text-based: Higher medial % (88-92%)
   - Diagram-based: Lower medial % (73%)

2. **Frequency patterns vary:**
   - Recipes: High 'e' frequency (41%)
   - Biological: Standard frequency (~30%)
   - Herbal: Standard frequency (~30%)

3. **Text structure differs:**
   - Continuous text vs labels
   - Procedural vs descriptive
   - Different grammatical contexts

### Testing Strategy:

- **Primary hold-out:** Text-based sections (Recipes ✅)
- **Secondary hold-out:** Diagram-based sections (Biological ✅)
- **Compare:** Text vs diagram behavior
- **Remaining:** Stars (unused), Cosmological (unused)

---

## AUTHORITATIVE BASELINE ESTABLISHED

**Source file:** `/home/claude/transliteration.txt`  
**Section codes:** Embedded in folio metadata ($I=X)  
**Verification:** Manual inspection of transitions  
**Status:** ✅ **VERIFIED AND DOCUMENTED**

**All future extraction will reference this document.**

---

**Last updated:** November 27, 2025  
**Verified by:** Error correction process  
**Status:** Authoritative baseline ✅
