#!/usr/bin/env python3
"""
Test 4: Suffix Phonological Classes
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
N4 = BASE / "N4_Frozen_Model"
TOK = BASE / "corpora/romance_tokenized"

print("="*80)
print("TEST 4: SUFFIX PHONOLOGICAL PATTERNS")
print("="*80)

def classify_suffix(suf):
    """Classify suffix by phonological ending"""
    suf = str(suf).lower()
    if len(suf) == 0:
        return 'null'
    
    last = suf[-1]
    if last in 'aeiou':
        return 'vowel'
    elif last in 'lrn':
        return 'liquid/nasal'
    elif last in 'tdskp':
        return 'stop'
    elif last in 'my':
        return 'sonorant'
    else:
        return 'other'

# Voynich suffixes
v_suf = pd.read_csv(N4 / "PhaseM/out/m01_suffix_inventory.tsv", sep='\t')
v_suf = v_suf.dropna(subset=['suffix'])
v_suf['class'] = v_suf['suffix'].apply(classify_suffix)

print("\nVoynich suffix phonological classes:")
v_class_dist = v_suf.groupby('class')['token_count'].sum()
v_total = v_class_dist.sum()
v_class_dist = v_class_dist / v_total

for cls in sorted(v_class_dist.index):
    prob = v_class_dist[cls]
    examples = list(v_suf[v_suf['class']==cls]['suffix'][:3])
    print(f"  {cls:15s}: {prob:6.1%}  (e.g., {', '.join(str(e) for e in examples)})")

# Compare to Romance
print("\n" + "="*80)
print("ROMANCE LANGUAGE COMPARISONS")
print("="*80)

results = []

for lang in ['french', 'latin', 'catalan', 'italian']:
    suf_file = TOK / f"{lang}_suffixes.tsv"
    if not suf_file.exists():
        continue
    
    l_suf = pd.read_csv(suf_file, sep='\t')
    l_suf['class'] = l_suf['suffix'].apply(classify_suffix)
    
    l_class_dist = l_suf.groupby('class')['count'].sum()
    l_total = l_class_dist.sum()
    l_class_dist = l_class_dist / l_total
    
    print(f"\n{lang.capitalize()}:")
    
    # Calculate similarity to Voynich
    similarity = 0
    for cls in set(v_class_dist.index) | set(l_class_dist.index):
        v_val = v_class_dist.get(cls, 0)
        l_val = l_class_dist.get(cls, 0)
        
        # Show values
        if v_val > 0.01 or l_val > 0.01:  # Only show significant classes
            print(f"  {cls:15s}: {l_val:6.1%}  (Voynich={v_val:6.1%}, diff={abs(v_val-l_val):6.1%})")
        
        # Similarity (inverse of difference)
        similarity += (1 - abs(v_val - l_val))
    
    results.append({
        'language': lang.capitalize(),
        'similarity': similarity / len(set(v_class_dist.index) | set(l_class_dist.index))
    })

# Rank
df = pd.DataFrame(results).sort_values('similarity', ascending=False)

print("\n" + "="*80)
print("PHONOLOGICAL PATTERN SIMILARITY RANKING")
print("="*80)

for _, row in df.iterrows():
    print(f"\n{row['language']}: {row['similarity']:.3f}")

best = df.iloc[0]
print(f"\n🏆 BEST PHONOLOGICAL MATCH: {best['language']} ({best['similarity']:.3f})")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)
print("\n✅ Tests if suffix TYPES match (vowel-final vs consonant-final)")
print("⚠️  NOT exact suffix identity (due to compression)")
print("💡 Romance languages cluster suffixes by phonological class")
print("💡 If Voynichese matches, suggests Romance-like morphology")

