#!/usr/bin/env python3
"""
VPCA-SM2: Root & Affix Role Classification
==========================================

Classifies stems and suffixes into semantic role families based on behavior.

Key Principle:
  We classify morphemes by HOW they behave (role class),
  not WHAT they mean (lexical semantics).
  
Example:
  ✓ CORRECT: "chol → R3 (peak-state ingredient-like)"
  ✗ INCORRECT: "chol → 'herb' or 'plant'"

Input:
  - data/vpca2_all_tokens.tsv (VPCA classifications)
  - data/ea_root_vpca_summary.tsv (root polarity patterns)
  - ../Phase69/out/p69_rules_final.json (morphological rules from repo)

Output:
  - results/sm2_root_classes.tsv (root classifications)
  - results/sm2_affix_classes.tsv (affix classifications)
  - results/sm2_role_lexicon.json (complete role lexicon)
  - results/sm2_classification_report.txt (evidence summary)

Classification Scheme:
  ROOT CLASSES:
    R1: Ingredient-like (V-heavy, Herbal/Pharma dominant)
    R2: Process-like (C-heavy, Recipes/Pharma dominant)
    R3: State-like (A-heavy, descriptive contexts)
    R4: Neutral (P-heavy, distributed across sections)
    
  AFFIX CLASSES:
    S1: Transformation suffixes (OT-family: -ot, -oty, -otol, etc.)
    S2: State suffixes (-dy, -ain, -al, -or)
    S3: Intensifier suffixes
    P1: Valley-inducing prefixes (ch-, d-, etc.)
    P2: Peak-inducing prefixes
    P3: Neutral prefixes
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import re

# Data paths
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Input files
VPCA_TOKENS = DATA_DIR / "vpca2_all_tokens.tsv"
ROOT_VPCA = DATA_DIR / "ea_root_vpca_summary.tsv"
P69_RULES = Path("../Phase69/out/p69_rules_final.json")

# Output files
ROOT_CLASSES = RESULTS_DIR / "sm2_root_classes.tsv"
AFFIX_CLASSES = RESULTS_DIR / "sm2_affix_classes.tsv"
ROLE_LEXICON = RESULTS_DIR / "sm2_role_lexicon.json"
CLASSIFICATION_REPORT = RESULTS_DIR / "sm2_classification_report.txt"


def load_vpca_tokens():
    """Load complete VPCA token classifications"""
    tokens = []
    with open(VPCA_TOKENS) as f:
        header = f.readline().strip().split('\t')
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 9:
                tokens.append({
                    'token': parts[0],
                    'folio': parts[1],
                    'section': parts[4],
                    'left_score': float(parts[5]) if parts[5] != '' else 0.0,
                    'right_score': float(parts[6]) if parts[6] != '' else 0.0,
                    'pred_side': parts[7],
                    'VPCA2': parts[8]
                })
    return tokens


def load_p69_rules():
    """Load p69 morphological rules"""
    try:
        with open(P69_RULES) as f:
            data = json.load(f)
            if 'rules' in data:
                return data['rules']
            return data
    except FileNotFoundError:
        print(f"⚠️  p69 rules not found at {P69_RULES}, will use basic morpheme extraction")
        return []


def extract_morphemes(token):
    """
    Basic morpheme extraction
    Returns (prefix, core, suffix)
    """
    # Common prefixes
    prefixes = ['qok', 'sh', 'ch', 'ck', 'kch', 'dch', 'ych', 'ol', 'd', 'k', 's', 'l', 'r', 'y', 't', 'p', 'f']
    
    # Common suffixes (including OT family)
    suffixes = [
        'otchy', 'otchor', 'otol', 'oty', 'ot',  # OT family
        'aiin', 'ain', 'iin', 'eey', 'ey', 'dy', 'edy', 'ody',  # -ain/-dy families
        'al', 'ol', 'ar', 'or', 'am',  # liquid finals
        'che', 'he', 'ee', 'e',  # e-finals
        'chy', 'hy', 'y',  # y-finals
        'ch', 'h', 'k', 'd', 'l', 'm', 'n', 'r', 's', 't'  # single consonants
    ]
    
    # Sort by length (longest first for greedy matching)
    prefixes.sort(key=len, reverse=True)
    suffixes.sort(key=len, reverse=True)
    
    token_lower = token.lower()
    prefix = ""
    suffix = ""
    core = token_lower
    
    # Extract prefix
    for p in prefixes:
        if token_lower.startswith(p) and len(token_lower) > len(p):
            prefix = p
            core = token_lower[len(p):]
            break
    
    # Extract suffix
    for s in suffixes:
        if core.endswith(s) and len(core) > len(s):
            suffix = s
            core = core[:-len(s)]
            break
    
    return (prefix, core, suffix)


def analyze_roots(tokens):
    """
    Analyze root behavior across sections and VPCA states
    """
    root_stats = defaultdict(lambda: {
        'total': 0,
        'V': 0, 'P': 0, 'C': 0, 'A': 0,
        'sections': Counter(),
        'tokens': []
    })
    
    for token_data in tokens:
        token = token_data['token']
        vpca = token_data['VPCA2']
        section = token_data['section']
        
        # Extract morphemes
        prefix, core, suffix = extract_morphemes(token)
        
        if len(core) >= 1:  # Valid root
            root_stats[core]['total'] += 1
            root_stats[core][vpca] += 1
            root_stats[core]['sections'][section] += 1
            root_stats[core]['tokens'].append(token)
    
    return root_stats


def analyze_affixes(tokens):
    """
    Analyze prefix and suffix behavior
    """
    prefix_stats = defaultdict(lambda: {
        'total': 0,
        'V': 0, 'P': 0, 'C': 0, 'A': 0,
        'sections': Counter(),
        'left_score': [],
        'right_score': []
    })
    
    suffix_stats = defaultdict(lambda: {
        'total': 0,
        'V': 0, 'P': 0, 'C': 0, 'A': 0,
        'sections': Counter(),
        'tokens': []
    })
    
    for token_data in tokens:
        token = token_data['token']
        vpca = token_data['VPCA2']
        section = token_data['section']
        left_score = token_data['left_score']
        right_score = token_data['right_score']
        
        prefix, core, suffix = extract_morphemes(token)
        
        if prefix:
            prefix_stats[prefix]['total'] += 1
            prefix_stats[prefix][vpca] += 1
            prefix_stats[prefix]['sections'][section] += 1
            prefix_stats[prefix]['left_score'].append(left_score)
            prefix_stats[prefix]['right_score'].append(right_score)
        
        if suffix:
            suffix_stats[suffix]['total'] += 1
            suffix_stats[suffix][vpca] += 1
            suffix_stats[suffix]['sections'][section] += 1
            suffix_stats[suffix]['tokens'].append(token)
    
    return prefix_stats, suffix_stats


def classify_root(root, stats, min_freq=10):
    """
    Classify root into role family based on behavior
    
    Returns: (class, confidence, evidence)
    """
    if stats['total'] < min_freq:
        return ('RARE', 'Low', ['Insufficient frequency for classification'])
    
    total = stats['total']
    v_ratio = stats['V'] / total if total > 0 else 0
    p_ratio = stats['P'] / total if total > 0 else 0
    c_ratio = stats['C'] / total if total > 0 else 0
    
    # Get dominant sections
    top_sections = stats['sections'].most_common(3)
    section_list = [s[0] for s in top_sections]
    
    evidence = [
        f"Total: {total} tokens",
        f"VPCA: V={stats['V']} ({v_ratio:.1%}), P={stats['P']} ({p_ratio:.1%}), C={stats['C']} ({c_ratio:.1%})",
        f"Top sections: {', '.join(section_list)}"
    ]
    
    # Classification logic
    # R1: Ingredient-like (V-heavy, Herbal/Pharma)
    if v_ratio > 0.4 and ('Herbal' in section_list or 'Pharmaceutical' in section_list):
        return ('R1', 'High', evidence + ['V-heavy, ingredient contexts'])
    
    # R2: Process-like (C-heavy, Recipes/Pharma)
    if c_ratio > 0.05 and 'Recipes' in section_list:
        return ('R2', 'Medium', evidence + ['C-present, recipe contexts'])
    
    # R3: State-like (descriptive, distributed)
    if p_ratio > 0.6 and len(section_list) >= 3:
        return ('R3', 'Medium', evidence + ['P-heavy, distributed'])
    
    # R4: Neutral (default)
    return ('R4', 'Low', evidence + ['Neutral behavior'])


def classify_suffix(suffix, stats, min_freq=5):
    """
    Classify suffix into role family
    
    Returns: (class, confidence, evidence)
    """
    if stats['total'] < min_freq:
        return ('RARE', 'Low', ['Insufficient frequency'])
    
    total = stats['total']
    c_ratio = stats['C'] / total if total > 0 else 0
    v_ratio = stats['V'] / total if total > 0 else 0
    
    evidence = [
        f"Total: {total} tokens",
        f"VPCA: V={stats['V']} ({v_ratio:.1%}), C={stats['C']} ({c_ratio:.1%})"
    ]
    
    # S1: OT-family (transformation markers)
    if re.match(r'^ot(chy|chor|ol|y)?$', suffix):
        return ('S1', 'High', evidence + ['OT-family transformation marker'])
    
    # S2: State suffixes
    if suffix in ['dy', 'edy', 'ody', 'ain', 'aiin', 'iin', 'al', 'or']:
        if c_ratio > 0.02:
            return ('S2', 'Medium', evidence + ['State/result marker with C-association'])
        else:
            return ('S2', 'Low', evidence + ['State marker, low C-association'])
    
    # S3: Intensifiers (e-finals, -ee)
    if suffix in ['e', 'ee', 'ey', 'eey', 'che', 'he']:
        return ('S3', 'Medium', evidence + ['Potential intensifier/modifier'])
    
    return ('S0', 'Low', evidence + ['Unclassified suffix'])


def classify_prefix(prefix, stats, min_freq=5):
    """
    Classify prefix into role family
    
    Returns: (class, confidence, evidence)
    """
    if stats['total'] < min_freq:
        return ('RARE', 'Low', ['Insufficient frequency'])
    
    total = stats['total']
    
    # Calculate average scores
    avg_left = sum(stats['left_score']) / len(stats['left_score']) if stats['left_score'] else 0
    avg_right = sum(stats['right_score']) / len(stats['right_score']) if stats['right_score'] else 0
    
    evidence = [
        f"Total: {total} tokens",
        f"Avg left score: {avg_left:.1f}",
        f"Avg right score: {avg_right:.1f}"
    ]
    
    # P1: Valley-inducing (left-biased)
    if avg_left > avg_right + 10:
        return ('P1', 'High', evidence + ['Strong left/Valley bias'])
    
    # P2: Peak-inducing (right-biased)
    if avg_right > avg_left + 10:
        return ('P2', 'High', evidence + ['Strong right/Peak bias'])
    
    # P3: Neutral
    return ('P3', 'Medium', evidence + ['Neutral or weak bias'])


def generate_role_lexicon(root_classes, prefix_classes, suffix_classes):
    """
    Generate complete role lexicon with all classifications
    """
    lexicon = {
        'roots': {},
        'prefixes': {},
        'suffixes': {},
        'statistics': {
            'total_roots': len(root_classes),
            'total_prefixes': len(prefix_classes),
            'total_suffixes': len(suffix_classes)
        },
        'class_descriptions': {
            'R1': 'Ingredient-like (V-heavy, Herbal/Pharma)',
            'R2': 'Process-like (C-heavy, Recipes)',
            'R3': 'State-like (P-heavy, distributed)',
            'R4': 'Neutral',
            'S1': 'Transformation markers (OT-family)',
            'S2': 'State/result markers',
            'S3': 'Intensifiers/modifiers',
            'P1': 'Valley-inducing prefixes',
            'P2': 'Peak-inducing prefixes',
            'P3': 'Neutral prefixes'
        }
    }
    
    for root, (cls, conf, evid) in root_classes.items():
        lexicon['roots'][root] = {
            'class': cls,
            'confidence': conf,
            'evidence': evid
        }
    
    for prefix, (cls, conf, evid) in prefix_classes.items():
        lexicon['prefixes'][prefix] = {
            'class': cls,
            'confidence': conf,
            'evidence': evid
        }
    
    for suffix, (cls, conf, evid) in suffix_classes.items():
        lexicon['suffixes'][suffix] = {
            'class': cls,
            'confidence': conf,
            'evidence': evid
        }
    
    return lexicon


def generate_report(lexicon, root_stats, prefix_stats, suffix_stats):
    """
    Generate human-readable classification report
    """
    output = []
    output.append("="*80)
    output.append("VPCA-SM2: ROOT & AFFIX ROLE CLASSIFICATION")
    output.append("="*80)
    output.append("")
    output.append("Classifies morphemes by behavioral patterns, not lexical meanings.")
    output.append("")
    
    # Summary statistics
    output.append("="*80)
    output.append("SUMMARY STATISTICS")
    output.append("="*80)
    output.append(f"  Total roots analyzed: {len(root_stats)}")
    output.append(f"  Total prefixes analyzed: {len(prefix_stats)}")
    output.append(f"  Total suffixes analyzed: {len(suffix_stats)}")
    output.append("")
    
    # Class distribution
    root_class_dist = Counter()
    for root, data in lexicon['roots'].items():
        root_class_dist[data['class']] += 1
    
    output.append("ROOT CLASS DISTRIBUTION:")
    for cls in sorted(root_class_dist.keys()):
        count = root_class_dist[cls]
        desc = lexicon['class_descriptions'].get(cls, 'Unknown')
        output.append(f"  {cls}: {count} roots - {desc}")
    output.append("")
    
    # Top examples per class
    output.append("="*80)
    output.append("TOP EXAMPLES BY CLASS")
    output.append("="*80)
    output.append("")
    
    for cls in ['R1', 'R2', 'R3', 'R4']:
        output.append(f"\n{cls} - {lexicon['class_descriptions'].get(cls, '')}")
        output.append("-"*80)
        
        examples = [(root, data) for root, data in lexicon['roots'].items() 
                   if data['class'] == cls and data['confidence'] in ['High', 'Medium']]
        
        # Sort by frequency (extract from evidence)
        examples_sorted = []
        for root, data in examples:
            freq = 0
            for evid in data['evidence']:
                if evid.startswith('Total:'):
                    freq = int(evid.split()[1])
                    break
            examples_sorted.append((root, data, freq))
        
        examples_sorted.sort(key=lambda x: x[2], reverse=True)
        
        for root, data, freq in examples_sorted[:10]:  # Top 10
            output.append(f"  {root:15s} (freq={freq}, conf={data['confidence']})")
            for evid in data['evidence'][:2]:  # First 2 evidence items
                output.append(f"    • {evid}")
    
    # Suffix classes
    output.append("\n\n" + "="*80)
    output.append("SUFFIX CLASSIFICATIONS")
    output.append("="*80)
    output.append("")
    
    for cls in ['S1', 'S2', 'S3']:
        output.append(f"\n{cls} - {lexicon['class_descriptions'].get(cls, '')}")
        output.append("-"*80)
        
        examples = [(suff, data) for suff, data in lexicon['suffixes'].items()
                   if data['class'] == cls]
        
        for suff, data in examples[:15]:  # Top 15
            output.append(f"  {suff:15s} (conf={data['confidence']})")
            for evid in data['evidence'][:2]:
                output.append(f"    • {evid}")
    
    # Prefix classes
    output.append("\n\n" + "="*80)
    output.append("PREFIX CLASSIFICATIONS")
    output.append("="*80)
    output.append("")
    
    for cls in ['P1', 'P2', 'P3']:
        output.append(f"\n{cls} - {lexicon['class_descriptions'].get(cls, '')}")
        output.append("-"*80)
        
        examples = [(pref, data) for pref, data in lexicon['prefixes'].items()
                   if data['class'] == cls]
        
        for pref, data in examples[:15]:
            output.append(f"  {pref:15s} (conf={data['confidence']})")
            for evid in data['evidence'][:3]:
                output.append(f"    • {evid}")
    
    output.append("\n\n" + "="*80)
    output.append("METHODOLOGY NOTE")
    output.append("="*80)
    output.append("""
This classification describes morpheme BEHAVIOR patterns, not meanings.

Example:
  ✓ "Root 'o' → R1 (ingredient-like, V-heavy in Herbal)"
  ✗ "Root 'o' → 'water' or 'oil'"

Classifications are:
  - Behavioral (how they pattern statistically)
  - Context-aware (section-dependent distributions)
  - Evidence-based (frequency and VPCA data)
  - Conservative (confidence tiers applied)

Next step: Use these classes to build frame templates (SM3).
""")
    
    return "\n".join(output)


def main():
    print("="*80)
    print("VPCA-SM2: ROOT & AFFIX ROLE CLASSIFICATION")
    print("="*80)
    print()
    
    print("Loading data...")
    tokens = load_vpca_tokens()
    print(f"  ✓ Loaded {len(tokens):,} tokens")
    
    p69_rules = load_p69_rules()
    print(f"  ✓ Loaded {len(p69_rules)} p69 rules")
    
    print()
    print("Analyzing roots...")
    root_stats = analyze_roots(tokens)
    print(f"  ✓ Analyzed {len(root_stats)} unique roots")
    
    print()
    print("Analyzing affixes...")
    prefix_stats, suffix_stats = analyze_affixes(tokens)
    print(f"  ✓ Analyzed {len(prefix_stats)} prefixes")
    print(f"  ✓ Analyzed {len(suffix_stats)} suffixes")
    
    print()
    print("Classifying morphemes...")
    
    root_classes = {}
    for root, stats in root_stats.items():
        root_classes[root] = classify_root(root, stats)
    print(f"  ✓ Classified {len(root_classes)} roots")
    
    prefix_classes = {}
    for prefix, stats in prefix_stats.items():
        prefix_classes[prefix] = classify_prefix(prefix, stats)
    print(f"  ✓ Classified {len(prefix_classes)} prefixes")
    
    suffix_classes = {}
    for suffix, stats in suffix_stats.items():
        suffix_classes[suffix] = classify_suffix(suffix, stats)
    print(f"  ✓ Classified {len(suffix_classes)} suffixes")
    
    print()
    print("Generating outputs...")
    
    # Generate role lexicon
    lexicon = generate_role_lexicon(root_classes, prefix_classes, suffix_classes)
    
    with open(ROLE_LEXICON, 'w') as f:
        json.dump(lexicon, f, indent=2)
    print(f"  ✓ Saved: {ROLE_LEXICON}")
    
    # Generate report
    report = generate_report(lexicon, root_stats, prefix_stats, suffix_stats)
    with open(CLASSIFICATION_REPORT, 'w') as f:
        f.write(report)
    print(f"  ✓ Saved: {CLASSIFICATION_REPORT}")
    
    # Save TSV files
    with open(ROOT_CLASSES, 'w') as f:
        f.write("root\tclass\tconfidence\ttotal_freq\tV_count\tP_count\tC_count\n")
        for root, (cls, conf, evid) in root_classes.items():
            if root in root_stats:
                stats = root_stats[root]
                f.write(f"{root}\t{cls}\t{conf}\t{stats['total']}\t{stats['V']}\t{stats['P']}\t{stats['C']}\n")
    print(f"  ✓ Saved: {ROOT_CLASSES}")
    
    with open(AFFIX_CLASSES, 'w') as f:
        f.write("affix\ttype\tclass\tconfidence\ttotal_freq\n")
        for prefix, (cls, conf, evid) in prefix_classes.items():
            f.write(f"{prefix}\tprefix\t{cls}\t{conf}\t{prefix_stats[prefix]['total']}\n")
        for suffix, (cls, conf, evid) in suffix_classes.items():
            f.write(f"{suffix}\tsuffix\t{cls}\t{conf}\t{suffix_stats[suffix]['total']}\n")
    print(f"  ✓ Saved: {AFFIX_CLASSES}")
    
    print()
    print("="*80)
    print("SM2 COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Review classification report: cat results/sm2_classification_report.txt")
    print("  2. Check role lexicon: cat results/sm2_role_lexicon.json")
    print("  3. Proceed to SM3 (section frame templates)")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
