#!/usr/bin/env python3
"""
Cross-Section Validator: Test Pattern Generalization
=====================================================

Tests whether zodiac patterns generalize to:
- Herbal section (f1-f66)
- Biological section (f75v-f84)
- Recipe section (f103-f116)

Compares:
- Morphological structure (PREFIX+ROOT+SUFFIX)
- Functional morpheme frequencies
- Compositional patterns
- Root distributions

Output: Cross-section comparison report
"""

import re
from pathlib import Path
from collections import defaultdict, Counter

# Section definitions (folio ranges)
SECTIONS = {
    'zodiac': {
        'folios': list(range(67, 74)) + [75],
        'recto_verso': ['r', 'v'],
        'description': 'Zodiac/astronomical diagrams'
    },
    'herbal': {
        'folios': list(range(1, 67)),
        'recto_verso': ['r', 'v'],
        'description': 'Herbal/botanical section'
    },
    'biological': {
        'folios': list(range(75, 85)),
        'recto_verso': ['v'],  # Start from 75v
        'description': 'Biological/cosmological section'
    },
    'recipes': {
        'folios': list(range(103, 117)),
        'recto_verso': ['r', 'v'],
        'description': 'Recipe/pharmaceutical section'
    }
}

# From validated SM1/SM4 analysis
PREFIXES = ['ch', 'ot', 'ok', 'sh', 'qo', 'da', 'yk', 'ol', 'sa', 'op', 'do']
SUFFIXES = ['ey', 'dy', 'in', 'ar', 'al', 'ol', 'os', 'or', 'es', 'oy', 'y', 'e', 'ed', 'om']

# High-confidence patterns from zodiac
HIGH_CONFIDENCE_PATTERNS = [
    'ch-[ROOT]-ey',
    'ot-[ROOT]-ey',
    'ot-[ROOT]-dy',
    'ch-[ROOT]-dy',
    'ch-[ROOT]-y',
    'ot-[ROOT]-y',
    'ok-[ROOT]-y',
    '[ROOT]-in',
    '[ROOT]-ar',
]


def load_section(section_name, filepath="transliteration.txt"):
    """Load all tokens from a specific section"""
    print(f"Loading {section_name} section...")
    
    section_def = SECTIONS[section_name]
    tokens = []
    
    current_folio = None
    
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            
            # Check for folio marker
            if line.startswith('<f') and '>' in line and '.' not in line.split('>')[0]:
                folio_match = re.match(r'<(f\d+[rv]\d*)>', line)
                if folio_match:
                    current_folio = folio_match.group(1)
                continue
            
            # Check if in target section
            if current_folio:
                # Extract folio number and r/v
                folio_match = re.match(r'f(\d+)([rv])', current_folio)
                if folio_match:
                    folio_num = int(folio_match.group(1))
                    folio_rv = folio_match.group(2)
                    
                    # Check if in section
                    if folio_num in section_def['folios']:
                        if folio_rv in section_def['recto_verso'] or section_def['recto_verso'] == ['r', 'v']:
                            # This is a text line
                            if line.startswith('<') and '>' in line:
                                parts = line.split('>', 1)
                                if len(parts) == 2:
                                    text = parts[1].strip()
                                    
                                    # Split tokens
                                    words = re.split(r'[.\s]+', text)
                                    
                                    for token in words:
                                        # Clean token
                                        token = re.sub(r'[{}\[\]@,;:!?\d\'"-]', '', token)
                                        token = token.strip()
                                        
                                        # Valid token
                                        if token and len(token) > 1 and token.isalpha():
                                            tokens.append(token)
    
    print(f"  Loaded {len(tokens)} tokens")
    return tokens


def extract_morphemes(token):
    """Extract PREFIX + ROOT + SUFFIX from token"""
    # Try each prefix
    for prefix in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            remainder = token[len(prefix):]
            
            # Try each suffix
            for suffix in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(suffix):
                    root = remainder[:-len(suffix)] if suffix else remainder
                    
                    if root:
                        return (prefix, root, suffix)
            
            # No suffix
            if remainder:
                return (prefix, remainder, '')
    
    # No prefix - check suffix only
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(suffix):
            root = token[:-len(suffix)] if suffix else token
            if root and len(root) > 1:
                return ('', root, suffix)
    
    # No morphemes
    return ('', token, '')


def analyze_section(tokens, section_name):
    """Analyze morphological structure of section"""
    
    results = {
        'section': section_name,
        'total_tokens': len(tokens),
        'morpheme_patterns': Counter(),
        'prefix_freq': Counter(),
        'suffix_freq': Counter(),
        'roots': set(),
        'pattern_types': Counter(),
        'high_confidence_patterns': Counter()
    }
    
    for token in tokens:
        prefix, root, suffix = extract_morphemes(token)
        
        results['roots'].add(root)
        
        if prefix:
            results['prefix_freq'][prefix] += 1
        if suffix:
            results['suffix_freq'][suffix] += 1
        
        # Pattern type
        if prefix and suffix:
            pattern_type = 'PREFIX+ROOT+SUFFIX'
            pattern_key = f"{prefix}-[ROOT]-{suffix}"
        elif prefix:
            pattern_type = 'PREFIX+ROOT'
            pattern_key = f"{prefix}-[ROOT]"
        elif suffix:
            pattern_type = 'ROOT+SUFFIX'
            pattern_key = f"[ROOT]-{suffix}"
        else:
            pattern_type = 'ROOT_ONLY'
            pattern_key = '[ROOT]'
        
        results['pattern_types'][pattern_type] += 1
        results['morpheme_patterns'][pattern_key] += 1
        
        # Check high-confidence patterns
        if pattern_key in HIGH_CONFIDENCE_PATTERNS:
            results['high_confidence_patterns'][pattern_key] += 1
    
    return results


def compare_sections(all_results):
    """Compare results across sections"""
    
    print("\n" + "=" * 80)
    print("CROSS-SECTION COMPARISON")
    print("=" * 80)
    
    # Summary table
    print("\n1. BASIC STATISTICS")
    print("-" * 80)
    print(f"{'Section':<15} {'Tokens':>10} {'Unique Roots':>15} {'Patterns':>15}")
    print("-" * 80)
    
    for section in ['zodiac', 'herbal', 'biological', 'recipes']:
        if section in all_results:
            r = all_results[section]
            print(f"{section:<15} {r['total_tokens']:>10} {len(r['roots']):>15} "
                  f"{len(r['morpheme_patterns']):>15}")
    
    # Morpheme structure comparison
    print("\n2. MORPHOLOGICAL STRUCTURE")
    print("-" * 80)
    print(f"{'Section':<15} {'P+R+S':>10} {'P+R':>10} {'R+S':>10} {'R only':>10}")
    print("-" * 80)
    
    for section in ['zodiac', 'herbal', 'biological', 'recipes']:
        if section in all_results:
            r = all_results[section]
            total = r['total_tokens']
            prs = 100 * r['pattern_types']['PREFIX+ROOT+SUFFIX'] / total if total else 0
            pr = 100 * r['pattern_types']['PREFIX+ROOT'] / total if total else 0
            rs = 100 * r['pattern_types']['ROOT+SUFFIX'] / total if total else 0
            ro = 100 * r['pattern_types']['ROOT_ONLY'] / total if total else 0
            
            print(f"{section:<15} {prs:>9.1f}% {pr:>9.1f}% {rs:>9.1f}% {ro:>9.1f}%")
    
    # Prefix comparison (top 5)
    print("\n3. TOP PREFIXES (% of tokens)")
    print("-" * 80)
    
    zodiac_prefixes = all_results['zodiac']['prefix_freq']
    zodiac_total = all_results['zodiac']['total_tokens']
    
    top_prefixes = [p for p, _ in zodiac_prefixes.most_common(5)]
    
    print(f"{'Section':<15} " + " ".join(f"{p:>8}" for p in top_prefixes))
    print("-" * 80)
    
    for section in ['zodiac', 'herbal', 'biological', 'recipes']:
        if section in all_results:
            r = all_results[section]
            total = r['total_tokens']
            values = []
            for prefix in top_prefixes:
                pct = 100 * r['prefix_freq'][prefix] / total if total else 0
                values.append(f"{pct:>7.1f}%")
            print(f"{section:<15} " + " ".join(values))
    
    # Suffix comparison (top 5)
    print("\n4. TOP SUFFIXES (% of tokens)")
    print("-" * 80)
    
    zodiac_suffixes = all_results['zodiac']['suffix_freq']
    top_suffixes = [s for s, _ in zodiac_suffixes.most_common(5)]
    
    print(f"{'Section':<15} " + " ".join(f"{s:>8}" for s in top_suffixes))
    print("-" * 80)
    
    for section in ['zodiac', 'herbal', 'biological', 'recipes']:
        if section in all_results:
            r = all_results[section]
            total = r['total_tokens']
            values = []
            for suffix in top_suffixes:
                pct = 100 * r['suffix_freq'][suffix] / total if total else 0
                values.append(f"{pct:>7.1f}%")
            print(f"{section:<15} " + " ".join(values))
    
    # High-confidence patterns
    print("\n5. HIGH-CONFIDENCE PATTERNS FROM ZODIAC")
    print("-" * 80)
    print(f"{'Pattern':<20} {'Zodiac':>10} {'Herbal':>10} {'Bio':>10} {'Recipe':>10}")
    print("-" * 80)
    
    for pattern in HIGH_CONFIDENCE_PATTERNS[:7]:  # Top 7
        values = []
        for section in ['zodiac', 'herbal', 'biological', 'recipes']:
            if section in all_results:
                count = all_results[section]['high_confidence_patterns'][pattern]
                total = all_results[section]['total_tokens']
                pct = 100 * count / total if total else 0
                values.append(f"{pct:>9.1f}%")
            else:
                values.append(f"{'N/A':>10}")
        
        print(f"{pattern:<20} " + " ".join(values))
    
    # Overall assessment
    print("\n6. GENERALIZATION ASSESSMENT")
    print("-" * 80)
    
    zodiac_structure = all_results['zodiac']['pattern_types']
    z_total = all_results['zodiac']['total_tokens']
    z_prs_pct = 100 * zodiac_structure['PREFIX+ROOT+SUFFIX'] / z_total
    
    for section in ['herbal', 'biological', 'recipes']:
        if section in all_results:
            r = all_results[section]
            total = r['total_tokens']
            prs_pct = 100 * r['pattern_types']['PREFIX+ROOT+SUFFIX'] / total
            
            diff = abs(prs_pct - z_prs_pct)
            
            if diff < 5:
                status = "✅ SIMILAR"
            elif diff < 10:
                status = "⚠️  SOMEWHAT DIFFERENT"
            else:
                status = "❌ VERY DIFFERENT"
            
            print(f"{section:<15} P+R+S: {prs_pct:>5.1f}% (zodiac: {z_prs_pct:.1f}%) → {status}")


def main():
    print("=" * 80)
    print("CROSS-SECTION MORPHOLOGICAL VALIDATOR")
    print("=" * 80)
    print("\nTesting if zodiac patterns generalize to other sections...")
    
    all_results = {}
    
    # Analyze each section
    for section in ['zodiac', 'herbal', 'biological', 'recipes']:
        print(f"\n--- Analyzing {section.upper()} section ---")
        
        try:
            tokens = load_section(section)
            
            if tokens:
                results = analyze_section(tokens, section)
                all_results[section] = results
                print(f"  ✓ Analysis complete")
            else:
                print(f"  ⚠ No tokens found")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Compare results
    if len(all_results) > 1:
        compare_sections(all_results)
        
        # Write report
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "cross_section_validation.txt", 'w') as f:
            f.write("CROSS-SECTION VALIDATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            for section, r in all_results.items():
                f.write(f"\n{section.upper()} SECTION:\n")
                f.write(f"  Tokens: {r['total_tokens']}\n")
                f.write(f"  Unique roots: {len(r['roots'])}\n")
                f.write(f"  Patterns: {len(r['morpheme_patterns'])}\n")
                
                total = r['total_tokens']
                f.write(f"  P+R+S: {100*r['pattern_types']['PREFIX+ROOT+SUFFIX']/total:.1f}%\n")
                f.write(f"  P+R:   {100*r['pattern_types']['PREFIX+ROOT']/total:.1f}%\n")
                f.write(f"  R+S:   {100*r['pattern_types']['ROOT+SUFFIX']/total:.1f}%\n")
                f.write(f"  R:     {100*r['pattern_types']['ROOT_ONLY']/total:.1f}%\n")
        
        print(f"\n✓ Report saved to: results/cross_section_validation.txt")
    
    print("\n" + "=" * 80)
    print("CROSS-SECTION VALIDATION COMPLETE")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
