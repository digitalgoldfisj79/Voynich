#!/usr/bin/env python3
"""
VPCA-SM3: Frame Templates (MINIMAL - VPCA Transitions Only)
===========================================================

Identifies structural frame patterns using ONLY validated VPCA states.
NO morpheme analysis - pure sequential patterns.

Key Principle:
  Analyze how VPCA states (Valley/Peak/Change) combine in sequences.
  Section-specific frame templates from state transitions.

Dependencies:
  - ONLY vpca2_all_tokens.tsv (VPCA classifications)
  - NO morpheme files needed (SM1/SM2 independent)

Output:
  - sm3_minimal_frame_patterns.json (frame templates per section)
  - sm3_minimal_sequence_analysis.txt (sequence pattern analysis)
  - sm3_minimal_transitions.tsv (VPCA state transition matrix)

Author: Validated analysis, November 27, 2025
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import sys

# Check if we have the data file
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Input
VPCA_TOKENS = DATA_DIR / "vpca2_all_tokens.tsv"

# Output
FRAME_PATTERNS = RESULTS_DIR / "sm3_minimal_frame_patterns.json"
SEQUENCE_ANALYSIS = RESULTS_DIR / "sm3_minimal_sequence_analysis.txt"
TRANSITIONS_TSV = RESULTS_DIR / "sm3_minimal_transitions.tsv"

# VPCA state definitions
VPCA_STATES = ['V', 'P', 'C']
SECTION_NAMES = {
    'H': 'Herbal',
    'A': 'Astronomical', 
    'B': 'Biological',
    'C': 'Cosmological',
    'P': 'Pharmaceutical',
    'R': 'Recipes',
    'S': 'Stars',
    'Z': 'Zodiac'
}


def load_vpca_sequences():
    """
    Load tokens preserving folio/line sequence information.
    Only needs VPCA states - no morphology.
    """
    sequences = defaultdict(list)  # (folio, line) -> [tokens with VPCA]
    token_count = 0
    
    print("Loading VPCA token sequences...")
    
    if not VPCA_TOKENS.exists():
        print(f"ERROR: Cannot find {VPCA_TOKENS}")
        print(f"Current directory: {Path.cwd()}")
        return sequences
    
    with open(VPCA_TOKENS) as f:
        header = f.readline().strip().split('\t')
        print(f"Header: {header}")
        
        # Find column indices
        try:
            token_idx = header.index('token')
            folio_idx = header.index('folio')
            line_idx = header.index('line')
            section_idx = header.index('section')
            vpca_idx = header.index('vpca')
        except ValueError as e:
            print(f"ERROR: Missing required column: {e}")
            return sequences
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) <= max(token_idx, folio_idx, line_idx, section_idx, vpca_idx):
                continue
            
            token = parts[token_idx]
            folio = parts[folio_idx]
            line_num = parts[line_idx]
            section = parts[section_idx]
            vpca = parts[vpca_idx]
            
            # Only include valid VPCA states
            if vpca in VPCA_STATES:
                sequences[(folio, line_num)].append({
                    'token': token,
                    'vpca': vpca,
                    'section': section
                })
                token_count += 1
    
    print(f"Loaded {token_count} tokens in {len(sequences)} sequences")
    return sequences


def analyze_transitions(sequences):
    """
    Analyze VPCA state transitions (bigrams).
    Pure structural analysis - no semantics.
    """
    print("\nAnalyzing VPCA transitions...")
    
    # Global transitions
    global_transitions = defaultdict(lambda: defaultdict(int))
    
    # Section-specific transitions
    section_transitions = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    # Trigrams (3-state sequences)
    trigrams = defaultdict(int)
    section_trigrams = defaultdict(lambda: defaultdict(int))
    
    for (folio, line), tokens in sequences.items():
        if len(tokens) < 2:
            continue
        
        section = tokens[0]['section']
        
        # Bigrams
        for i in range(len(tokens) - 1):
            current = tokens[i]['vpca']
            next_state = tokens[i+1]['vpca']
            
            global_transitions[current][next_state] += 1
            section_transitions[section][current][next_state] += 1
        
        # Trigrams
        for i in range(len(tokens) - 2):
            trigram = tuple(t['vpca'] for t in tokens[i:i+3])
            trigrams[trigram] += 1
            section_trigrams[section][trigram] += 1
    
    return global_transitions, section_transitions, trigrams, section_trigrams


def identify_frame_patterns(section_trigrams, section_transitions, min_count=5):
    """
    Identify structural frame patterns per section.
    
    Frame = common 3-state sequence that might represent:
      - Procedural steps (e.g., V→C→P = setup→change→result)
      - Descriptive patterns (e.g., P→P→P = sustained peak)
      - Transformation sequences (e.g., C→C→C = continuous change)
    """
    print("\nIdentifying frame patterns...")
    
    frames = {}
    
    for section, trigrams in section_trigrams.items():
        # Filter to common patterns
        common_trigrams = {t: c for t, c in trigrams.items() if c >= min_count}
        
        if not common_trigrams:
            continue
        
        # Sort by frequency
        sorted_trigrams = sorted(common_trigrams.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate transition preferences
        trans = section_transitions.get(section, {})
        total_trans = sum(sum(d.values()) for d in trans.values())
        
        # Identify dominant patterns
        patterns = []
        for trigram, count in sorted_trigrams[:10]:  # Top 10
            pattern_type = classify_pattern(trigram)
            frequency = count / total_trans if total_trans > 0 else 0
            
            patterns.append({
                'sequence': '→'.join(trigram),
                'type': pattern_type,
                'count': count,
                'frequency': round(frequency, 4)
            })
        
        frames[section] = {
            'name': SECTION_NAMES.get(section, section),
            'patterns': patterns,
            'total_sequences': total_trans
        }
    
    return frames


def classify_pattern(trigram):
    """
    Classify what type of structural pattern this might represent.
    Based on VPCA semantics:
      V = Valley (stable/preparatory)
      P = Peak (active/intensive)
      C = Change (transitional)
    """
    if trigram == ('V', 'C', 'P'):
        return "Progressive: Preparation → Transition → Action"
    elif trigram == ('P', 'C', 'V'):
        return "Regressive: Action → Transition → Stabilization"
    elif trigram == ('C', 'C', 'C'):
        return "Continuous Change: Transformation sequence"
    elif trigram == ('P', 'P', 'P'):
        return "Sustained Peak: Intensive action"
    elif trigram == ('V', 'V', 'V'):
        return "Sustained Valley: Stable/descriptive"
    elif trigram[0] == trigram[2] and trigram[1] == 'C':
        return f"Symmetric: {trigram[0]} → Change → {trigram[0]} (cyclic)"
    elif trigram.count('C') >= 2:
        return "Change-heavy: Multiple transformations"
    elif trigram.count('P') >= 2:
        return "Peak-heavy: Action-focused"
    elif trigram.count('V') >= 2:
        return "Valley-heavy: Stable/descriptive"
    else:
        return "Mixed: Varied states"


def calculate_transition_matrix(global_transitions):
    """
    Calculate normalized transition probabilities.
    """
    print("\nCalculating transition matrix...")
    
    matrix = {}
    
    for state1 in VPCA_STATES:
        total = sum(global_transitions[state1].values())
        if total == 0:
            matrix[state1] = {s2: 0.0 for s2 in VPCA_STATES}
        else:
            matrix[state1] = {
                s2: global_transitions[state1][s2] / total 
                for s2 in VPCA_STATES
            }
    
    return matrix


def write_analysis(frames, matrix, section_transitions, trigrams):
    """
    Write human-readable analysis.
    """
    print(f"\nWriting analysis to {SEQUENCE_ANALYSIS}...")
    
    with open(SEQUENCE_ANALYSIS, 'w') as f:
        f.write("VPCA-SM3: FRAME TEMPLATE ANALYSIS (MINIMAL)\n")
        f.write("=" * 70 + "\n\n")
        f.write("Structural frame patterns using ONLY validated VPCA states.\n")
        f.write("NO morpheme analysis - pure sequential patterns.\n\n")
        
        # Global transition matrix
        f.write("GLOBAL TRANSITION MATRIX\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'From':<10} {'→ V':>12} {'→ P':>12} {'→ C':>12}\n")
        f.write("-" * 70 + "\n")
        
        for state1 in VPCA_STATES:
            f.write(f"{state1:<10}")
            for state2 in VPCA_STATES:
                prob = matrix[state1][state2]
                f.write(f"{prob:>12.3f}")
            f.write("\n")
        
        f.write("\n\n")
        
        # Section-specific patterns
        f.write("SECTION-SPECIFIC FRAME PATTERNS\n")
        f.write("=" * 70 + "\n\n")
        
        for section, data in sorted(frames.items()):
            f.write(f"{data['name']} (Section {section})\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total sequences: {data['total_sequences']}\n\n")
            
            f.write(f"{'Pattern':<20} {'Type':<40} {'Count':>8}\n")
            f.write("-" * 70 + "\n")
            
            for pattern in data['patterns']:
                f.write(f"{pattern['sequence']:<20} {pattern['type']:<40} {pattern['count']:>8}\n")
            
            f.write("\n\n")
        
        # Top global trigrams
        f.write("TOP 20 GLOBAL TRIGRAM PATTERNS\n")
        f.write("=" * 70 + "\n\n")
        
        sorted_trigrams = sorted(trigrams.items(), key=lambda x: x[1], reverse=True)[:20]
        
        f.write(f"{'Pattern':<15} {'Type':<35} {'Count':>8}\n")
        f.write("-" * 70 + "\n")
        
        for trigram, count in sorted_trigrams:
            pattern = '→'.join(trigram)
            ptype = classify_pattern(trigram)
            f.write(f"{pattern:<15} {ptype:<35} {count:>8}\n")


def write_transition_tsv(matrix, section_transitions):
    """
    Write transition matrix as TSV.
    """
    print(f"Writing transitions to {TRANSITIONS_TSV}...")
    
    with open(TRANSITIONS_TSV, 'w') as f:
        # Global matrix
        f.write("section\tfrom_state\tto_state\tcount\tprobability\n")
        
        # Calculate global counts
        global_counts = defaultdict(lambda: defaultdict(int))
        for section, trans in section_transitions.items():
            for s1, targets in trans.items():
                for s2, count in targets.items():
                    global_counts[s1][s2] += count
        
        # Write global
        for s1 in VPCA_STATES:
            for s2 in VPCA_STATES:
                count = global_counts[s1][s2]
                prob = matrix[s1][s2]
                f.write(f"GLOBAL\t{s1}\t{s2}\t{count}\t{prob:.4f}\n")
        
        # Write per section
        for section in sorted(section_transitions.keys()):
            trans = section_transitions[section]
            total = sum(sum(d.values()) for d in trans.values())
            
            for s1 in VPCA_STATES:
                for s2 in VPCA_STATES:
                    count = trans[s1][s2]
                    prob = count / total if total > 0 else 0.0
                    f.write(f"{section}\t{s1}\t{s2}\t{count}\t{prob:.4f}\n")


def main():
    print("=" * 70)
    print("VPCA-SM3: MINIMAL FRAME ANALYSIS")
    print("=" * 70)
    print("\nStructural patterns using ONLY validated VPCA states")
    print("NO morpheme dependencies - SM1/SM2 independent\n")
    
    # Load sequences
    sequences = load_vpca_sequences()
    
    if not sequences:
        print("\nERROR: No sequences loaded. Check data file location.")
        return 1
    
    # Analyze transitions
    global_trans, section_trans, trigrams, section_trigrams = analyze_transitions(sequences)
    
    # Identify patterns
    frames = identify_frame_patterns(section_trigrams, section_trans)
    
    # Calculate matrix
    matrix = calculate_transition_matrix(global_trans)
    
    # Write outputs
    with open(FRAME_PATTERNS, 'w') as f:
        json.dump({
            'transition_matrix': matrix,
            'section_frames': frames,
            'metadata': {
                'version': 'SM3-Minimal',
                'dependencies': 'VPCA states only',
                'morphemes': 'None (SM1/SM2 independent)',
                'total_sequences': len(sequences),
                'total_tokens': sum(len(s) for s in sequences.values())
            }
        }, f, indent=2)
    
    write_analysis(frames, matrix, section_trans, trigrams)
    write_transition_tsv(matrix, section_trans)
    
    print("\n" + "=" * 70)
    print("SM3-MINIMAL COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  {FRAME_PATTERNS}")
    print(f"  {SEQUENCE_ANALYSIS}")
    print(f"  {TRANSITIONS_TSV}")
    print("\nKey Findings:")
    print(f"  - Analyzed {len(sequences)} sequences")
    print(f"  - Identified {len(frames)} section-specific frame patterns")
    print(f"  - {len(trigrams)} unique trigram patterns found")
    print("\nThis analysis is SM1/SM2 independent - uses only VPCA states.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
