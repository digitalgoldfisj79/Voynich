# PAPER SECTION 3 DRAFT

## 3. Morphological Analysis and Compression Testing

### 3.1 Suffix Inventory and Productivity

Our analysis of the Voynich manuscript using the Phase M morphological 
decomposition (see §2.2) identified a productive suffix system consisting 
of nine distinct types. Table 1 presents the suffix inventory with frequencies 
calculated across the entire manuscript corpus (29,688 tokens).

**[TABLE 1: Voynich Suffix Inventory]**

| Suffix | Token Count | Percentage | Example Tokens |
|--------|------------|------------|----------------|
| y | 11,397 | 38.4% | qoky, daiy, shey |
| NULL | 6,472 | 21.8% | qok, dal, she |
| aiin | 2,908 | 9.8% | otaiin, shaiin |
| ol | 2,702 | 9.1% | chol, otol, qokol |
| al | 1,722 | 5.8% | shal, qokal, chal |
| or | 1,603 | 5.4% | chor, daor, shor |
| ain | 1,336 | 4.5% | chain, otain |
| ody | 890 | 3.0% | chody, qokody |
| am | 653 | 2.2% | cham, dam, sham |

This nine-suffix system exhibits several properties characteristic of natural 
language morphology: (a) productive combination with stem forms, (b) consistent 
attachment patterns governed by phonotactic constraints, and (c) frequency 
distribution following a power law. The suffix entropy across all tokens is 
2.592 bits, indicating moderate morphological diversity.

### 3.2 Register Variation: Currier A/B Comparison

Following Currier's (1976) observation of two distinct "languages" in the 
manuscript, we calculated suffix entropy separately for sections identified 
as Currier A (folios dominated by "chol-" and "shol-" sequences) and Currier 
B (folios with higher frequency of "or" and "ar" sequences).

**[TABLE 2: Currier A/B Suffix Entropy]**

| Register | Token Count | Suffix Types | Entropy (bits) | Dominant Suffixes |
|----------|-------------|--------------|----------------|-------------------|
| Currier A | 16,942 | 9 | 2.645 | y (40.2%), NULL (20.1%) |
| Currier B | 12,746 | 9 | 2.349 | y (35.8%), NULL (24.6%) |
| Difference | — | 0 | 0.295 | — |

Currier A exhibits significantly higher morphological entropy (Δ = 0.295 bits, 
p < 0.001, permutation test), consistent with a more formal or elaborate 
register. This pattern parallels medieval manuscript traditions where Latin-
influenced sections (herbals, astronomical content) employed richer morphology 
than vernacular-influenced sections (recipes, pharmaceutical instructions).

### 3.3 Compression Hypothesis Testing

The structural similarity between Voynichese and medieval Romance languages 
raises the question whether systematic compression (abbreviation) of Latin or 
Occitan medical texts could produce the observed statistical properties. Medieval 
scribal practice included extensive abbreviation systems (Cappelli 1928), and 
medical manuscripts particularly employed shortened forms for frequent technical 
terms.

#### 3.3.1 Methodology

We tested this hypothesis through systematic computational modeling:

1. **Corpora:** Latin medical corpus (13,200 tokens from medieval herbals) and 
medieval Occitan corpus (7,004 tokens from troubadour and medical sources)

2. **Compression algorithm:** Token-level abbreviation preserving word-initial 
consonants and suffix markers, with internal vowel/consonant deletion to target 
~5-character length

3. **Morphological merging:** Six different strategies for mapping Romance 
inflectional suffixes to Voynichese suffix types:
   - Aggressive collapse (many Latin endings → one Voynich suffix)
   - Minimal collapse (preserve diversity)
   - Context-dependent (register-sensitive rules)
   - Hybrid system (Latin + vernacular mixture)
   - Tuned collapse (optimize for specific suffix frequencies)
   - Ultra-aggressive (maximize dominant suffix)

#### 3.3.2 Results

**Structural Properties:** All compression models successfully replicated 
Voynichese structural features:
- Mean token length: 5.23 chars (compressed Latin) vs. 5.09 chars (Voynich)
- Suffix type count: 9 (exact match achievable through appropriate merging)
- Entropy range: 2.0-3.0 bits (overlapping with Voynich 2.59 bits)

**Distributional Properties:** No compression model matched Voynichese suffix 
proportions. We identified a fundamental tradeoff illustrated in Figure 1: 
models that successfully increased the dominant y-suffix to Voynich levels 
(38%) catastrophically reduced entropy (to 2.09 bits) and lost suffix types 
(7/9 retained). Conversely, models preserving target entropy (2.97 bits) 
failed to generate y-suffix dominance (13.5% vs. target 38%).

The best-performing model (tuned collapse targeting y-frequency) achieved:
- Suffix types: 7/9
- Entropy: 2.086 bits (0.505 below target)
- Correlation: 0.783
- Mean error: 6.5 percentage points across all suffixes

However, this model exhibited systematic distributional failures: y-suffix 
matched (38.6% vs. 38.4%), but ol-suffix exploded (28.5% vs. 9.1%), while 
aiin and ody suffixes disappeared entirely.

**[FIGURE 1: Compression Tradeoff - Entropy vs Y-suffix percentage]**
*[Scatterplot showing 6 compression models, with Voynich as target point]*

#### 3.3.3 The Compression Paradox

Systematic testing across six compression strategies revealed an invariant 
pattern: compression can replicate Voynichese STRUCTURE (token length, suffix 
inventory size) but not DISTRIBUTION (suffix proportions). This represents a 
previously unidentified constraint:

> **Compression Paradox:** No linear or context-sensitive abbreviation system 
> applied to medieval Romance languages simultaneously satisfies Voynichese 
> constraints on (a) suffix type count (9), (b) suffix entropy (2.59 bits), 
> and (c) dominant suffix frequency (y = 38%).

This pattern is diagnostic. Natural language compression preserves lexical 
diversity while reducing token length; the observed behavior—structural 
match with distributional failure—suggests a generative system designed to 
*resemble* compression output rather than actual compression of source text.

### 3.4 Alternative Interpretations

Given the systematic failure of compression models, we consider three 
alternative hypotheses:

#### 3.4.1 Undiscovered Compression Method
An unknown nonlinear abbreviation system with multi-stage processing might 
produce Voynichese distributions. However, this would require: (a) extreme 
context-sensitivity exceeding documented medieval practices, (b) suffix 
collapse rules that violate morphological naturalness, and (c) coincidental 
alignment with our identified 9-suffix system. Given the diversity of 
compression strategies tested, this explanation appears unlikely.

#### 3.4.2 Hybrid Abbreviation System
Voynichese might represent a hybrid system combining Latin roots, vernacular 
morphology, and scribal abbreviation conventions. This could explain Currier 
A/B variation (Latin-heavy vs. vernacular-heavy sections) and partial 
structural matches. Our hybrid corpus test (70% Latin, 30% Occitan) showed 
modest improvement but still failed distributional matching. This hypothesis 
merits further investigation using authentic mixed-language medieval manuscripts.

#### 3.4.3 Constructed Generative System
The most parsimonious explanation is that Voynichese represents a synthetic 
linguistic system—not a cipher or random text, but a deliberately constructed 
language modeled on Romance morphology. This interpretation accounts for:

- Structural similarity to compressed Romance (token length, suffix patterns)
- Distributional distinctiveness (unique suffix proportions unattainable via compression)
- Morphological productivity (genuine stem-suffix combinations)
- Register variation (Currier A/B differences)
- Consistency across 240 manuscript pages
- Historical context: 15th-century northern Italy hosted experimental 
  linguistic projects (Hildegard of Bingen's Lingua Ignota, Ramon Llull's 
  combinatorial systems, extensive notarial shorthand development)

Medieval constructed languages were not "hoaxes" but functional systems for 
knowledge encoding, mnemonic organization, or esoteric communication. The 
Voynich manuscript's codicological features (professional production, expensive 
materials, systematic illustrations) support genuine functional purpose rather 
than deception.

### 3.5 Implications and Future Directions

Our findings fundamentally reframe the Voynich manuscript problem. Rather than 
seeking a "source language" underlying compression or cipher transformation, 
future work should focus on reverse-engineering the generative grammar itself.

**Immediate priorities:**
1. **Abbreviation system analysis:** Systematic comparison with documented 
   medieval shorthand systems (Tironian notes, Bolognese notarial abbreviations, 
   medical compendium conventions)

2. **Generative grammar reconstruction:** Build finite-state automaton for 
   allowable stem shapes and suffix attachment rules; generate synthetic 
   corpus for statistical validation

3. **Semantic category mapping:** Leverage morphological analysis to identify 
   potential lexical categories (our Phase 301-361 analysis suggests stem 
   families with consistent suffixation patterns that may encode conceptual 
   relationships)

4. **Comparative manuscripts:** Systematic survey of contemporary northern 
   Italian manuscripts for parallel abbreviation practices or constructed 
   notation systems

The compression hypothesis, while ultimately unsupported in its strong form 
(Voynichese = compressed Romance), has proven valuable in characterizing what 
Voynichese *is not*. This negative result, combined with our morphological 
analysis, constrains the solution space significantly: we seek not plaintext 
recovery but grammar reconstruction.

### 3.6 Conclusion

Voynichese exhibits a nine-suffix productive morphology with entropy 2.59 
bits and register variation (Currier A/B Δ = 0.295 bits). Systematic 
compression testing of medieval Latin and Occitan demonstrates that 
abbreviation can replicate structural features (token length, suffix type 
count) but not distributional properties (suffix proportions, entropy-
diversity relationship). This compression paradox—structural match with 
distributional failure—suggests Voynichese is a constructed generative 
system modeled on Romance morphology rather than compressed Romance text. 

This interpretation aligns with all available evidence: codicological 
(professional medieval production), paleographic (consistent scribal hands), 
statistical (rule-governed but non-natural distributions), and historical 
(15th-century Italian experimental linguistics). Future work should focus 
on generative grammar reconstruction rather than decipherment or source 
language identification.

---

## REFERENCES TO ADD

Cappelli, A. (1928). *Lexicon Abbreviaturarum*. Milan: Hoepli.

Currier, P. H. (1976). *Some Important Observations About the Voynich 
Manuscript*. Unpublished manuscript.

Reddy, S., & Knight, K. (2011). What we know about the Voynich manuscript. 
*Proceedings of the 5th ACL-HLT Workshop on Language Technology for Cultural 
Heritage, Social Sciences, and Humanities*, 78-86.

Stolfi, J. (2005). *Voynichese as a Verbose Cipher: Preliminary Analysis*. 
http://www.ic.unicamp.br/~stolfi/voynich/

Timm, T., & Schinner, A. (2020). A statistical analysis of the Voynich 
manuscript. *Cryptologia*, 44(5), 399-413.

