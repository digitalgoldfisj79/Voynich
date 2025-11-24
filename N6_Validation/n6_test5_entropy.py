#!/usr/bin/env python3
"""
N6 Test 5: Entropy Reduction

If N5 mapping is correct, it should reduce entropy (increase predictability).
Random mappings increase entropy (noise).

Pass criteria:
- H1 reduction ≥ 0.12 bits
- H2 reduction ≥ 0.20 bits  
- Bootstrap p < 0.01
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import random
import json

BASE = Path(__file__).parent.parent

print("="*80)
print("N6 TEST 5: ENTROPY REDUCTION")
print("="*80)

# Load N5 hypotheses (top candidate per stem)
h5 = pd.read_csv(BASE / "N5_Hypotheses/h5_candidates.tsv", sep='\t')
top_hyp = h5[h5['candidate_rank'] == 1].set_index('stem')['candidate_latin'].to_dict()

print(f"\nN5 hypotheses: {len(top_hyp)} stem mappings")

# Load Voynich tokens
with open(BASE / "corpora/p6_voynich_tokens.txt") as f:
    voynich_tokens = f.read().split()

print(f"Total tokens: {len(voynich_tokens)}")

# Calculate entropy functions
def char_entropy(text):
    """H1: Character-level entropy"""
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c/total) * np.log2(c/total) for c in counts.values())

def bigram_entropy(sequence):
    """H2: Bigram entropy"""
    bigrams = list(zip(sequence[:-1], sequence[1:]))
    if not bigrams:
        return 0.0
    counts = Counter(bigrams)
    total = len(bigrams)
    return -sum((c/total) * np.log2(c/total) for c in counts.values())

# Map to Latin
def map_text(tokens, mapping):
    return [mapping.get(t, "UNK") for t in tokens]

print("\n[1/5] Computing baseline (Voynich original)...")
voynich_text = ' '.join(voynich_tokens)
h1_voynich = char_entropy(voynich_text)
h2_voynich = bigram_entropy(voynich_tokens)

print(f"  H1 (Voynich): {h1_voynich:.3f} bits")
print(f"  H2 (Voynich): {h2_voynich:.3f} bits")

print("\n[2/5] Computing N5 mapping...")
latin_seq_n5 = map_text(voynich_tokens, top_hyp)
latin_text_n5 = ' '.join(latin_seq_n5)
h1_n5 = char_entropy(latin_text_n5)
h2_n5 = bigram_entropy(latin_seq_n5)

print(f"  H1 (N5 Latin): {h1_n5:.3f} bits")
print(f"  H2 (N5 Latin): {h2_n5:.3f} bits")

h1_reduction = h1_voynich - h1_n5
h2_reduction = h2_voynich - h2_n5

print(f"\n  H1 reduction: {h1_reduction:.3f} bits ({h1_reduction/h1_voynich*100:+.1f}%)")
print(f"  H2 reduction: {h2_reduction:.3f} bits ({h2_reduction/h2_voynich*100:+.1f}%)")

print("\n[3/5] Random baseline (1000 permutations)...")
all_latin = list(h5['candidate_latin'].unique())
random_h1 = []
random_h2 = []

for i in range(1000):
    rand_map = {stem: random.choice(all_latin) for stem in top_hyp.keys()}
    rand_seq = map_text(voynich_tokens, rand_map)
    rand_text = ' '.join(rand_seq)
    
    random_h1.append(char_entropy(rand_text))
    random_h2.append(bigram_entropy(rand_seq))
    
    if (i+1) % 200 == 0:
        print(f"    {i+1}/1000...")

random_h1 = np.array(random_h1)
random_h2 = np.array(random_h2)

mean_h1_rand = random_h1.mean()
mean_h2_rand = random_h2.mean()

print(f"\n  Random H1: {mean_h1_rand:.3f} ± {random_h1.std():.3f}")
print(f"  Random H2: {mean_h2_rand:.3f} ± {random_h2.std():.3f}")

print("\n[4/5] Bootstrap confidence intervals...")
n_boot = 1000
boot_h1 = []
boot_h2 = []

for _ in range(n_boot):
    indices = np.random.choice(len(voynich_tokens), len(voynich_tokens), replace=True)
    boot_tokens = [voynich_tokens[i] for i in indices]
    boot_seq = map_text(boot_tokens, top_hyp)
    boot_text = ' '.join(boot_seq)
    
    boot_h1.append(char_entropy(boot_text))
    boot_h2.append(bigram_entropy(boot_seq))

boot_h1 = np.array(boot_h1)
boot_h2 = np.array(boot_h2)

ci_h1_low, ci_h1_high = np.percentile(boot_h1, [2.5, 97.5])
ci_h2_low, ci_h2_high = np.percentile(boot_h2, [2.5, 97.5])

print(f"  H1 95% CI: [{ci_h1_low:.3f}, {ci_h1_high:.3f}]")
print(f"  H2 95% CI: [{ci_h2_low:.3f}, {ci_h2_high:.3f}]")

print("\n[5/5] Statistical tests...")

# P-values
p_h1 = (random_h1 <= h1_n5).sum() / len(random_h1)
p_h2 = (random_h2 <= h2_n5).sum() / len(random_h2)

print(f"  P(random <= N5) for H1: {p_h1:.4f}")
print(f"  P(random <= N5) for H2: {p_h2:.4f}")

# Test pass/fail
print("\n" + "="*80)
print("TEST 5 RESULTS")
print("="*80)

criteria_met = []

# Criterion 1: H1 reduction
if h1_reduction >= 0.12:
    print(f"\n✓ H1 reduction ({h1_reduction:.3f}) >= 0.12 bits")
    criteria_met.append(True)
else:
    print(f"\n✗ H1 reduction ({h1_reduction:.3f}) < 0.12 bits")
    criteria_met.append(False)

# Criterion 2: H2 reduction  
if h2_reduction >= 0.20:
    print(f"✓ H2 reduction ({h2_reduction:.3f}) >= 0.20 bits")
    criteria_met.append(True)
else:
    print(f"✗ H2 reduction ({h2_reduction:.3f}) < 0.20 bits")
    criteria_met.append(False)

# Criterion 3: Bootstrap p-value
if p_h1 < 0.01 and p_h2 < 0.01:
    print(f"✓ Bootstrap p-values < 0.01")
    criteria_met.append(True)
else:
    print(f"✗ Bootstrap p-values not significant")
    criteria_met.append(False)

# Final verdict
if all(criteria_met):
    result = "PASS"
    print(f"\n🎉 TEST 5: PASS - N5 mapping shows significant entropy reduction")
else:
    result = "FAIL"
    print(f"\n❌ TEST 5: FAIL - N5 mapping does not meet entropy criteria")

# Save results
results = {
    'test_name': 'Entropy_Reduction',
    'timestamp': datetime.now().isoformat(),
    'voynich_h1': float(h1_voynich),
    'voynich_h2': float(h2_voynich),
    'n5_h1': float(h1_n5),
    'n5_h2': float(h2_n5),
    'h1_reduction': float(h1_reduction),
    'h2_reduction': float(h2_reduction),
    'baseline_h1_mean': float(mean_h1_rand),
    'baseline_h2_mean': float(mean_h2_rand),
    'p_value_h1': float(p_h1),
    'p_value_h2': float(p_h2),
    'ci_h1': [float(ci_h1_low), float(ci_h1_high)],
    'ci_h2': [float(ci_h2_low), float(ci_h2_high)],
    'result': result,
    'criteria_met': criteria_met
}

output = BASE / "N6_Validation/test5_entropy_results.json"
with open(output, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Saved: {output}")

