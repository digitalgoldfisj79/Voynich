#!/usr/bin/env python3
"""
SM4: Root Semantic Triangulation
================================

Uses cross-section contexts to constrain root meanings.

Method:
1. Map each root across ALL sections
2. Identify distributional patterns
3. Apply VPCA semantic field assignments
4. Check common morpheme patterns
5. Generate probabilistic semantic hypotheses

Output:
  - Root semantic profiles
  - Cross-context consistency scores
  - Probabilistic meaning assignments

Author: SM4 Semantic Triangulation, November 27, 2025
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

# Paths
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Outputs
SEMANTICS_JSON = RESULTS_DIR / "sm4_root_semantics.json"
SEMANTICS_TXT = RESULTS_DIR / "sm4_root_semantic_analysis.txt"
SEMANTICS_TSV = RESULTS_DIR / "sm4_root_semantic_profiles.tsv"

# From SM1/SM2 - validated morphemes and semantic fields
PREFIXES = ['ch', 'ot', 'ok', 'sh', 'qo', 'da', 'yk', 'ol', 'sa', 'op', 'do']
SUFFIXES = ['ey', 'dy', 'in', 'ar', 'al', 'ol', 'os', 'or', 'es', 'oy', 'y', 'e', 'ed', 'om']

# From SM2 - VPCA semantic fields
SEMANTIC_FIELDS = {
    'e': ('Modifier/Relation', 0.85),
    'ee': ('Modifier/Relation', 0.80),
    'k': ('Modifier/Relation', 0.75),
    'ol': ('Quality/State', 0.85),
    'al': ('Quality/State', 0.85),
    'l': ('Quality/State', 0.80),
    'eo': ('Quality/State', 0.75),
    'o': ('Quality/State', 0.70),
    'ar': ('Quality/State', 0.70),
    'i': ('Process/Active', 0.75),
    'ir': ('Process/Active', 0.75),
    'ot': ('Process/Active', 0.70),
    'ch': ('Entity/Object', 0.75),
}

# Functional morpheme hypotheses
PREFIX_FUNCTIONS = {
    'ch': ('intensifier', 0.95),
    'ot': ('transition', 0.95),
    'ok': ('constituent', 0.85),
    'qo': ('biological_process?', 0.50),
    'da': ('root/base?', 0.40),
    'sh': ('unknown', 0.30),
}

SUFFIX_FUNCTIONS = {
    'ey': ('state_marker', 0.95),
    'dy': ('process_marker', 0.95),
    'in': ('nominal', 0.90),
    'ar': ('agent/doer', 0.80),
    'al': ('quality', 0.80),
    'y': ('state', 0.75),
}

# Section definitions
SECTIONS = {
    'Herbal': range(1, 67),
    'Zodiac': range(67, 74),
    'Biological': range(75, 85),
    'Recipes': range(103, 117),
}


def load_section_tokens(filepath="transliteration.txt", section_name=None, folio_range=None):
    """Load tokens from specific manuscript section."""
    tokens = []
    current_folio = None
    
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('<f') and '>' in line and '.' not in line.split('>')[0]:
                    folio_match = re.match(r'<f(\d+)[rv]\d*>', line)
                    if folio_match:
                        current_folio = int(folio_match.group(1))
                    continue
                
                if current_folio and current_folio in folio_range:
                    if line.startswith('<') and '>' in line:
                        parts = line.split('>', 1)
                        if len(parts) == 2:
                            text = parts[1].strip()
                            token_list = re.split(r'[.\s]+', text)
                            
                            for token in token_list:
                                token = re.sub(r'[{}\[\]@,;:!?\d\'"-]', '', token)
                                token = token.strip()
                                
                                if token and len(token) > 1 and token.isalpha():
                                    tokens.append(token)
        
        return tokens
        
    except FileNotFoundError:
        return []


def extract_morphemes(token):
    """Extract PREFIX + ROOT + SUFFIX from token."""
    for prefix in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            remainder = token[len(prefix):]
            
            for suffix in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(suffix):
                    root = remainder[:-len(suffix)] if suffix else remainder
                    if root:
                        return (prefix, root, suffix)
            
            if remainder:
                return (prefix, remainder, '')
    
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(suffix):
            root = token[:-len(suffix)] if suffix else token
            if root and len(root) > 1:
                return ('', root, suffix)
    
    return ('', token, '')


def build_root_profiles(section_data):
    """Build comprehensive profiles for all roots."""
    print("\nBuilding root semantic profiles...")
    
    root_profiles = defaultdict(lambda: {
        'total': 0,
        'by_section': Counter(),
        'with_prefixes': Counter(),
        'with_suffixes': Counter(),
        'patterns': Counter(),
        'tokens': set(),
    })
    
    for section_name, tokens in section_data.items():
        for token in tokens:
            prefix, root, suffix = extract_morphemes(token)
            
            if root:
                profile = root_profiles[root]
                profile['total'] += 1
                profile['by_section'][section_name] += 1
                profile['tokens'].add(token)
                
                if prefix:
                    profile['with_prefixes'][prefix] += 1
                if suffix:
                    profile['with_suffixes'][suffix] += 1
                
                # Store pattern
                if prefix and suffix:
                    pattern = f"{prefix}-[]-{suffix}"
                elif prefix:
                    pattern = f"{prefix}-[]"
                elif suffix:
                    pattern = f"[]-{suffix}"
                else:
                    pattern = "[]"
                
                profile['patterns'][pattern] += 1
    
    return root_profiles


def analyze_root_semantics(root, profile):
    """Analyze semantic profile of a root."""
    total = profile['total']
    
    # Section distribution
    section_dist = {}
    for section in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
        count = profile['by_section'][section]
        section_dist[section] = {
            'count': count,
            'percentage': 100 * count / total if total > 0 else 0
        }
    
    # Check for section enrichment
    avg_pct = 25.0  # Equal distribution
    enriched_sections = []
    for section, data in section_dist.items():
        if data['percentage'] > avg_pct * 1.5:  # 50% above average
            enriched_sections.append(section)
    
    # VPCA semantic field (if known)
    vpca_field = None
    vpca_confidence = 0.0
    if root in SEMANTIC_FIELDS:
        vpca_field, vpca_confidence = SEMANTIC_FIELDS[root]
    
    # Common prefixes/suffixes
    top_prefixes = profile['with_prefixes'].most_common(3)
    top_suffixes = profile['with_suffixes'].most_common(3)
    
    # Common patterns
    top_patterns = profile['patterns'].most_common(5)
    
    # Semantic hypothesis based on patterns
    hypothesis = generate_hypothesis(
        root, vpca_field, top_prefixes, top_suffixes, 
        enriched_sections, section_dist
    )
    
    return {
        'total_occurrences': total,
        'section_distribution': section_dist,
        'enriched_sections': enriched_sections,
        'vpca_field': vpca_field,
        'vpca_confidence': vpca_confidence,
        'top_prefixes': [(p, c) for p, c in top_prefixes],
        'top_suffixes': [(s, c) for s, c in top_suffixes],
        'top_patterns': [(pat, c) for pat, c in top_patterns],
        'semantic_hypothesis': hypothesis,
        'example_tokens': list(profile['tokens'])[:10],
    }


def generate_hypothesis(root, vpca_field, top_prefixes, top_suffixes, 
                       enriched_sections, section_dist):
    """Generate semantic hypothesis based on distributional evidence."""
    hypotheses = []
    confidence_scores = []
    
    # Hypothesis 1: VPCA field (if available)
    if vpca_field:
        hypotheses.append(f"VPCA: {vpca_field}")
        confidence_scores.append(0.80)
    
    # Hypothesis 2: Section enrichment
    if enriched_sections:
        section_hints = {
            'Herbal': 'plant-related',
            'Zodiac': 'cosmological/seasonal',
            'Biological': 'anatomical/process',
            'Recipes': 'procedural/ingredient',
        }
        
        for section in enriched_sections:
            hint = section_hints.get(section, 'unknown')
            hypotheses.append(f"Enriched in {section}: likely {hint}")
            confidence_scores.append(0.60)
    
    # Hypothesis 3: Prefix associations
    if top_prefixes:
        prefix, count = top_prefixes[0]
        if prefix in PREFIX_FUNCTIONS:
            func, conf = PREFIX_FUNCTIONS[prefix]
            pct = 100 * count / sum(c for _, c in top_prefixes)
            if pct > 40:  # Strongly associated
                hypotheses.append(f"Often with {prefix}- ({func}): {pct:.0f}%")
                confidence_scores.append(conf * 0.7)
    
    # Hypothesis 4: Suffix associations
    if top_suffixes:
        suffix, count = top_suffixes[0]
        if suffix in SUFFIX_FUNCTIONS:
            func, conf = SUFFIX_FUNCTIONS[suffix]
            pct = 100 * count / sum(c for _, c in top_suffixes)
            if pct > 40:  # Strongly associated
                hypotheses.append(f"Often with -{suffix} ({func}): {pct:.0f}%")
                confidence_scores.append(conf * 0.7)
    
    # Hypothesis 5: Root length heuristic
    if len(root) == 1:
        hypotheses.append("Single letter: likely grammatical/relational")
        confidence_scores.append(0.50)
    elif len(root) >= 3:
        hypotheses.append("Multi-letter: likely content word")
        confidence_scores.append(0.50)
    
    # Synthesize
    if not hypotheses:
        return {
            'primary': 'Unknown - insufficient evidence',
            'confidence': 0.0,
            'supporting': []
        }
    
    # Primary hypothesis = highest confidence
    max_idx = confidence_scores.index(max(confidence_scores))
    
    return {
        'primary': hypotheses[max_idx],
        'confidence': confidence_scores[max_idx],
        'supporting': [h for i, h in enumerate(hypotheses) if i != max_idx]
    }


def write_analysis(root_analyses):
    """Write human-readable analysis."""
    print(f"\nWriting analysis to {SEMANTICS_TXT}...")
    
    with open(SEMANTICS_TXT, 'w') as f:
        f.write("SM4: ROOT SEMANTIC TRIANGULATION\n")
        f.write("=" * 70 + "\n\n")
        f.write("Using cross-section contexts to constrain root meanings\n")
        f.write(f"Analyzed: {len(root_analyses)} unique roots\n\n")
        
        # Sort by total frequency
        sorted_roots = sorted(
            root_analyses.items(),
            key=lambda x: x[1]['total_occurrences'],
            reverse=True
        )
        
        f.write("TOP 50 ROOTS WITH SEMANTIC ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        
        for i, (root, analysis) in enumerate(sorted_roots[:50], 1):
            f.write(f"{i}. ROOT: '{root}' ({analysis['total_occurrences']}× manuscript-wide)\n")
            f.write("-" * 70 + "\n")
            
            # Section distribution
            f.write("  Section distribution:\n")
            for section in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
                data = analysis['section_distribution'][section]
                enriched = " ⬆️" if section in analysis['enriched_sections'] else ""
                f.write(f"    {section:<12} {data['count']:>6}× ({data['percentage']:>5.1f}%){enriched}\n")
            
            # VPCA field
            if analysis['vpca_field']:
                f.write(f"\n  VPCA field: {analysis['vpca_field']} "
                       f"(confidence: {analysis['vpca_confidence']:.0%})\n")
            
            # Top patterns
            f.write(f"\n  Top morpheme patterns:\n")
            for pattern, count in analysis['top_patterns'][:3]:
                f.write(f"    {pattern:<20} {count:>6}×\n")
            
            # Prefixes/suffixes
            if analysis['top_prefixes']:
                f.write(f"\n  Common prefixes: ")
                f.write(", ".join(f"{p} ({c}×)" for p, c in analysis['top_prefixes'][:3]))
                f.write("\n")
            
            if analysis['top_suffixes']:
                f.write(f"  Common suffixes: ")
                f.write(", ".join(f"{s} ({c}×)" for s, c in analysis['top_suffixes'][:3]))
                f.write("\n")
            
            # Semantic hypothesis
            hyp = analysis['semantic_hypothesis']
            f.write(f"\n  SEMANTIC HYPOTHESIS:\n")
            f.write(f"    Primary: {hyp['primary']}\n")
            f.write(f"    Confidence: {hyp['confidence']:.0%}\n")
            
            if hyp['supporting']:
                f.write(f"    Supporting evidence:\n")
                for sup in hyp['supporting'][:3]:
                    f.write(f"      • {sup}\n")
            
            # Examples
            f.write(f"\n  Example tokens: ")
            f.write(", ".join(analysis['example_tokens'][:8]))
            f.write("\n\n")


def write_json(root_analyses):
    """Write JSON output."""
    print(f"Writing JSON to {SEMANTICS_JSON}...")
    
    output = {
        'metadata': {
            'version': 'SM4-Semantics-v1',
            'total_roots': len(root_analyses),
        },
        'roots': {}
    }
    
    for root, analysis in root_analyses.items():
        output['roots'][root] = analysis
    
    with open(SEMANTICS_JSON, 'w') as f:
        json.dump(output, f, indent=2)


def write_tsv(root_analyses):
    """Write TSV for spreadsheet analysis."""
    print(f"Writing TSV to {SEMANTICS_TSV}...")
    
    sorted_roots = sorted(
        root_analyses.items(),
        key=lambda x: x[1]['total_occurrences'],
        reverse=True
    )
    
    with open(SEMANTICS_TSV, 'w') as f:
        f.write("root\ttotal\therbal\tzodiac\tbiological\trecipes\t"
               "vpca_field\tconfidence\thypothesis\tenriched_sections\n")
        
        for root, analysis in sorted_roots:
            dist = analysis['section_distribution']
            hyp = analysis['semantic_hypothesis']
            
            f.write(f"{root}\t")
            f.write(f"{analysis['total_occurrences']}\t")
            f.write(f"{dist['Herbal']['count']}\t")
            f.write(f"{dist['Zodiac']['count']}\t")
            f.write(f"{dist['Biological']['count']}\t")
            f.write(f"{dist['Recipes']['count']}\t")
            f.write(f"{analysis['vpca_field'] or 'unknown'}\t")
            f.write(f"{hyp['confidence']:.3f}\t")
            f.write(f"{hyp['primary']}\t")
            f.write(f"{','.join(analysis['enriched_sections'])}\n")


def main():
    print("=" * 70)
    print("SM4: ROOT SEMANTIC TRIANGULATION")
    print("=" * 70)
    print("\nUsing cross-section contexts to constrain root meanings...\n")
    
    # Load all sections
    section_data = {}
    for section_name, folio_range in SECTIONS.items():
        print(f"Loading {section_name}...")
        tokens = load_section_tokens(
            filepath="transliteration.txt",
            section_name=section_name,
            folio_range=folio_range
        )
        if tokens:
            section_data[section_name] = tokens
            print(f"  {len(tokens)} tokens")
    
    if not section_data:
        print("\nERROR: No sections loaded.")
        return 1
    
    # Build root profiles
    root_profiles = build_root_profiles(section_data)
    print(f"Found {len(root_profiles)} unique roots")
    
    # Analyze semantics for top roots
    root_analyses = {}
    for root, profile in root_profiles.items():
        if profile['total'] >= 10:  # Minimum 10 occurrences
            root_analyses[root] = analyze_root_semantics(root, profile)
    
    print(f"Analyzed {len(root_analyses)} roots (≥10 occurrences)")
    
    # Write outputs
    write_analysis(root_analyses)
    write_json(root_analyses)
    write_tsv(root_analyses)
    
    print("\n" + "=" * 70)
    print("SEMANTIC TRIANGULATION COMPLETE")
    print("=" * 70)
    
    # Summary statistics
    high_conf = sum(1 for a in root_analyses.values() 
                   if a['semantic_hypothesis']['confidence'] >= 0.70)
    med_conf = sum(1 for a in root_analyses.values() 
                  if 0.50 <= a['semantic_hypothesis']['confidence'] < 0.70)
    
    print(f"\nSemantic Hypotheses Generated:")
    print(f"  High confidence (≥70%): {high_conf} roots")
    print(f"  Medium confidence (50-69%): {med_conf} roots")
    print(f"  Total analyzed: {len(root_analyses)} roots")
    
    # Coverage estimate
    total_tokens = sum(len(tokens) for tokens in section_data.values())
    covered_tokens = sum(a['total_occurrences'] for a in root_analyses.values())
    coverage = 100 * covered_tokens / total_tokens
    
    print(f"\nManuscript Coverage:")
    print(f"  Analyzed roots cover: {coverage:.1f}% of manuscript")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
