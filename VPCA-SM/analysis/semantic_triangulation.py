#!/usr/bin/env python3
"""
Semantic Triangulation: Cross-Section Root Analysis
===================================================

Uses multiple contexts to constrain root semantics:
  1. Section distribution (herbal/zodiac/bio/recipe)
  2. VPCA semantic fields (from SM2)
  3. Pattern contexts (what prefixes/suffixes appear with root)
  4. Frequency and stability across sections

Output:
  - Probabilistic semantic hypotheses for top 100 roots
  - Confidence scores based on contextual evidence
  - Medieval parallels where applicable

Author: Semantic Triangulation v1, November 27, 2025
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

# Paths
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Outputs
SEMANTIC_JSON = RESULTS_DIR / "semantic_triangulation.json"
SEMANTIC_TXT = RESULTS_DIR / "semantic_triangulation_report.txt"
SEMANTIC_TSV = RESULTS_DIR / "semantic_triangulation_roots.tsv"

# Morphemes
PREFIXES = ['ch', 'ot', 'ok', 'sh', 'qo', 'da', 'yk', 'ol', 'sa', 'op', 'do']
SUFFIXES = ['ey', 'dy', 'in', 'ar', 'al', 'ol', 'os', 'or', 'es', 'oy', 'y', 'e', 'ed', 'om']

# Section definitions
SECTIONS = {
    'Herbal': range(1, 67),
    'Zodiac': range(67, 74),
    'Biological': range(75, 85),
    'Recipes': range(103, 117),
}

# VPCA semantic fields (from SM2)
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

# Functional morphemes (validated)
PREFIX_FUNCTIONS = {
    'ch': 'intensifier',
    'ot': 'transition',
    'ok': 'constituent',
}

SUFFIX_FUNCTIONS = {
    'ey': 'state_marker',
    'dy': 'process_marker',
    'in': 'nominal',
    'ar': 'agent',
    'al': 'quality',
}

# Medieval parallels for common roots
MEDIEVAL_PARALLELS = {
    'ol': 'Latin: -ol- (oil, liquid) / Romance: calor (heat)',
    'al': 'Latin: -al- (quality) / Romance: -al suffix',
    'ar': 'Latin: -ar- (agent) / Romance: -ar suffix',
    'e': 'Latin: et (and) / Romance: e/y (and)',
    'or': 'Latin: -or (agent) / Romance: or/oro (gold/border)',
    'in': 'Latin: in (in/into) / Romance: -in suffix',
    'o': 'Latin: -o (noun ending) / Romance: o/ou',
    'ch': 'Latin: cum (with) / Romance: ch- digraph',
    'eo': 'Latin: -eo (verb) / Greek: -eo',
    'd': 'Latin: de (from/of) / Romance: d-',
}


def load_section_tokens(filepath="transliteration.txt", section_name=None, folio_range=None):
    """Load tokens from specific section."""
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
    """Extract PREFIX + ROOT + SUFFIX."""
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


def analyze_root_contexts(section_data):
    """Analyze root behavior across all contexts."""
    print("\nAnalyzing root contexts across sections...")
    
    root_data = defaultdict(lambda: {
        'total': 0,
        'sections': Counter(),
        'with_prefixes': Counter(),
        'with_suffixes': Counter(),
        'patterns': Counter(),
    })
    
    for section_name, tokens in section_data.items():
        for token in tokens:
            prefix, root, suffix = extract_morphemes(token)
            
            if root:
                root_data[root]['total'] += 1
                root_data[root]['sections'][section_name] += 1
                
                if prefix:
                    root_data[root]['with_prefixes'][prefix] += 1
                if suffix:
                    root_data[root]['with_suffixes'][suffix] += 1
                
                # Pattern
                if prefix and suffix:
                    pattern = f"{prefix}-[{root}]-{suffix}"
                elif prefix:
                    pattern = f"{prefix}-[{root}]"
                elif suffix:
                    pattern = f"[{root}]-{suffix}"
                else:
                    pattern = f"[{root}]"
                
                root_data[root]['patterns'][pattern] += 1
    
    return root_data


def calculate_semantic_hypothesis(root, data):
    """Generate semantic hypothesis based on contextual evidence."""
    
    total = data['total']
    section_dist = data['sections']
    prefixes = data['with_prefixes']
    suffixes = data['with_suffixes']
    
    # Evidence scoring
    evidence = []
    confidence = 0.0
    
    # 1. VPCA semantic field (if known)
    vpca_field = SEMANTIC_FIELDS.get(root)
    if vpca_field:
        evidence.append(f"VPCA: {vpca_field}")
        confidence += 0.3
    
    # 2. Section distribution pattern
    section_spread = len([s for s in section_dist if section_dist[s] > 0])
    if section_spread == 4:
        evidence.append("Universal across all sections")
        confidence += 0.2
    elif section_spread >= 3:
        evidence.append(f"Present in {section_spread}/4 sections")
        confidence += 0.15
    
    # Check for section enrichment
    if total > 0:
        for section in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
            pct = 100 * section_dist[section] / total
            if pct > 50:
                evidence.append(f"Enriched in {section} ({pct:.1f}%)")
                confidence += 0.1
    
    # 3. Prefix associations
    if prefixes:
        top_prefix = prefixes.most_common(1)[0]
        prefix_name = top_prefix[0]
        prefix_pct = 100 * top_prefix[1] / total
        
        if prefix_pct > 30:
            function = PREFIX_FUNCTIONS.get(prefix_name, 'unknown')
            evidence.append(f"Often with {prefix_name}- ({function}, {prefix_pct:.1f}%)")
            if function != 'unknown':
                confidence += 0.15
    
    # 4. Suffix associations  
    if suffixes:
        top_suffix = suffixes.most_common(1)[0]
        suffix_name = top_suffix[0]
        suffix_pct = 100 * top_suffix[1] / total
        
        if suffix_pct > 30:
            function = SUFFIX_FUNCTIONS.get(suffix_name, 'unknown')
            evidence.append(f"Often with -{suffix_name} ({function}, {suffix_pct:.1f}%)")
            if function != 'unknown':
                confidence += 0.15
    
    # 5. Medieval parallel (if known)
    parallel = MEDIEVAL_PARALLELS.get(root)
    if parallel:
        evidence.append(f"Medieval: {parallel}")
        confidence += 0.1
    
    # Generate hypothesis
    hypothesis = generate_hypothesis(root, vpca_field, prefixes, suffixes, section_dist, total)
    
    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)
    
    return {
        'hypothesis': hypothesis,
        'evidence': evidence,
        'confidence': confidence,
    }


def generate_hypothesis(root, vpca_field, prefixes, suffixes, sections, total):
    """Generate semantic hypothesis text."""
    
    # Base on VPCA field
    if vpca_field == 'Modifier/Relation':
        base = "Likely relational/connective element"
        examples = "Similar to 'of', 'with', 'and', 'to'"
    elif vpca_field == 'Quality/State':
        base = "Likely quality or state descriptor"
        examples = "Similar to adjectives or state markers"
    elif vpca_field == 'Process/Active':
        base = "Likely process or action marker"
        examples = "Similar to verbs or process terms"
    elif vpca_field == 'Entity/Object':
        base = "Likely entity or object reference"
        examples = "Similar to nouns or object terms"
    else:
        base = "Semantic role unclear"
        examples = "Insufficient contextual evidence"
    
    # Modify based on prefixes
    if prefixes:
        top_prefix = prefixes.most_common(1)[0][0]
        if top_prefix == 'ch':
            base += ", often intensified"
        elif top_prefix == 'ot':
            base += ", often in transition contexts"
        elif top_prefix == 'ok':
            base += ", often in constituent/unit contexts"
    
    # Modify based on suffixes
    if suffixes:
        top_suffix = suffixes.most_common(1)[0][0]
        if top_suffix in ['ey', 'y']:
            base += ", typically as state"
        elif top_suffix == 'dy':
            base += ", typically as process"
        elif top_suffix == 'in':
            base += ", typically as nominal"
        elif top_suffix == 'ar':
            base += ", typically as agent"
    
    # Add section context
    if sections['Herbal'] > 0.4 * total:
        base += "; common in plant descriptions"
    elif sections['Recipes'] > 0.4 * total:
        base += "; common in recipe instructions"
    elif sections['Biological'] > 0.4 * total:
        base += "; common in biological/anatomical contexts"
    elif sections['Zodiac'] > 0.4 * total:
        base += "; common in cosmological contexts"
    
    return f"{base}. {examples}"


def write_report(root_data, top_n=100):
    """Write human-readable semantic triangulation report."""
    print(f"\nWriting report to {SEMANTIC_TXT}...")
    
    # Sort by frequency
    sorted_roots = sorted(root_data.items(), key=lambda x: x[1]['total'], reverse=True)
    
    with open(SEMANTIC_TXT, 'w') as f:
        f.write("SEMANTIC TRIANGULATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write("Cross-section root analysis with probabilistic semantic hypotheses\n\n")
        f.write(f"Analyzing top {top_n} roots by frequency\n")
        f.write(f"Coverage: ~{sum(d['total'] for _, d in sorted_roots[:top_n])} tokens\n\n")
        
        f.write("=" * 70 + "\n\n")
        
        for i, (root, data) in enumerate(sorted_roots[:top_n], 1):
            hypothesis = calculate_semantic_hypothesis(root, data)
            
            f.write(f"{i}. ROOT: '{root}'\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total occurrences: {data['total']}\n")
            f.write(f"Confidence: {hypothesis['confidence']:.2f}\n\n")
            
            # Section distribution
            f.write("Section distribution:\n")
            for section in ['Herbal', 'Zodiac', 'Biological', 'Recipes']:
                count = data['sections'][section]
                pct = 100 * count / data['total'] if data['total'] > 0 else 0
                f.write(f"  {section:<12} {count:>6} ({pct:>5.1f}%)\n")
            f.write("\n")
            
            # Top patterns
            f.write("Top patterns:\n")
            for pattern, count in data['patterns'].most_common(5):
                f.write(f"  {pattern:<30} {count:>5}×\n")
            f.write("\n")
            
            # Hypothesis
            f.write("SEMANTIC HYPOTHESIS:\n")
            f.write(f"{hypothesis['hypothesis']}\n\n")
            
            # Evidence
            if hypothesis['evidence']:
                f.write("Supporting evidence:\n")
                for ev in hypothesis['evidence']:
                    f.write(f"  • {ev}\n")
            
            f.write("\n" + "=" * 70 + "\n\n")


def write_json(root_data, top_n=100):
    """Write structured JSON output."""
    print(f"Writing JSON to {SEMANTIC_JSON}...")
    
    sorted_roots = sorted(root_data.items(), key=lambda x: x[1]['total'], reverse=True)
    
    output = {
        'metadata': {
            'version': 'SemanticTriangulation-v1',
            'total_roots_analyzed': len(root_data),
            'top_n': top_n,
        },
        'roots': []
    }
    
    for root, data in sorted_roots[:top_n]:
        hypothesis = calculate_semantic_hypothesis(root, data)
        
        output['roots'].append({
            'root': root,
            'total_occurrences': data['total'],
            'sections': dict(data['sections']),
            'top_prefixes': [{'prefix': p, 'count': c} for p, c in data['with_prefixes'].most_common(5)],
            'top_suffixes': [{'suffix': s, 'count': c} for s, c in data['with_suffixes'].most_common(5)],
            'top_patterns': [{'pattern': p, 'count': c} for p, c in data['patterns'].most_common(10)],
            'hypothesis': hypothesis['hypothesis'],
            'evidence': hypothesis['evidence'],
            'confidence': hypothesis['confidence'],
        })
    
    with open(SEMANTIC_JSON, 'w') as f:
        json.dump(output, f, indent=2)


def write_tsv(root_data, top_n=100):
    """Write TSV for spreadsheet analysis."""
    print(f"Writing TSV to {SEMANTIC_TSV}...")
    
    sorted_roots = sorted(root_data.items(), key=lambda x: x[1]['total'], reverse=True)
    
    with open(SEMANTIC_TSV, 'w') as f:
        f.write("root\ttotal\therbal\tzodiac\tbiological\trecipes\tvpca_field\tconfidence\thypothesis\n")
        
        for root, data in sorted_roots[:top_n]:
            hypothesis = calculate_semantic_hypothesis(root, data)
            
            vpca = SEMANTIC_FIELDS.get(root, 'Unknown')
            
            f.write(f"{root}\t")
            f.write(f"{data['total']}\t")
            f.write(f"{data['sections']['Herbal']}\t")
            f.write(f"{data['sections']['Zodiac']}\t")
            f.write(f"{data['sections']['Biological']}\t")
            f.write(f"{data['sections']['Recipes']}\t")
            f.write(f"{vpca}\t")
            f.write(f"{hypothesis['confidence']:.3f}\t")
            f.write(f"{hypothesis['hypothesis']}\n")


def main():
    print("=" * 70)
    print("SEMANTIC TRIANGULATION: ROOT ANALYSIS")
    print("=" * 70)
    print("\nInferring root semantics from cross-section contexts...\n")
    
    # Load all sections
    print("Loading manuscript sections...")
    section_data = {}
    
    for section_name, folio_range in SECTIONS.items():
        tokens = load_section_tokens(
            filepath="transliteration.txt",
            section_name=section_name,
            folio_range=folio_range
        )
        print(f"  {section_name}: {len(tokens)} tokens")
        section_data[section_name] = tokens
    
    total_tokens = sum(len(tokens) for tokens in section_data.values())
    print(f"\nTotal tokens: {total_tokens:,}")
    
    # Analyze roots
    root_data = analyze_root_contexts(section_data)
    
    print(f"\nFound {len(root_data)} unique roots")
    
    # Generate reports
    write_report(root_data, top_n=100)
    write_json(root_data, top_n=100)
    write_tsv(root_data, top_n=100)
    
    print("\n" + "=" * 70)
    print("SEMANTIC TRIANGULATION COMPLETE")
    print("=" * 70)
    
    # Summary statistics
    sorted_roots = sorted(root_data.items(), key=lambda x: x[1]['total'], reverse=True)
    
    top_100_coverage = sum(d['total'] for _, d in sorted_roots[:100])
    coverage_pct = 100 * top_100_coverage / total_tokens
    
    print(f"\nTop 100 roots cover: {top_100_coverage:,} tokens ({coverage_pct:.1f}%)")
    
    # Confidence distribution
    high_conf = sum(1 for r, d in sorted_roots[:100] 
                   if calculate_semantic_hypothesis(r, d)['confidence'] >= 0.7)
    medium_conf = sum(1 for r, d in sorted_roots[:100] 
                     if 0.5 <= calculate_semantic_hypothesis(r, d)['confidence'] < 0.7)
    low_conf = sum(1 for r, d in sorted_roots[:100] 
                   if calculate_semantic_hypothesis(r, d)['confidence'] < 0.5)
    
    print(f"\nConfidence distribution (top 100):")
    print(f"  High (≥70%):     {high_conf} roots")
    print(f"  Medium (50-70%): {medium_conf} roots")
    print(f"  Low (<50%):      {low_conf} roots")
    
    print("\n✅ Semantic hypotheses generated for top 100 roots!")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
