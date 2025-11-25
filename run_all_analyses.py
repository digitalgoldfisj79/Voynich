#!/usr/bin/env python3
"""
Voynich Manuscript Analysis - Master Reproduction Script

This script reproduces all analyses reported in the manuscript:
"Systematic Structural Analysis of the Voynich Manuscript: 
 Falsification of Compression and Simple Hoax Hypotheses"

Expected runtime: ~30 minutes on standard laptop

Usage:
    python run_all_analyses.py                    # Run all analyses
    python run_all_analyses.py --section morph    # Run only morphology
    python run_all_analyses.py --verify           # Verification mode only
"""

import sys
import time
import subprocess
import argparse
from pathlib import Path

# Color output for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    """Print formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(message):
    """Print formatted step message"""
    print(f"{Colors.OKCYAN}➜ {message}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def run_script(script_path, description):
    """Run a Python script and report success/failure"""
    print_step(f"Running: {description}")
    print(f"   Script: {script_path}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        elapsed = time.time() - start_time
        print_success(f"Completed in {elapsed:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print_error(f"Failed after {elapsed:.1f}s")
        print(f"   Error: {e.stderr[:200]}")
        return False
    except FileNotFoundError:
        print_error(f"Script not found: {script_path}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required = ['numpy', 'scipy', 'pandas', 'matplotlib', 'sklearn', 'statsmodels']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print_success(f"{package} installed")
        except ImportError:
            missing.append(package)
            print_error(f"{package} NOT installed")
    
    if missing:
        print_error(f"\nMissing packages: {', '.join(missing)}")
        print(f"Install with: pip install -r requirements.txt")
        return False
    
    print_success("\nAll dependencies satisfied")
    return True

def run_baseline_analysis():
    """Run baseline statistical characterization"""
    print_header("Baseline Statistical Analysis")
    
    success = True
    success &= run_script(
        "scripts/baseline/normalize_corpus.py",
        "Corpus normalization (29,688 tokens)"
    )
    success &= run_script(
        "scripts/baseline/compute_statistics.py",
        "Baseline statistics (entropy, MI, Zipf)"
    )
    
    return success

def run_morphology_analysis():
    """Run morphological analysis"""
    print_header("Morphological Analysis")
    
    success = True
    success &= run_script(
        "scripts/morphology/identify_productive_stems.py",
        "Identifying 9-suffix system (Table 1 & 2)"
    )
    success &= run_script(
        "scripts/morphology/type_frequency_correlation.py",
        "Type-frequency correlation (r=0.89)"
    )
    
    return success

def run_fsm_analysis():
    """Run FSM grammar construction and validation"""
    print_header("FSM Grammar Analysis")
    
    success = True
    success &= run_script(
        "scripts/fsm/build_fsm.py",
        "Building 109-rule FSM grammar"
    )
    success &= run_script(
        "scripts/fsm/validate_fsm.py",
        "Validating on 900 held-out stems"
    )
    
    return success

def run_compression_analysis():
    """Run compression hypothesis testing"""
    print_header("Compression Hypothesis Testing")
    
    success = True
    success &= run_script(
        "scripts/compression/compress_latin.py",
        "Compressing Latin corpus (13,200 tokens)"
    )
    success &= run_script(
        "scripts/compression/compress_occitan.py",
        "Compressing Occitan corpus (7,004 tokens)"
    )
    success &= run_script(
        "scripts/compression/evaluate_compression.py",
        "Evaluating 6 compression models (Tables 3 & 4)"
    )
    
    return success

def run_hoax_analysis():
    """Run hoax hypothesis testing"""
    print_header("Hoax Hypothesis Testing")
    
    success = True
    success &= run_script(
        "scripts/hoax/generate_rugg_controls.py",
        "Generating 3 synthetic controls (30,000 tokens)"
    )
    success &= run_script(
        "scripts/hoax/evaluate_discriminants.py",
        "Evaluating MI₁, FSM, morphology (Table 5)"
    )
    
    return success

def run_verification():
    """Run all verification scripts"""
    print_header("Verification - Checking Manuscript Claims")
    
    verifications = [
        ("scripts/verification/verify_table1.py", "Table 1: Suffix Inventory"),
        ("scripts/verification/verify_table2.py", "Table 2: Stem Paradigms"),
        ("scripts/verification/verify_table3.py", "Table 3: Compression Examples"),
        ("scripts/verification/verify_table4.py", "Table 4: Compression Models"),
        ("scripts/verification/verify_table5.py", "Table 5: Hoax Discriminants"),
    ]
    
    success = True
    for script, description in verifications:
        success &= run_script(script, description)
    
    return success

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Run Voynich manuscript analyses"
    )
    parser.add_argument(
        '--section',
        choices=['baseline', 'morph', 'fsm', 'compression', 'hoax', 'all'],
        default='all',
        help='Which section to run (default: all)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Run verification scripts only'
    )
    parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='Skip dependency check'
    )
    
    args = parser.parse_args()
    
    # Print welcome message
    print_header("Voynich Manuscript Analysis - Reproduction Pipeline")
    print(f"Manuscript: Falsification of Compression and Simple Hoax Hypotheses")
    print(f"Expected runtime: ~30 minutes")
    print(f"Repository: github.com/digitalgoldfisj79/Voynich/tree/paper-2025\n")
    
    start_time = time.time()
    
    # Check dependencies
    if not args.skip_deps and not args.verify:
        if not check_dependencies():
            sys.exit(1)
    
    # Run requested analyses
    success = True
    
    if args.verify:
        success &= run_verification()
    elif args.section == 'all':
        success &= run_baseline_analysis()
        success &= run_morphology_analysis()
        success &= run_fsm_analysis()
        success &= run_compression_analysis()
        success &= run_hoax_analysis()
        print_header("Running Verification")
        success &= run_verification()
    else:
        section_map = {
            'baseline': run_baseline_analysis,
            'morph': run_morphology_analysis,
            'fsm': run_fsm_analysis,
            'compression': run_compression_analysis,
            'hoax': run_hoax_analysis,
        }
        success &= section_map[args.section]()
    
    # Print summary
    elapsed = time.time() - start_time
    print_header("Summary")
    
    if success:
        print_success(f"All analyses completed successfully!")
        print(f"Total runtime: {elapsed/60:.1f} minutes")
        print(f"\nResults saved to: results/")
        print(f"  - Tables: results/tables/")
        print(f"  - Figures: results/figures/")
    else:
        print_error(f"Some analyses failed")
        print(f"Total runtime: {elapsed/60:.1f} minutes")
        print(f"\nCheck error messages above for details")
        sys.exit(1)
    
    print(f"\n{Colors.OKGREEN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Reproduction complete!{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{'='*70}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
