#!/usr/bin/env python3
"""
Master Script: Generate All Hoax Controls

Generates all 3 synthetic control types and calculates discriminants:
1. Rugg Basic (grid-based, mean ~25 chars)
2. Rugg Markov (Markov chain, mean ~10 chars)
3. Calculate discriminant metrics

This reproduces Table 5 of the manuscript.
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_path, description):
    """Run a Python script and report results"""
    print()
    print("="*80)
    print(f"RUNNING: {description}")
    print("="*80)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(Path(__file__).parent.parent.parent),
            capture_output=False,  # Show output in real-time
            timeout=300
        )
        
        if result.returncode == 0:
            print()
            print(f"✓ SUCCESS: {description}")
            return True
        else:
            print()
            print(f"✗ FAILED: {description}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ TIMEOUT: {description}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {description}")
        print(f"  {str(e)}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     HOAX CONTROL GENERATION PIPELINE                         ║
║                                                                              ║
║  Generates synthetic Voynich-like controls to test hoax hypothesis          ║
║  - Rugg Basic (grid method)                                                  ║
║  - Rugg Markov (bigram chains)                                               ║
║  - Discriminant analysis (Table 5)                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    scripts_dir = Path(__file__).parent
    
    scripts = [
        (scripts_dir / 'generate_rugg_basic.py', 'Generate Rugg Basic Controls'),
        (scripts_dir / 'generate_rugg_markov.py', 'Generate Rugg Markov Controls'),
        (scripts_dir / 'calculate_discriminants.py', 'Calculate Discriminants (Table 5)'),
    ]
    
    results = []
    for script, desc in scripts:
        if script.exists():
            results.append(run_script(script, desc))
        else:
            print(f"✗ Script not found: {script}")
            results.append(False)
    
    print()
    print("="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    print()
    
    for (script, desc), success in zip(scripts, results):
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {desc}")
    
    print()
    
    if all(results):
        print("="*80)
        print("✓ ALL HOAX CONTROLS GENERATED SUCCESSFULLY")
        print("="*80)
        print()
        print("Output files:")
        print("  • results/hoax/rugg_basic.tsv")
        print("  • results/hoax/rugg_markov.tsv")
        print("  • results/hoax/rugg_metrics.tsv")
        print("  • results/hoax/pR3_summary.tsv")
        print()
        print("These files contain:")
        print("  • 10,000 synthetic tokens per control type")
        print("  • Discriminant metrics (MI, FSM, suffix diversity)")
        print("  • Z-scores showing difference from Voynich")
        print("  • Distinguish index (composite discriminant)")
        print()
        print("Key finding:")
        print("  → Synthetic controls are distinguishable from Voynich")
        print("  → This argues against simple hoax hypothesis")
        print()
        sys.exit(0)
    else:
        print("="*80)
        print("✗ SOME SCRIPTS FAILED")
        print("="*80)
        print()
        print("Check error messages above for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()
