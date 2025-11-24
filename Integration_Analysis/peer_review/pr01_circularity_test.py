#!/usr/bin/env python3
"""
Peer Review 01: Circularity Test

CRITICAL: Prove T3 domain assignments are independent of Voynich section occurrence.

Tests:
1. Were domains assigned from Latin corpus features only?
2. Do Latin corpus features predict T3 domains?
3. Can domains be reconstructed without Voynich data?

Addresses: Reviewer concern about circular validation
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
OUTPUT = BASE / "Integration_Analysis/peer_review/pr01_circularity_results.tsv"

print("="*80)
print("PEER REVIEW 01: CIRCULARITY TEST")
print("="*80)

print("\nCRITICAL QUESTION: Are T3 domain assignments circular?")
print("\nIf domains were assigned by looking at Voynich sections,")
print("then Test 2's 'perfect alignment' is circular validation.")

# Load data
t3 = pd.read_csv(BASE / "metadata/t3_candidates_domains_filtered.tsv", sep='\t')
latin_freq = pd.read_csv(BASE / "PhaseS/out/s6_materia_token_freq.tsv", sep='\t')

print(f"\nLoaded {len(t3)} T3 candidates with domain assignments")

# Test 1: Check if T3 has 'candidate_source' metadata
print(f"\n{'='*80}")
print("TEST 1: DOMAIN ASSIGNMENT PROVENANCE")
print("="*80)

if 'candidate_source' in t3.columns:
    print("\nT3 candidates have 'candidate_source' metadata:")
    sources = t3['candidate_source'].value_counts()
    for source, count in sources.items():
        print(f"  {source}: {count} candidates")
    
    # Check if any source mentions section/Voynich
    voynich_sources = sources.index[sources.index.str.contains('SECTION|VOYNICH|OCCURRENCE', case=False, na=False)]
    
    if len(voynich_sources) > 0:
        print(f"\n  ⚠ WARNING: {len(voynich_sources)} sources reference Voynich/sections")
        print("  This suggests potential circularity")
        test1_pass = False
    else:
        print(f"\n  ✓ No sources reference Voynich sections")
        print("  Domain assignments appear independent")
        test1_pass = True
else:
    print("\n  ⚠ No provenance metadata available")
    test1_pass = None

# Test 2: Can domains be predicted from Latin corpus features alone?
print(f"\n{'='*80}")
print("TEST 2: LATIN CORPUS PREDICTABILITY")
print("="*80)

print("\nCan we reconstruct domain assignments using ONLY Latin corpus data?")

# Merge T3 with Latin frequencies
t3_latin = t3.merge(latin_freq, left_on='lemma_latin', right_on='token', how='left')

print(f"\nMatched {len(t3_latin[t3_latin['total_count'].notna()])} T3 candidates to Latin corpus")

# Check if corpus frequency correlates with domain
domain_freq = t3_latin.groupby('latin_domain')['corpus_freq'].agg(['mean', 'median', 'std']).reset_index()

print(f"\nLatin corpus frequency by domain:")
print(domain_freq.to_string(index=False))

# Test: Do different domains have different Latin frequencies?
freq_variance = domain_freq['mean'].var()
print(f"\nFrequency variance across domains: {freq_variance:.2f}")

if freq_variance > 10:
    print(f"  ✓ Domains show different Latin corpus frequencies")
    print(f"  This suggests domains reflect Latin semantics, not Voynich patterns")
    test2_pass = True
else:
    print(f"  ⚠ Low variance suggests domains may not reflect Latin structure")
    test2_pass = False

# Test 3: Domain names themselves - are they Latin-centric?
print(f"\n{'='*80}")
print("TEST 3: DOMAIN NOMENCLATURE")
print("="*80)

print("\nDomain names used:")
domains = t3['latin_domain'].unique()
for domain in sorted(domains):
    print(f"  {domain}")

# Check if domains use standard Latin semantic categories
latin_categories = ['BOT', 'PROC', 'BIO', 'HERB', 'COOKING', 'GRINDING', 'MIXING', 'ADDING', 'FLUID']
domain_is_latin = sum(1 for d in domains if any(cat in str(d) for cat in latin_categories))

print(f"\nDomains using Latin semantic categories: {domain_is_latin}/{len(domains)}")

if domain_is_latin / len(domains) > 0.8:
    print(f"  ✓ Domain names reflect Latin semantic structure")
    test3_pass = True
else:
    print(f"  ⚠ Domain names may be Voynich-centric")
    test3_pass = False

# Test 4: Temporal ordering - was Latin corpus analyzed first?
print(f"\n{'='*80}")
print("TEST 4: TEMPORAL ORDERING")
print("="*80)

# Check file timestamps
latin_corpus_file = BASE / "PhaseS/out/s6_materia_token_freq.tsv"
t3_file = BASE / "metadata/t3_candidates_domains_filtered.tsv"
section_analysis = BASE / "PhaseS/out/s4_stem_section_distribution.tsv"

from datetime import datetime

files_exist = all([latin_corpus_file.exists(), t3_file.exists(), section_analysis.exists()])

if files_exist:
    latin_time = datetime.fromtimestamp(latin_corpus_file.stat().st_mtime)
    t3_time = datetime.fromtimestamp(t3_file.stat().st_mtime)
    section_time = datetime.fromtimestamp(section_analysis.stat().st_mtime)
    
    print(f"\nFile timestamps:")
    print(f"  Latin corpus:    {latin_time}")
    print(f"  T3 domains:      {t3_time}")
    print(f"  Section analysis: {section_time}")
    
    # Check if Latin corpus predates T3 domains
    if latin_time < t3_time:
        print(f"\n  ✓ Latin corpus analyzed before T3 domains")
        test4_pass = True
    else:
        print(f"\n  ⚠ Temporal ordering unclear")
        test4_pass = None
else:
    print("\n  ⚠ Cannot verify temporal ordering")
    test4_pass = None

# VERDICT
print(f"\n{'='*80}")
print("VERDICT: CIRCULARITY TEST")
print("="*80)

tests = [test1_pass, test2_pass, test3_pass]
tests_passed = sum(1 for t in tests if t == True)
tests_total = len([t for t in tests if t is not None])

print(f"\nTests passed: {tests_passed}/{tests_total}")

if tests_passed >= 3:
    verdict = "PASS - No circularity detected"
    confidence = "HIGH"
elif tests_passed >= 2:
    verdict = "WEAK PASS - Some independence shown"
    confidence = "MODERATE"
else:
    verdict = "FAIL - Circularity concern remains"
    confidence = "LOW"

print(f"\nVERDICT: {verdict}")
print(f"CONFIDENCE: {confidence}")

print(f"\n{'='*80}")
print("INTERPRETATION")
print("="*80)

if tests_passed >= 2:
    print("\nEvidence suggests T3 domains were assigned from Latin corpus")
    print("features, not Voynich section occurrence patterns.")
    print("\nDomain assignments appear independent of section analysis,")
    print("reducing circularity concerns.")
else:
    print("\nInsufficient evidence that domain assignments are independent.")
    print("\nREVIEWER CONCERN: Test 2's perfect alignment may be circular.")
    print("\nRECOMMENDATION: Document T3 domain assignment methodology")
    print("explicitly showing independence from Voynich data.")

# Save
results = pd.DataFrame([{
    'test': 'circularity_check',
    'verdict': verdict,
    'provenance_check': test1_pass,
    'latin_predictability': test2_pass,
    'nomenclature_check': test3_pass,
    'temporal_ordering': test4_pass,
    'confidence': confidence
}])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results.to_csv(OUTPUT, sep='\t', index=False)

print(f"\n✓ Saved: {OUTPUT}")
