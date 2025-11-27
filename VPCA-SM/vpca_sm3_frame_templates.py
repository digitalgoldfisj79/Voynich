#!/usr/bin/env python3
"""
VPCA-SM3: Section Frame Templates
==================================

Identifies structural frame patterns in token sequences per section.

Key Principle:
  We identify STRUCTURAL patterns (how tokens combine),
  not SEMANTIC content (what they mean).
  
Example:
  ✓ CORRECT: "Herbal shows pattern [V-heavy] → [C-state] → [P-heavy]"
  ✗ INCORRECT: "Herbal says 'mix herb with water'"

Input:
  - data/vpca2_all_tokens.tsv (VPCA classifications with sequences)
  - results/sm1_vpca_role_map.json (VPCA role mappings)
  - results/sm2_role_lexicon.json (morpheme classifications)

Output:
  - results/sm3_frame_patterns.json (frame templates per section)
  - results/sm3_sequence_analysis.txt (sequence pattern analysis)
  - results/sm3_bigram_transitions.tsv (VPCA state transitions)

Frame Types Identified:
  - Sequential patterns (e.g., V → C → P)
  - Morpheme combinations (e.g., P1-prefix + R1-root + S1-suffix)
  - Section-specific templates
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Data paths
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Input files
VPCA_TOKENS = DATA_DIR / "vpca2_all_tokens.tsv"
ROLE_MAP = RESULTS_DIR / "sm1_vpca_role_map.json"
ROLE_LEXICON = RESULTS_DIR / "sm2_role_lexicon.json"

# Output files
FRAME_PATTERNS = RESULTS_DIR / "sm3_frame_patterns.json"
SEQUENCE_ANALYSIS = RESULTS_DIR / "sm3_sequence_analysis.txt"
BIGRAM_TRANSITIONS = RESULTS_DIR / "sm3_bigram_transitions.tsv"


def load_vpca_sequences():
    """
    Load tokens preserving folio/line sequence information
    """
    sequences = defaultdict(list)  # (folio, line) -> [tokens]
    
    with open(VPCA_TOKENS) as f:
        header = f.readline().strip().split('\t')
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 9:
                folio = parts[1]
                line_num = parts[2]
                token = parts[0]
                vpca = parts[8]
                section = parts[4]
                
                sequences[(folio, line_num)].append({
                    'token': token,
                    'vpca': vpca,
                    'section': section
                })
    
    return sequences


def analyze_vpca_transitions(sequences):
    """
    Analyze VPCA state transitions (bigrams)
    """
    transitions = defaultdict(lambda: defaultdict(int))
    section_transitions = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for (folio, line), tokens in sequences.items():
        if len(tokens) < 2:
            continue
        
        section = tokens[0]['section']
        
        for i in range(len(tokens) - 1):
            current = tokens[i]['vpca']
            next_state = tokens[i+1]['vpca']
            
            transitions[current][next_state] += 1
            section_transitions[section][current][next_state] += 1
    
    return transitions, section_transitions


def identify_sequence_patterns(sequences, min_length=3):
    """
    Identify common VPCA sequence patterns
    """
    patterns = defaultdict(lambda: defaultdict(int))
    
    for (folio, line), tokens in sequences.items():
        if len(tokens) < min_length:
            continue
        
        section = tokens[0]['section']
        
        # Extract VPCA sequences of varying lengths
        for length in range(min_length, min(6, len(tokens) + 1)):
            for i in range(len(tokens) - length + 1):
                pattern = tuple(tokens[i+j]['vpca'] for j in range(length))
                patterns[section][pattern] += 1
    
    return patterns


def classify_line_structure(tokens):
    """
    Classify the overall structure of a line
    Returns: structure type and confidence
    """
    if len(tokens) < 2:
        return ('SINGLE', 'Low', [])
    
    vpca_seq = [t['vpca'] for t in tokens]
    
    # Count state types
    v_count = vpca_seq.count('V')
    p_count = vpca_seq.count('P')
    c_count = vpca_seq.count('C')
    a_count = vpca_seq.count('A')
    
    total = len(vpca_seq)
    v_ratio = v_count / total
    c_ratio = c_count / total
    
    evidence = [
        f"Length: {total} tokens",
        f"V={v_count}, P={p_count}, C={c_count}, A={a_count}"
    ]
    
    # Identify patterns
    
    # V → C progression (ingredient → process)
    if v_ratio > 0.3 and c_ratio > 0.1:
        # Check if V tends to come before C
        v_positions = [i for i, x in enumerate(vpca_seq) if x == 'V']
        c_positions = [i for i, x in enumerate(vpca_seq) if x == 'C']
        if v_positions and c_positions and sum(v_positions)/len(v_positions) < sum(c_positions)/len(c_positions):
            return ('V→C', 'Medium', evidence + ['V precedes C (ingredient → process)'])
    
    # C-heavy (procedural)
    if c_ratio > 0.15:
        return ('PROCEDURAL', 'Medium', evidence + ['High C-state (procedural)'])
    
    # V-heavy (descriptive/ingredient)
    if v_ratio > 0.5:
        return ('DESCRIPTIVE', 'Medium', evidence + ['High V-state (descriptive)'])
    
    # P-heavy (neutral/connective)
    if p_count > total * 0.7:
        return ('NEUTRAL', 'Low', evidence + ['P-dominant'])
    
    return ('MIXED', 'Low', evidence)


def build_section_frames(sequences):
    """
    Build frame templates for each section
    """
    frames = {}
    
    # Group sequences by section
    by_section = defaultdict(list)
    for (folio, line), tokens in sequences.items():
        if tokens:
            section = tokens[0]['section']
            by_section[section].append(tokens)
    
    # Analyze each section
    for section, line_list in by_section.items():
        structure_types = Counter()
        pattern_examples = defaultdict(list)
        
        for tokens in line_list:
            struct_type, conf, evid = classify_line_structure(tokens)
            structure_types[struct_type] += 1
            
            if conf in ['Medium', 'High'] and len(pattern_examples[struct_type]) < 3:
                token_str = ' '.join(t['token'] for t in tokens[:10])  # First 10 tokens
                vpca_str = ' '.join(t['vpca'] for t in tokens[:10])
                pattern_examples[struct_type].append({
                    'tokens': token_str,
                    'vpca': vpca_str
                })
        
        frames[section] = {
            'total_lines': len(line_list),
            'structure_distribution': dict(structure_types),
            'dominant_structure': structure_types.most_common(1)[0][0] if structure_types else 'UNKNOWN',
            'examples': dict(pattern_examples)
        }
    
    return frames


def generate_analysis_report(transitions, section_transitions, patterns, frames):
    """
    Generate human-readable sequence analysis report
    """
    output = []
    output.append("="*80)
    output.append("VPCA-SM3: SECTION FRAME TEMPLATES")
    output.append("="*80)
    output.append("")
    output.append("Identifies structural patterns in token sequences per section.")
    output.append("")
    
    # VPCA transition analysis
    output.append("="*80)
    output.append("VPCA STATE TRANSITIONS (Overall)")
    output.append("="*80)
    output.append("")
    output.append("Most common bigram transitions:")
    
    # Flatten and sort transitions
    all_transitions = []
    for state1, next_states in transitions.items():
        for state2, count in next_states.items():
            all_transitions.append((state1, state2, count))
    
    all_transitions.sort(key=lambda x: x[2], reverse=True)
    
    for state1, state2, count in all_transitions[:20]:
        output.append(f"  {state1} → {state2}: {count:,} occurrences")
    
    output.append("")
    
    # Section-specific frame patterns
    output.append("="*80)
    output.append("SECTION FRAME PATTERNS")
    output.append("="*80)
    output.append("")
    
    for section in sorted(frames.keys()):
        frame_data = frames[section]
        output.append(f"\n{section}")
        output.append("-"*80)
        output.append(f"Total lines: {frame_data['total_lines']}")
        output.append(f"Dominant structure: {frame_data['dominant_structure']}")
        output.append("")
        output.append("Structure distribution:")
        for struct_type, count in sorted(frame_data['structure_distribution'].items(), 
                                         key=lambda x: x[1], reverse=True):
            pct = (count / frame_data['total_lines']) * 100
            output.append(f"  {struct_type:15s}: {count:4d} ({pct:5.1f}%)")
        
        output.append("")
        output.append("Example patterns:")
        for struct_type, examples in frame_data['examples'].items():
            if examples:
                output.append(f"  {struct_type}:")
                for ex in examples[:2]:  # Show 2 examples
                    output.append(f"    Tokens: {ex['tokens']}")
                    output.append(f"    VPCA:   {ex['vpca']}")
                    output.append("")
    
    # Common sequence patterns
    output.append("\n" + "="*80)
    output.append("COMMON VPCA SEQUENCES (3+ tokens)")
    output.append("="*80)
    output.append("")
    
    for section in sorted(patterns.keys()):
        output.append(f"\n{section}")
        output.append("-"*80)
        section_patterns = patterns[section]
        
        # Sort by frequency
        sorted_patterns = sorted(section_patterns.items(), key=lambda x: x[1], reverse=True)
        
        for pattern, count in sorted_patterns[:10]:  # Top 10
            if count >= 5:  # Minimum frequency threshold
                pattern_str = ' → '.join(pattern)
                output.append(f"  {pattern_str:25s}: {count:4d} occurrences")
    
    output.append("\n\n" + "="*80)
    output.append("INTERPRETATION GUIDE")
    output.append("="*80)
    output.append("""
Frame patterns describe STRUCTURAL templates, not semantic content.

Structure Types:
  V→C: Ingredient-to-process progression
       (Common in Recipes, Pharma)
       
  PROCEDURAL: High C-state concentration
              (Indicates step-by-step operations)
              
  DESCRIPTIVE: High V-state concentration
               (Indicates ingredient/property lists)
               
  NEUTRAL: P-state dominant
           (Connective or transitional text)

These patterns constrain what KINDS of semantic content are likely,
but do NOT determine specific meanings.

Example:
  ✓ "Recipe shows V→C pattern (ingredients → processing)"
  ✗ "This recipe says 'boil the herbs'" (too specific)

Next step: Use frames to constrain proto-gloss hypotheses (SM4).
""")
    
    return "\n".join(output)


def main():
    print("="*80)
    print("VPCA-SM3: SECTION FRAME TEMPLATES")
    print("="*80)
    print()
    
    print("Loading data...")
    sequences = load_vpca_sequences()
    print(f"  ✓ Loaded {len(sequences):,} lines")
    
    print()
    print("Analyzing VPCA transitions...")
    transitions, section_transitions = analyze_vpca_transitions(sequences)
    total_transitions = sum(sum(next_states.values()) for next_states in transitions.values())
    print(f"  ✓ Analyzed {total_transitions:,} state transitions")
    
    print()
    print("Identifying sequence patterns...")
    patterns = identify_sequence_patterns(sequences)
    total_patterns = sum(sum(p.values()) for p in patterns.values())
    print(f"  ✓ Identified {total_patterns:,} sequence patterns")
    
    print()
    print("Building section frame templates...")
    frames = build_section_frames(sequences)
    print(f"  ✓ Built frames for {len(frames)} sections")
    
    print()
    print("Generating outputs...")
    
    # Save frame patterns JSON
    output_data = {
        'frames': frames,
        'transitions': {k: dict(v) for k, v in transitions.items()},
        'section_transitions': {
            section: {k: dict(v) for k, v in trans.items()}
            for section, trans in section_transitions.items()
        }
    }
    
    with open(FRAME_PATTERNS, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"  ✓ Saved: {FRAME_PATTERNS}")
    
    # Save analysis report
    report = generate_analysis_report(transitions, section_transitions, patterns, frames)
    with open(SEQUENCE_ANALYSIS, 'w') as f:
        f.write(report)
    print(f"  ✓ Saved: {SEQUENCE_ANALYSIS}")
    
    # Save bigram transitions TSV
    with open(BIGRAM_TRANSITIONS, 'w') as f:
        f.write("state1\tstate2\tcount\n")
        for state1, next_states in sorted(transitions.items()):
            for state2, count in sorted(next_states.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{state1}\t{state2}\t{count}\n")
    print(f"  ✓ Saved: {BIGRAM_TRANSITIONS}")
    
    print()
    print("="*80)
    print("SM3 COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Review sequence analysis: cat results/sm3_sequence_analysis.txt")
    print("  2. Check frame patterns: cat results/sm3_frame_patterns.json")
    print("  3. Proceed to SM4 (controlled proto-glosses)")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
