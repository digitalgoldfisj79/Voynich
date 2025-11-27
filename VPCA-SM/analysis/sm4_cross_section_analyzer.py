#!/usr/bin/env python3
"""
SM4: Cross-Section Generalization Test
======================================

Tests whether zodiac patterns generalize to other manuscript sections.

Sections analyzed:
  - Herbal (f1r-f66v): plant descriptions
  - Zodiac (f67r-f73v): astrological diagrams
  - Biological (f75r-f84v): tubes/human figures
  - Recipes (f103r-f116v): text paragraphs

Output:
  - Cross-section pattern comparison
  - Generalization assessment
  - Section-specific vs universal patterns

Author: SM4 Cross-Section Analysis, November 27, 2025
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

# Paths
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Outputs
COMPARISON_JSON = RESULTS_DIR / "sm4_cross_section_comparison.json"
COMPARISON_TXT = RESULTS_DIR / "sm4_cross_section_analysis.txt"
COMPARISON_TSV = RESULTS_DIR / "sm4_cross_section_patterns.tsv"

# From SM1 - validated morphemes
PREFIXES = ['ch', 'ot', 'ok', 'sh', 'qo', 'da', 'yk', 'ol', 'sa', 'op', 'do']
SUFFIXES = ['ey', 'dy', 'in', 'ar', 'al', 'ol', 'os', 'or', 'es', 'oy', 'y', 'e', 'ed', 'om']

# Section definitions
SECTIONS = {
    'Herbal': range(1, 67),      # f1r-f66v
    'Zodiac': range(67, 74),     # f67r-f73v (includes f73)
    'Biological': range(75, 85), # f75r-f84v
    'Recipes': range(103, 117),  # f103r-f116v
}


def load_section_tokens(filepath="transliteration.txt", section_name=None, folio_range=None):
    """
    Load tokens from specific manuscript section.
    
    Args:
        filepath: Path to IVTFF transliteration file
        section_name: Name of section (for display)
        folio_range: Range of folio numbers to extract
    """
    print(f"Loading {section_name} section (f{min(folio_range)}-f{max(folio_range)})...")
    
    tokens = []
    current_folio = None
    
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                
                # Check for folio marker
                if line.startswith('<f') and '>' in line and '.' not in line.split('>')[0]:
                    folio_match = re.match(r'<f(\d+)[rv]\d*>', line)
                    if folio_match:
                        current_folio = int(folio_match.group(1))
                    continue
                
                # Process lines in target section
                if current_folio and current_folio in folio_range:
                    if line.startswith('<') and '>' in line:
                        parts = line.split('>', 1)
                        if len(parts) == 2:
                            text = parts[1].strip()
                            
                            # Split tokens
                            token_list = re.split(r'[.\s]+', text)
                            
                            for token in token_list:
                                # Clean token
                                token = re.sub(r'[{}\[\]@,;:!?\d\'"-]', '', token)
                                token = token.strip()
                                
                                # Valid token: alphabetic, length > 1
                                if token and len(token) > 1 and token.isalpha():
                                    tokens.append(token)
        
        print(f"  Loaded {len(tokens)} tokens")
        return tokens
        
    except FileNotFoundError:
        print(f"  ERROR: Could not find {filepath}")
        return []


def extract_morphemes(token):
    """Extract PREFIX + ROOT + SUFFIX from token."""
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
    
    # No morphemes - entire token is root
    return ('', token, '')


def analyze_section_patterns(tokens, section_name):
    """Analyze morpheme patterns in section."""
    print(f"\nAnalyzing {section_name} patterns...")
    
    patterns = defaultdict(int)
    prefix_counts = Counter()
    suffix_counts = Counter()
    root_counts = Counter()
    
    # Pattern categories
    full_pattern = 0  # PREFIX+ROOT+SUFFIX
    prefix_only = 0   # PREFIX+ROOT
    suffix_only = 0   # ROOT+SUFFIX
    root_only = 0     # ROOT
    
    for token in tokens:
        result = extract_morphemes(token)
        
        if result:
            prefix, root, suffix = result
            
            # Count morphemes
            if prefix:
                prefix_counts[prefix] += 1
            if suffix:
                suffix_counts[suffix] += 1
            root_counts[root] += 1
            
            # Pattern key
            if prefix and suffix:
                pattern_key = f"{prefix}-[ROOT]-{suffix}"
                full_pattern += 1
            elif prefix:
                pattern_key = f"{prefix}-[ROOT]"
                prefix_only += 1
            elif suffix:
                pattern_key = f"[ROOT]-{suffix}"
                suffix_only += 1
            else:
                pattern_key = "[ROOT]"
                root_only += 1
            
            patterns[pattern_key] += 1
    
    return {
        'patterns': patterns,
        'prefix_counts': prefix_counts,
        'suffix_counts': suffix_counts,
        'root_counts': root_counts,
        'structure_distribution': {
            'PREFIX+ROOT+SUFFIX': full_pattern,
            'PREFIX+ROOT': prefix_only,
            'ROOT+SUFFIX': suffix_only,
            'ROOT': root_only,
        },
        'total_tokens': len(tokens),
    }


def compare_sections(section_results):
    """Compare patterns across sections."""
    print("\nComparing patterns across sections...")
    
    # Find common patterns (present in all sections)
    all_patterns = set()
    for section_name, data in section_results.items():
        all_patterns.update(data['patterns'].keys())
    
    common_patterns = set(all_patterns)
    for section_name, data in section_results.items():
        section_patterns = set(data['patterns'].keys())
        common_patterns &= section_patterns
    
    # Universal vs section-specific
    universal = {}
    section_specific = defaultdict(list)
    
    for pattern in all_patterns:
        sections_with = [s for s, d in section_results.items() 
                        if pattern in d['patterns']]
        
        if len(sections_with) == len(section_results):
            # Present in all sections
            universal[pattern] = {
                s: d['patterns'][pattern] 
                for s, d in section_results.items()
            }
        else:
            # Section-specific
            for section in sections_with:
                section_specific[section].append(pattern)
    
    return {
        'total_patterns': len(all_patterns),
        'universal_patterns': len(universal),
        'common_pattern_details': universal,
        'section_specific': {
            s: len(patterns) for s, patterns in section_specific.items()
        }
    }


def write_analysis(section_results, comparison):
    """Write human-readable analysis."""
    print(f"\nWriting analysis to {COMPARISON_TXT}...")
    
    with open(COMPARISON_TXT, 'w') as f:
        f.write("SM4: CROSS-SECTION GENERALIZATION TEST\n")
        f.write("=" * 70 + "\n\n")
        
        # Section overview
        f.write("SECTION STATISTICS\n")
        f.write("-" * 70 + "\n\n")
        
        for section_name in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
            if section_name not in section_results:
                continue
            
            data = section_results[section_name]
            
            f.write(f"{section_name}:\n")
            f.write(f"  Total tokens:    {data['total_tokens']:>8,}\n")
            f.write(f"  Unique patterns: {len(data['patterns']):>8}\n")
            f.write(f"  Unique roots:    {len(data['root_counts']):>8}\n")
            f.write(f"  Unique prefixes: {len(data['prefix_counts']):>8}\n")
            f.write(f"  Unique suffixes: {len(data['suffix_counts']):>8}\n")
            
            # Structure distribution
            dist = data['structure_distribution']
            total = data['total_tokens']
            f.write(f"\n  Structure distribution:\n")
            for struct, count in dist.items():
                pct = 100 * count / total if total > 0 else 0
                f.write(f"    {struct:<20} {count:>8} ({pct:>5.1f}%)\n")
            
            f.write("\n")
        
        # Cross-section comparison
        f.write("\n\nCROSS-SECTION COMPARISON\n")
        f.write("-" * 70 + "\n\n")
        
        f.write(f"Total unique patterns (all sections): {comparison['total_patterns']}\n")
        f.write(f"Universal patterns (in all 4 sections): {comparison['universal_patterns']}\n")
        f.write(f"Universality: {100*comparison['universal_patterns']/comparison['total_patterns']:.1f}%\n\n")
        
        # Section-specific patterns
        f.write("Section-specific patterns:\n")
        for section, count in comparison['section_specific'].items():
            f.write(f"  {section:<12} {count:>6} unique patterns\n")
        
        # Top universal patterns
        f.write("\n\nTOP 20 UNIVERSAL PATTERNS (present in all sections)\n")
        f.write("-" * 70 + "\n\n")
        
        # Sort by total frequency across sections
        universal = comparison['common_pattern_details']
        sorted_universal = sorted(
            universal.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True
        )
        
        for i, (pattern, counts) in enumerate(sorted_universal[:20], 1):
            total = sum(counts.values())
            f.write(f"{i}. {pattern:<25} {total:>6} total\n")
            for section in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
                count = counts.get(section, 0)
                f.write(f"     {section:<12} {count:>6}\n")
            f.write("\n")
        
        # Morpheme comparison
        f.write("\n\nTOP PREFIXES BY SECTION\n")
        f.write("-" * 70 + "\n\n")
        
        for section_name in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
            if section_name not in section_results:
                continue
            
            data = section_results[section_name]
            f.write(f"{section_name}:\n")
            
            for prefix, count in data['prefix_counts'].most_common(10):
                pct = 100 * count / data['total_tokens']
                f.write(f"  {prefix:<10} {count:>8} ({pct:>5.2f}%)\n")
            
            f.write("\n")
        
        # Generalization assessment
        f.write("\n\nGENERALIZATION ASSESSMENT\n")
        f.write("-" * 70 + "\n\n")
        
        universality = 100 * comparison['universal_patterns'] / comparison['total_patterns']
        
        if universality > 70:
            f.write("✅ HIGH GENERALIZATION (>70%)\n")
            f.write("Most patterns are universal across manuscript.\n")
            f.write("Zodiac findings strongly generalize.\n")
        elif universality > 50:
            f.write("⚠️ MODERATE GENERALIZATION (50-70%)\n")
            f.write("Many patterns are universal, but significant section variation.\n")
            f.write("Zodiac findings partially generalize.\n")
        else:
            f.write("❌ LOW GENERALIZATION (<50%)\n")
            f.write("Most patterns are section-specific.\n")
            f.write("Zodiac findings do NOT generalize well.\n")


def write_json(section_results, comparison):
    """Write JSON output."""
    print(f"Writing JSON to {COMPARISON_JSON}...")
    
    output = {
        'metadata': {
            'version': 'SM4-CrossSection-v1',
            'sections_analyzed': list(section_results.keys()),
        },
        'section_results': {},
        'comparison': comparison,
    }
    
    for section_name, data in section_results.items():
        output['section_results'][section_name] = {
            'total_tokens': data['total_tokens'],
            'unique_patterns': len(data['patterns']),
            'unique_roots': len(data['root_counts']),
            'structure_distribution': data['structure_distribution'],
            'top_patterns': [
                {'pattern': p, 'count': c}
                for p, c in sorted(data['patterns'].items(), 
                                  key=lambda x: x[1], reverse=True)[:50]
            ],
            'top_prefixes': [
                {'prefix': p, 'count': c}
                for p, c in data['prefix_counts'].most_common(20)
            ],
            'top_suffixes': [
                {'suffix': s, 'count': c}
                for s, c in data['suffix_counts'].most_common(20)
            ],
        }
    
    with open(COMPARISON_JSON, 'w') as f:
        json.dump(output, f, indent=2)


def write_tsv(section_results, comparison):
    """Write TSV for pattern comparison."""
    print(f"Writing TSV to {COMPARISON_TSV}...")
    
    # Get all patterns
    all_patterns = set()
    for data in section_results.values():
        all_patterns.update(data['patterns'].keys())
    
    with open(COMPARISON_TSV, 'w') as f:
        # Header
        sections = ['Herbal', 'Zodiac', 'Biological', 'Recipes']
        f.write(f"pattern\t" + "\t".join(sections) + "\ttotal\tuniversal\n")
        
        # Sort by total frequency
        pattern_totals = {}
        for pattern in all_patterns:
            total = sum(
                section_results[s]['patterns'].get(pattern, 0)
                for s in sections if s in section_results
            )
            pattern_totals[pattern] = total
        
        for pattern in sorted(pattern_totals.keys(), 
                             key=lambda x: pattern_totals[x], 
                             reverse=True):
            
            counts = []
            for section in sections:
                if section in section_results:
                    count = section_results[section]['patterns'].get(pattern, 0)
                    counts.append(str(count))
                else:
                    counts.append('0')
            
            total = pattern_totals[pattern]
            
            # Check if universal
            present_in = sum(1 for c in counts if int(c) > 0)
            universal = 'yes' if present_in == len(sections) else 'no'
            
            f.write(f"{pattern}\t" + "\t".join(counts) + f"\t{total}\t{universal}\n")


def main():
    print("=" * 70)
    print("SM4: CROSS-SECTION GENERALIZATION TEST")
    print("=" * 70)
    print("\nTesting whether zodiac patterns generalize to full manuscript...\n")
    
    # Load all sections
    section_results = {}
    
    for section_name, folio_range in SECTIONS.items():
        tokens = load_section_tokens(
            filepath="transliteration.txt",
            section_name=section_name,
            folio_range=folio_range
        )
        
        if tokens:
            section_results[section_name] = analyze_section_patterns(tokens, section_name)
    
    if not section_results:
        print("\nERROR: No sections loaded successfully.")
        return 1
    
    # Compare sections
    comparison = compare_sections(section_results)
    
    # Write outputs
    write_analysis(section_results, comparison)
    write_json(section_results, comparison)
    write_tsv(section_results, comparison)
    
    print("\n" + "=" * 70)
    print("CROSS-SECTION ANALYSIS COMPLETE")
    print("=" * 70)
    
    print(f"\nKey Findings:")
    print(f"  Sections analyzed: {len(section_results)}")
    print(f"  Total patterns: {comparison['total_patterns']}")
    print(f"  Universal patterns: {comparison['universal_patterns']}")
    
    universality = 100 * comparison['universal_patterns'] / comparison['total_patterns']
    print(f"  Universality: {universality:.1f}%")
    
    if universality > 70:
        print("\n✅ HIGH GENERALIZATION: Zodiac findings strongly generalize!")
    elif universality > 50:
        print("\n⚠️ MODERATE GENERALIZATION: Zodiac findings partially generalize.")
    else:
        print("\n❌ LOW GENERALIZATION: Zodiac findings do NOT generalize well.")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
