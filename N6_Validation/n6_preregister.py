#!/usr/bin/env python3
"""
N6 Pre-Registration: Select Held-Out Data BEFORE N5 Begins

This script:
1. Randomly selects 15% of folios as held-out test set
2. Creates locked manifest with timestamp and hash
3. These folios MUST NOT be examined until N6 execution
4. Prevents researcher degrees of freedom and p-hacking
"""

import random
import hashlib
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "N6_Validation"

print("="*80)
print("N6 PRE-REGISTRATION: Selecting Held-Out Data")
print("="*80)

# Set random seed from current timestamp for reproducibility
SEED = int(datetime.now().timestamp())
random.seed(SEED)

print(f"\nRandom seed: {SEED}")
print(f"Timestamp: {datetime.now().isoformat()}")

# Load all folios from folio_sections.tsv
sections_file = BASE / "metadata/folio_sections.tsv"

if not sections_file.exists():
    print(f"ERROR: {sections_file} not found")
    exit(1)

import pandas as pd
folios_df = pd.read_csv(sections_file, sep='\t')

print(f"\nTotal folios available: {len(folios_df)}")

# Stratified sampling: 15% from each section
holdout_folios = []

for section in folios_df['section'].unique():
    section_folios = folios_df[folios_df['section'] == section]['folio'].tolist()
    n_holdout = max(1, int(len(section_folios) * 0.15))
    
    selected = random.sample(section_folios, n_holdout)
    holdout_folios.extend(selected)
    
    print(f"  {section}: {n_holdout}/{len(section_folios)} folios held out")

holdout_folios.sort()

print(f"\nTotal held-out folios: {len(holdout_folios)}")
print(f"Percentage: {len(holdout_folios)/len(folios_df)*100:.1f}%")

# Create manifest
manifest = {
    "creation_date": datetime.now().isoformat(),
    "random_seed": SEED,
    "total_folios": len(folios_df),
    "holdout_count": len(holdout_folios),
    "holdout_percentage": len(holdout_folios)/len(folios_df)*100,
    "holdout_folios": holdout_folios,
    "validation_tests": {
        "test_1": {
            "name": "Held-out stem prediction",
            "threshold": "p < 0.01 vs permutation baseline",
            "description": "N5 hypotheses must predict held-out stem meanings above chance"
        },
        "test_2": {
            "name": "Drawing-consistency prediction",
            "threshold": "p < 0.05 vs random assignment",
            "description": "Botanical stems appear in plant folios, astronomical in astronomical"
        },
        "test_3": {
            "name": "Phrase-level alignment",
            "threshold": "p < 0.01 vs random Latin phrases",
            "description": "Multi-word expressions match real medieval pharmaceutical phrases"
        },
        "test_4": {
            "name": "Entropy reduction",
            "threshold": "95% bootstrap CI shows reduction",
            "description": "Voynich→Latin mapping reduces word order entropy"
        },
        "test_5": {
            "name": "Cross-language comparison",
            "threshold": "p < 0.01, single best-fit language",
            "description": "PMI network similarity identifies Latin > other languages"
        },
        "test_6": {
            "name": "Expert evaluation",
            "threshold": "kappa > 0.6 inter-rater agreement",
            "description": "Medieval Latin experts agree glosses are plausible"
        }
    },
    "passing_criteria": "ALL 6 tests must pass. Failure = iterate N5 with new hypotheses + different holdout set."
}

# Save manifest
manifest_file = OUTPUT / "PREREGISTRATION.json"
with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2)

# Also save as markdown for readability
md_file = OUTPUT / "PREREGISTRATION.md"
with open(md_file, 'w') as f:
    f.write("# N6 VALIDATION PRE-REGISTRATION\n\n")
    f.write("**⚠️ THIS FILE IS LOCKED AND IMMUTABLE ⚠️**\n\n")
    f.write(f"**Created:** {manifest['creation_date']}\n")
    f.write(f"**Random Seed:** {manifest['random_seed']}\n\n")
    
    f.write("## Held-Out Test Set\n\n")
    f.write(f"Total folios: {manifest['total_folios']}\n")
    f.write(f"Held out: {manifest['holdout_count']} ({manifest['holdout_percentage']:.1f}%)\n\n")
    
    f.write("**Held-out folios:**\n```\n")
    for folio in manifest['holdout_folios']:
        f.write(f"{folio}\n")
    f.write("```\n\n")
    
    f.write("## N6 Validation Tests (All Must Pass)\n\n")
    for test_id, test_info in manifest['validation_tests'].items():
        f.write(f"### {test_info['name']}\n")
        f.write(f"- **Threshold:** {test_info['threshold']}\n")
        f.write(f"- **Description:** {test_info['description']}\n\n")
    
    f.write("## Passing Criteria\n\n")
    f.write(f"{manifest['passing_criteria']}\n\n")
    
    f.write("## Critical Rules\n\n")
    f.write("1. **Never examine held-out folios until N6 execution**\n")
    f.write("2. **N5 hypotheses generated without knowledge of held-out data**\n")
    f.write("3. **No post-hoc adjustment of thresholds**\n")
    f.write("4. **If N6 fails, use DIFFERENT held-out set for next iteration**\n")
    f.write("5. **Report results honestly regardless of outcome**\n\n")

# Calculate hash of manifest
manifest_str = json.dumps(manifest, sort_keys=True)
manifest_hash = hashlib.sha256(manifest_str.encode()).hexdigest()

with open(md_file, 'a') as f:
    f.write(f"## Manifest Hash\n\n")
    f.write(f"```\n{manifest_hash}\n```\n\n")
    f.write("Any modification to this file invalidates N6 validation.\n")

# Save hash separately
hash_file = OUTPUT / "PREREGISTRATION.hash"
with open(hash_file, 'w') as f:
    f.write(f"{manifest_hash}\n")

print(f"\n✅ Pre-registration complete!")
print(f"\n📋 Files created:")
print(f"  - {manifest_file}")
print(f"  - {md_file}")
print(f"  - {hash_file}")
print(f"\n🔒 Manifest hash: {manifest_hash}")
print(f"\n⚠️ CRITICAL: Do not examine held-out folios until N6 execution!")

# Create lockfile to prevent accidental access
lockfile = OUTPUT / "HOLDOUT_LOCKED.txt"
with open(lockfile, 'w') as f:
    f.write("="*80 + "\n")
    f.write("HELD-OUT DATA LOCKED\n")
    f.write("="*80 + "\n\n")
    f.write("The following folios are HELD OUT for N6 validation:\n\n")
    for folio in manifest['holdout_folios']:
        f.write(f"  {folio}\n")
    f.write("\n" + "="*80 + "\n")
    f.write("DO NOT EXAMINE THESE FOLIOS UNTIL N6 EXECUTION\n")
    f.write("="*80 + "\n\n")
    f.write("Examining held-out data before N6 invalidates the validation.\n")
    f.write("This would introduce researcher degrees of freedom and p-hacking.\n\n")
    f.write(f"Pre-registration hash: {manifest_hash}\n")

print(f"\n📋 Created lockfile: {lockfile}")
print(f"\nN5 work can now begin safely.")
