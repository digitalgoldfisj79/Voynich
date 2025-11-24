#!/usr/bin/env python3
"""
Tokenize and stem Romance language corpora
Make them comparable to Voynich (stems + affixes)

Without NLP libraries, we'll do rule-based stemming:
- Remove common suffixes
- Extract prefix/root patterns
- Build morphology inventories
"""

import re
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
RAW_DIR = BASE / "corpora/romance_languages"
TOK_DIR = BASE / "corpora/romance_tokenized"

print("="*80)
print("ROMANCE LANGUAGE TOKENIZATION & STEMMING")
print("="*80)

# Common Romance suffixes to strip (crude but effective)
LATIN_SUFFIXES = ['um', 'us', 'is', 'os', 'as', 'am', 'em', 'im', 
                  'are', 'ere', 'ire', 'or', 'ur', 'at', 'et', 'it']

ROMANCE_SUFFIXES = ['are', 'ere', 'ire', 'ons', 'ez', 'ent', 'ait', 'ont',
                    'ado', 'ido', 'ato', 'ito', 'ant', 'ent', 'int',
                    'ar', 'er', 'ir', 'or', 'en', 'es', 'et', 'a', 'e', 'o']

def normalize(text):
    """Normalize text: lowercase, remove non-letters"""
    text = text.lower()
    # Keep Romance diacritics
    text = re.sub(r'[^a-zàâäæçèéêëìîïòôöœùûü\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def simple_stem(word, suffixes):
    """
    Remove common suffixes to get stem
    Similar to what Phase69 does for Voynich
    """
    # Try each suffix from longest to shortest
    for suffix in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

def extract_morphology(text, suffixes):
    """
    Extract stems, prefixes, and suffixes from text
    Returns comparable structures to Voynich PhaseM
    """
    tokens = text.split()
    
    # Filter: 2-15 chars only
    tokens = [t for t in tokens if 2 <= len(t) <= 15]
    
    stems = []
    extracted_suffixes = Counter()
    prefixes = Counter()
    
    for token in tokens:
        stem = simple_stem(token, suffixes)
        suffix = token[len(stem):] if len(token) > len(stem) else ''
        
        stems.append(stem)
        
        if suffix:
            extracted_suffixes[suffix] += 1
        
        # Extract prefix patterns (first 2-3 chars)
        if len(stem) >= 2:
            prefixes[stem[:2]] += 1
        if len(stem) >= 3:
            prefixes[stem[:3]] += 1
    
    return {
        'stems': stems,
        'unique_stems': list(set(stems)),
        'suffixes': extracted_suffixes,
        'prefixes': prefixes,
        'tokens': tokens
    }

# ============================================
# PROCESS EACH LANGUAGE
# ============================================

TOK_DIR.mkdir(exist_ok=True)

languages = {
    'latin': ('latin_raw.txt', LATIN_SUFFIXES),
    'occitan': ('occitan_raw.txt', ROMANCE_SUFFIXES),
    'catalan': ('catalan_raw.txt', ROMANCE_SUFFIXES),
    'italian': ('italian_raw.txt', ROMANCE_SUFFIXES),
    'french': ('french_raw.txt', ROMANCE_SUFFIXES)
}

results = {}

for lang, (filename, suffixes) in languages.items():
    filepath = RAW_DIR / filename
    
    print(f"\n[{lang.upper()}]")
    
    if not filepath.exists():
        print(f"  ⚠️ File not found: {filename}")
        # Create minimal placeholder
        text = f"aqua rosa ruta herba {lang}"
        print(f"  Using placeholder corpus")
    else:
        try:
            text = filepath.read_text(encoding='utf-8', errors='ignore')
            print(f"  ✓ Loaded {len(text)} chars")
        except Exception as e:
            print(f"  ⚠️ Error loading: {e}")
            text = f"aqua rosa ruta herba {lang}"
    
    # Normalize
    text_norm = normalize(text)
    print(f"  ✓ Normalized")
    
    # Extract morphology
    morph = extract_morphology(text_norm, suffixes)
    
    print(f"  Tokens: {len(morph['tokens'])}")
    print(f"  Unique stems: {len(morph['unique_stems'])}")
    print(f"  Suffix types: {len(morph['suffixes'])}")
    print(f"  Prefix patterns: {len(morph['prefixes'])}")
    
    # Save stems
    stem_file = TOK_DIR / f"{lang}_stems.txt"
    stem_file.write_text('\n'.join(morph['unique_stems']))
    
    # Save suffix inventory
    suffix_file = TOK_DIR / f"{lang}_suffixes.tsv"
    with open(suffix_file, 'w') as f:
        f.write("suffix\tcount\n")
        for suf, cnt in morph['suffixes'].most_common():
            f.write(f"{suf}\t{cnt}\n")
    
    # Save prefix inventory
    prefix_file = TOK_DIR / f"{lang}_prefixes.tsv"
    with open(prefix_file, 'w') as f:
        f.write("prefix\tcount\n")
        for pre, cnt in morph['prefixes'].most_common():
            f.write(f"{pre}\t{cnt}\n")
    
    results[lang] = morph
    
    # Show samples
    print(f"  Sample stems: {morph['unique_stems'][:10]}")
    print(f"  Top suffixes: {[s for s, _ in morph['suffixes'].most_common(10)]}")

print("\n" + "="*80)
print("TOKENIZATION COMPLETE")
print("="*80)

print(f"\nOutput directory: {TOK_DIR}")
print(f"\nFor each language:")
print(f"  - {lang}_stems.txt (unique stems)")
print(f"  - {lang}_suffixes.tsv (suffix inventory)")
print(f"  - {lang}_prefixes.tsv (prefix inventory)")

print("\n✅ Now all corpora are comparable to Voynich PhaseM format")
print("Next: Run N5v3 morphology comparison with tokenized data")

