#!/usr/bin/env python3
"""
SM4: Compositional Pattern Analyzer
===================================

Identifies common PREFIX+ROOT+SUFFIX combinations and their properties.

Dependencies:
  - SM1 morpheme analysis results
  - SM2 semantic field mappings
  - Zodiac transliteration data

Output:
  - sm4_compositional_patterns.json (pattern database)
  - sm4_pattern_analysis.txt (human-readable report)
  - sm4_pattern_frequencies.tsv (detailed frequencies)

Author: SM4 Implementation, November 27, 2025
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

# Paths
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Outputs
PATTERNS_JSON = RESULTS_DIR / "sm4_compositional_patterns.json"
ANALYSIS_TXT = RESULTS_DIR / "sm4_pattern_analysis.txt"
FREQUENCIES_TSV = RESULTS_DIR / "sm4_pattern_frequencies.tsv"

# From SM1 - validated morphemes
PREFIXES = ['ch', 'ot', 'ok', 'sh', 'qo', 'da', 'yk', 'ol', 'sa', 'op', 'do']
SUFFIXES = ['ey', 'dy', 'in', 'ar', 'al', 'ol', 'os', 'or', 'es', 'oy', 'y', 'e', 'ed', 'om']

# From SM2 - semantic field mappings (root → field)
SEMANTIC_FIELDS = {
    'e': 'Modifier/Relation',
    'ee': 'Modifier/Relation',
    'k': 'Modifier/Relation',
    'ol': 'Quality/State',
    'al': 'Quality/State',
    'l': 'Quality/State',
    'eo': 'Quality/State',
    'o': 'Quality/State',
    'ar': 'Quality/State',
    'ey': 'Quality/State',
    'ai': 'Quality/State',
    'i': 'Process/Active',
    'ir': 'Process/Active',
    'ot': 'Process/Active',
    'ch': 'Entity/Object',
}

# Prefix functions (from SM1 functional analysis)
PREFIX_FUNCTIONS = {
    'ch': 'intensifier/modifier',
    'ot': 'transition/change',
    'ok': 'constituent/unit',
    'sh': 'unknown',
    'qo': 'unknown',
    'da': 'unknown',
    'yk': 'unknown',
    'ol': 'unknown',
    'sa': 'unknown',
    'op': 'unknown',
    'do': 'unknown',
}

# Suffix functions (from SM1 analysis)
SUFFIX_FUNCTIONS = {
    'ey': 'state_marker',
    'dy': 'process_marker',
    'in': 'nominal/substantive',
    'ar': 'agent/doer',
    'al': 'quality/attribute',
    'ol': 'unknown',
    'os': 'unknown',
    'or': 'unknown',
    'es': 'unknown',
    'oy': 'unknown',
    'y': 'state_marker',
    'e': 'unknown',
    'ed': 'unknown',
    'om': 'unknown',
}


def load_zodiac_labels(filepath="transliteration.txt"):
    """
    Load zodiac labels from IVTFF transliteration file.
    Extract only zodiac sections (f67-f73, f75).
    """
    print(f"Loading zodiac labels from {filepath}...")
    
    labels = []
    
    try:
        current_folio = None
        
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                
                # Check for folio marker (standalone line with just folio)
                if line.startswith('<f') and '>' in line and '.' not in line.split('>')[0]:
                    folio_match = re.match(r'<(f\d+[rv]\d*)>', line)
                    if folio_match:
                        current_folio = folio_match.group(1)
                    continue
                
                # Process lines in zodiac folios
                if current_folio:
                    folio_num_match = re.match(r'f(\d+)', current_folio)
                    if folio_num_match:
                        folio_num = int(folio_num_match.group(1))
                        
                        # Zodiac folios: 67-73, 75
                        if (67 <= folio_num <= 73) or folio_num == 75:
                            # This is a text line
                            if line.startswith('<') and '>' in line:
                                parts = line.split('>', 1)
                                if len(parts) == 2:
                                    text = parts[1].strip()
                                    
                                    # Split tokens
                                    tokens = re.split(r'[.\s]+', text)
                                    
                                    for token in tokens:
                                        # Clean token - remove special characters
                                        token = re.sub(r'[{}\[\]@,;:!?\d\'"-]', '', token)
                                        token = token.strip()
                                        
                                        # Valid token: alphabetic, length > 1
                                        if token and len(token) > 1 and token.isalpha():
                                            labels.append(token)
        
        print(f"Loaded {len(labels)} zodiac labels")
        return labels
        
    except FileNotFoundError:
        print(f"ERROR: Could not find {filepath}")
        print("Using fallback: empty dataset")
        return []


def extract_morphemes(token):
    """
    Extract PREFIX + ROOT + SUFFIX from token.
    Uses greedy longest-match for validated morphemes.
    
    Returns: (prefix, root, suffix) or None if can't parse
    """
    # Try each prefix
    for prefix in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            remainder = token[len(prefix):]
            
            # Try each suffix
            for suffix in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(suffix):
                    root = remainder[:-len(suffix)] if suffix else remainder
                    
                    # Valid if root exists and isn't empty
                    if root:
                        return (prefix, root, suffix)
            
            # No suffix - check if remainder is valid root
            if remainder:
                return (prefix, remainder, '')
    
    # No prefix - check suffix only
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(suffix):
            root = token[:-len(suffix)] if suffix else token
            if root and len(root) > 1:
                return ('', root, suffix)
    
    # No morphemes found - entire token is root
    return ('', token, '')


def analyze_patterns(labels):
    """
    Analyze all morpheme patterns in labels.
    """
    print("\nAnalyzing morpheme patterns...")
    
    patterns = defaultdict(lambda: {
        'count': 0,
        'tokens': [],
        'roots': Counter(),
        'examples': []
    })
    
    roots_only = Counter()
    prefix_root_combos = Counter()
    root_suffix_combos = Counter()
    
    parsed_count = 0
    
    for token in labels:
        result = extract_morphemes(token)
        
        if result:
            prefix, root, suffix = result
            parsed_count += 1
            
            # Pattern key
            if prefix and suffix:
                pattern_key = f"{prefix}-[ROOT]-{suffix}"
                pattern_type = "PREFIX+ROOT+SUFFIX"
            elif prefix:
                pattern_key = f"{prefix}-[ROOT]"
                pattern_type = "PREFIX+ROOT"
            elif suffix:
                pattern_key = f"[ROOT]-{suffix}"
                pattern_type = "ROOT+SUFFIX"
            else:
                pattern_key = "[ROOT]"
                pattern_type = "ROOT_ONLY"
            
            # Store pattern data
            patterns[pattern_key]['count'] += 1
            patterns[pattern_key]['type'] = pattern_type
            patterns[pattern_key]['prefix'] = prefix
            patterns[pattern_key]['suffix'] = suffix
            patterns[pattern_key]['roots'][root] += 1
            
            if len(patterns[pattern_key]['examples']) < 10:
                patterns[pattern_key]['examples'].append(token)
            
            # Store combinations
            roots_only[root] += 1
            if prefix:
                prefix_root_combos[(prefix, root)] += 1
            if suffix:
                root_suffix_combos[(root, suffix)] += 1
    
    print(f"Parsed {parsed_count}/{len(labels)} labels ({100*parsed_count/len(labels):.1f}%)")
    print(f"Found {len(patterns)} unique morpheme patterns")
    
    return patterns, roots_only, prefix_root_combos, root_suffix_combos


def classify_pattern(pattern_key, pattern_data):
    """
    Classify what this pattern might mean compositionally.
    """
    prefix = pattern_data.get('prefix', '')
    suffix = pattern_data.get('suffix', '')
    
    # Get most common root
    top_root = pattern_data['roots'].most_common(1)[0][0] if pattern_data['roots'] else ''
    root_field = SEMANTIC_FIELDS.get(top_root, 'Unknown')
    
    # Build compositional interpretation
    parts = []
    
    if prefix:
        parts.append(PREFIX_FUNCTIONS.get(prefix, 'unknown_prefix'))
    
    if root_field != 'Unknown':
        parts.append(root_field.lower())
    else:
        parts.append('unknown_root')
    
    if suffix:
        parts.append(SUFFIX_FUNCTIONS.get(suffix, 'unknown_suffix'))
    
    # Compositional meaning
    if parts:
        composition = ' + '.join(parts)
    else:
        composition = 'unclear'
    
    # Functional interpretation
    if prefix == 'ch' and suffix in ['y', 'ey'] and 'Quality' in root_field:
        interpretation = "intensified_quality_state"
    elif prefix == 'ot' and suffix in ['dy', 'y']:
        interpretation = "transitional_state/process"
    elif prefix == 'ok' and suffix == 'in':
        interpretation = "constituent_nominal"
    elif suffix == 'ar' and 'Quality' in root_field:
        interpretation = "quality_agent/doer"
    elif suffix == 'al':
        interpretation = "quality_attribute"
    else:
        interpretation = "unclear"
    
    return {
        'composition': composition,
        'interpretation': interpretation,
        'root_field': root_field,
        'confidence': estimate_confidence(prefix, root_field, suffix)
    }


def estimate_confidence(prefix, root_field, suffix):
    """
    Estimate confidence in compositional interpretation.
    """
    score = 0.0
    
    # Known prefix adds confidence
    if prefix in ['ch', 'ot', 'ok']:
        score += 0.3
    elif prefix:
        score += 0.1
    
    # Known semantic field adds confidence
    if root_field != 'Unknown':
        score += 0.3
    else:
        score += 0.05
    
    # Known suffix adds confidence
    if suffix in ['ey', 'dy', 'in', 'ar', 'al']:
        score += 0.3
    elif suffix:
        score += 0.1
    
    # Full pattern adds bonus
    if prefix and suffix:
        score += 0.1
    
    return min(score, 1.0)


def write_analysis(patterns, roots_only, prefix_root_combos, root_suffix_combos):
    """
    Write human-readable analysis.
    """
    print(f"\nWriting analysis to {ANALYSIS_TXT}...")
    
    with open(ANALYSIS_TXT, 'w') as f:
        f.write("SM4: COMPOSITIONAL PATTERN ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        
        # Sort patterns by frequency
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1]['count'], reverse=True)
        
        # Top 50 patterns
        f.write("TOP 50 MORPHEME PATTERNS\n")
        f.write("-" * 70 + "\n\n")
        
        for i, (pattern, data) in enumerate(sorted_patterns[:50], 1):
            classification = classify_pattern(pattern, data)
            
            f.write(f"{i}. {pattern}\n")
            f.write(f"   Count: {data['count']}\n")
            f.write(f"   Type: {data['type']}\n")
            f.write(f"   Composition: {classification['composition']}\n")
            f.write(f"   Interpretation: {classification['interpretation']}\n")
            f.write(f"   Confidence: {classification['confidence']:.2f}\n")
            top_roots_str = ', '.join(f"{r}({c})" for r, c in data['roots'].most_common(5))
            f.write(f"   Top roots: {top_roots_str}\n")
            f.write(f"   Examples: {', '.join(data['examples'][:5])}\n")
            f.write("\n")
        
        # Top roots
        f.write("\n\nTOP 30 ROOTS (All Patterns)\n")
        f.write("-" * 70 + "\n\n")
        
        for root, count in roots_only.most_common(30):
            field = SEMANTIC_FIELDS.get(root, 'Unknown')
            f.write(f"{root:<10} {count:>6}×  {field}\n")
        
        # Best prefix+root combinations
        f.write("\n\nTOP 20 PREFIX+ROOT COMBINATIONS\n")
        f.write("-" * 70 + "\n\n")
        
        for (prefix, root), count in prefix_root_combos.most_common(20):
            pref_func = PREFIX_FUNCTIONS.get(prefix, '?')
            root_field = SEMANTIC_FIELDS.get(root, 'Unknown')
            f.write(f"{prefix}-{root:<12} {count:>5}×  [{pref_func} + {root_field}]\n")
        
        # Best root+suffix combinations
        f.write("\n\nTOP 20 ROOT+SUFFIX COMBINATIONS\n")
        f.write("-" * 70 + "\n\n")
        
        for (root, suffix), count in root_suffix_combos.most_common(20):
            root_field = SEMANTIC_FIELDS.get(root, 'Unknown')
            suff_func = SUFFIX_FUNCTIONS.get(suffix, '?')
            f.write(f"{root}-{suffix:<12} {count:>5}×  [{root_field} + {suff_func}]\n")


def write_json(patterns):
    """
    Write structured JSON output.
    """
    print(f"Writing JSON to {PATTERNS_JSON}...")
    
    output = {
        'metadata': {
            'version': 'SM4-v1',
            'dependencies': 'SM1 (morphology), SM2 (semantic fields)',
            'total_patterns': len(patterns)
        },
        'patterns': []
    }
    
    # Sort by frequency
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for pattern, data in sorted_patterns:
        classification = classify_pattern(pattern, data)
        
        output['patterns'].append({
            'pattern': pattern,
            'count': data['count'],
            'type': data['type'],
            'prefix': data.get('prefix', ''),
            'suffix': data.get('suffix', ''),
            'top_roots': [{'root': r, 'count': c} for r, c in data['roots'].most_common(10)],
            'examples': data['examples'][:10],
            'composition': classification['composition'],
            'interpretation': classification['interpretation'],
            'root_semantic_field': classification['root_field'],
            'confidence': classification['confidence']
        })
    
    with open(PATTERNS_JSON, 'w') as f:
        json.dump(output, f, indent=2)


def write_tsv(patterns):
    """
    Write TSV for further analysis.
    """
    print(f"Writing TSV to {FREQUENCIES_TSV}...")
    
    with open(FREQUENCIES_TSV, 'w') as f:
        f.write("pattern\tcount\ttype\tprefix\tsuffix\ttop_root\troot_field\tinterpretation\tconfidence\n")
        
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for pattern, data in sorted_patterns:
            classification = classify_pattern(pattern, data)
            
            top_root = data['roots'].most_common(1)[0][0] if data['roots'] else ''
            
            f.write(f"{pattern}\t")
            f.write(f"{data['count']}\t")
            f.write(f"{data['type']}\t")
            f.write(f"{data.get('prefix', '')}\t")
            f.write(f"{data.get('suffix', '')}\t")
            f.write(f"{top_root}\t")
            f.write(f"{classification['root_field']}\t")
            f.write(f"{classification['interpretation']}\t")
            f.write(f"{classification['confidence']:.3f}\n")


def main():
    print("=" * 70)
    print("SM4: COMPOSITIONAL PATTERN ANALYZER")
    print("=" * 70)
    print("\nIdentifying PREFIX+ROOT+SUFFIX combinations...")
    print("Using validated SM1 morphemes + SM2 semantic fields\n")
    
    # Load data
    labels = load_zodiac_labels()
    
    if not labels:
        print("\nERROR: No labels loaded. Check transliteration.txt location.")
        return 1
    
    # Analyze patterns
    patterns, roots, prefix_root, root_suffix = analyze_patterns(labels)
    
    # Write outputs
    write_analysis(patterns, roots, prefix_root, root_suffix)
    write_json(patterns)
    write_tsv(patterns)
    
    print("\n" + "=" * 70)
    print("SM4 PATTERN ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  {PATTERNS_JSON}")
    print(f"  {ANALYSIS_TXT}")
    print(f"  {FREQUENCIES_TSV}")
    print(f"\nKey Findings:")
    print(f"  - {len(patterns)} unique morpheme patterns")
    print(f"  - {len(roots)} unique roots")
    print(f"  - Top pattern: {max(patterns.items(), key=lambda x: x[1]['count'])[0]}")
    print("\nReady for SM4 Phase 2: Medieval Parallels")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
