#!/usr/bin/env python3
"""
N6 Validation Master Suite
Combines both AI approaches for comprehensive validation

Test 1: Held-out lexical prediction (structural context)
Test 2: Phrase/collocation validation (Latin corpus matching)
Test 3: Drawing-anchored validation (image-text alignment)
Test 4: Cross-language fit (Latin vs Arabic/Occitan/etc)
Test 5: Entropy reduction (word order predictability)
Test 6: Expert blind evaluation (human validation)

ALL 6 must pass for validated decipherment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

BASE = Path(__file__).parent.parent
N6 = BASE / "N6_Validation"

print("="*80)
print("N6 VALIDATION MASTER SUITE")
print("="*80)

# Load pre-registration
with open(N6 / "PREREGISTRATION.json") as f:
    prereg = json.load(f)

print(f"\nPre-registration hash: {prereg['creation_date']}")
print(f"Held-out folios: {len(prereg['holdout_folios'])}")

# Test status tracking
tests = {
    'test1_lexical': {'status': 'PENDING', 'pass': None},
    'test2_phrases': {'status': 'PENDING', 'pass': None},
    'test3_drawings': {'status': 'PENDING', 'pass': None},
    'test4_language': {'status': 'PENDING', 'pass': None},
    'test5_entropy': {'status': 'PENDING', 'pass': None},
    'test6_expert': {'status': 'PENDING', 'pass': None}
}

print("\n" + "="*80)
print("TEST SUITE STATUS")
print("="*80)

for test_id, info in tests.items():
    print(f"{test_id}: {info['status']}")

print("\n⚠️ Run individual test scripts:")
print("  python3 N6_Validation/n6_test1_lexical.py")
print("  python3 N6_Validation/n6_test2_phrases.py")
print("  python3 N6_Validation/n6_test3_drawings.py")
print("  python3 N6_Validation/n6_test4_language.py")
print("  python3 N6_Validation/n6_test5_entropy.py")
print("  python3 N6_Validation/n6_test6_expert.py")

print("\nOr run all: python3 N6_Validation/n6_run_all.py")

