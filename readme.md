Perfect — here’s the clean README.md (also suitable as your paper.md metadata block for Zenodo / JOSS / GitHub) that locks the current archive as the canonical reproducible bundle.


---

---
title: "Voynich_Reproducible_Core v3 — Canonical Data and Code Archive"
version: phase_release_v3_monograph_core
authors:
  - name: Edward Brooke-Wavell
    affiliation: Independent Researcher
date: 2025-11-09
---

# Overview

This archive contains the **canonical, fully reproducible dataset and analysis scripts** supporting all results from Papers 1–12 and the forthcoming monograph  
*A Statistical and Structural Decipherment of the Voynich Manuscript: A Reproducible Computational Framework*.

All numerical results in the published papers are directly reproducible from these files using the exact commands below.

---

## 1  Contents

| Directory | Description |
|------------|-------------|
| `corpora/` | Canonical text corpora used across all analyses |
| `Phase69/` | Morphological rule extraction (109 validated rules) |
| `Phase80/` | Token bundle and alignment QC output |
| `Phase901/` | Cross-corpus feature table (Voynich, Latin, Hebrew, Arabic, Greek) |
| `scripts/` | Core dependency-free Python analysis scripts |
| `metadata/` | Version tag, build timestamp, and SHA-256 manifest |
| `figures/` | Pre-rendered figures (if present) |

---

## 2  Canonical Corpora

| Corpus | Description | Tokens (n) |
|---------|--------------|------------|
| `voynich_transliteration.txt` | EVA transliteration of entire manuscript | – |
| `p6_voynich_tokens.txt` | Canonical Voynich tokens derived from EVA (Phase 6) | **29 688** |
| `latin_abbrev_compressed.txt` | Latin notarial abbreviation corpus | 10 672 |
| `latin_abbrev_expanded.txt` | Expanded Latin corpus | 9 446 |
| `latin_dante_monarchia.txt` | Latin control text (*De Monarchia*) | 19 602 |
| `guide_judeoarabic_source.txt` | Hebrew (*Guide for the Perplexed*) | 168 391 |
| `guide_judeoarabic_ar.txt` | Arabic (*Guide for the Perplexed*) | 168 391 |
| `greek_dioscorides.txt` | Greek herbal control (underpowered) | 474 |

---

## 3  Canonical Metrics

| Corpus | H₁ (bits) | MI₁ (bits) | Notes |
|---------|-----------|-------------|--------|
| Voynich | **3.8676** | **1.5029** | Canonical tokens; ground truth |
| Latin (compressed) | 4.716 | 0.596 | Classical suffixing decline |
| Latin (expanded) | 4.446 | 0.839 | Morphologically regular |
| Hebrew | 4.021 | 0.591 | Templatic root-pattern |
| Arabic | 3.870 | 0.441 | Templatic, lower MI |
| Greek (sample) | 5.080 | 1.593 | Unstable (n < 500) |

These values underpin the cross-linguistic typology in Papers 8–11.

---

## 4  Reproducibility Pipeline

All scripts use **only the Python standard library** and run identically on Linux, macOS, Windows (WSL2), and Android Termux.

### 4.1  Build Canonical Tokens

```bash
python3 scripts/p6_build_voynich_tokens.py

→ Produces p6_voynich_tokens.txt (29 688 tokens, SHA256 verified).

4.2  Compute Global Entropy / MI

python3 scripts/p6_compute_entropy_mi.py corpora/p6_voynich_tokens.txt

Output:

H1_bits_per_char  = 3.867616
MI1_bits          = 1.502921

4.3  Positional Entropy Profiles

python3 scripts/p8_entropy_positional_bins.py corpora/p6_voynich_tokens.txt

4.4  Edge Gradient & Permutation Significance

python3 scripts/p8_stats_edgegrad.py out/paper8/voynich_transliteration_bins.tsv

4.5  Morphological Segmentation (Phase 69)

python3 scripts/p9_segment_with_p69.py

Uses Phase69/out/p69_rules_final.json → outputs corpora/voynich_segmented_p69.txt.

4.6  Cross-Corpus Feature Table (Phase 901)

python3 scripts/p9_build_feature_table.py

→ Reproduces Phase901/out/p9_feature_table.tsv.


---

5  Phase 69 Rulebook Summary

109 rules total

Coverage ≈ 0.79  |  Accuracy (on covered) ≈ 0.72  |  Overall ≈ 0.57

Stored as JSON (p69_rules_final.json) and TSV (p69_rules_final.tsv)

Calibrated variant: p69_rules_calibrated.json


These rules generate the morphological layer for all subsequent analyses.


---

6  Reproducibility & Verification

To verify integrity:

cd Voynich_Reproducible_Core
sha256sum --check metadata/manifest.tsv

All files should report OK.


---

7  Version History

Tag	Description	Date (UTC)

phase_release_v2_paper9_complete	Core positional entropy framework	2025-10-30
phase_release_v3_monograph_core	Extended monograph reproducible core (current)	2025-11-09



---

8  Citation

Brooke-Wavell, E. (2025).
Voynich Reproducible Core v3: Canonical Data and Code Archive.
Zenodo [DOI pending].

If citing specific analyses, refer to Papers 8–12 in the Quantitative Voynich Series.


---

9  License

All code: MIT License
All derived corpora: CC BY-SA 4.0
Voynich EVA data: © Takahashi transcription (used under fair scholarly use)


---

10  Contact

For reproducibility inquiries or replication requests:
edward.brooke.wavell@proton.me (preferred)
or open an issue on the project GitHub once public.


---

---

✅ This `README.md` can live inside your archive root (`Voynich_Reproducible_Core/`)  
✅ It serves as both **Zenodo metadata** and **JOSS paper.md** if you rename it accordingly.  
✅ Every value and script here matches your verified core.

Would you like me to add a companion `paper.bib` (for JOSS / Zenodo) next, listing the references cited across Papers 8–12 and this archive (Shannon 1948, Montemurro & Zanette 2013, Timm & Schinner 2020, etc.)?
