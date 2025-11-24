#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
print("N5v2 test - checking paths...")
print(f"BASE: {BASE}")
print(f"Whitaker: {BASE / 'corpora/latin_vocab/whitaker_lemmas.tsv'}")
