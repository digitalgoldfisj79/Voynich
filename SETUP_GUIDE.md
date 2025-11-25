# Publication Branch Setup Guide

This guide helps you set up the `paper-2025` publication branch with all files matching the manuscript claims.

---

## Step 1: Create Publication Branch

```bash
cd /path/to/your/Voynich/repo

# Create and switch to publication branch
git checkout -b paper-2025

# Confirm you're on the new branch
git branch
```

---

## Step 2: Copy Publication Files

```bash
# Copy the generated files to your repo
# (Assuming you downloaded them to ~/Downloads/publication_branch/)

cp ~/Downloads/publication_branch/README.md .
cp ~/Downloads/publication_branch/LICENSE .
cp ~/Downloads/publication_branch/requirements.txt .
cp ~/Downloads/publication_branch/run_all_analyses.py .

# Create scripts directory structure
mkdir -p scripts/verification
mkdir -p scripts/morphology
mkdir -p scripts/fsm
mkdir -p scripts/compression
mkdir -p scripts/hoax
mkdir -p scripts/baseline

# Copy verification scripts
cp ~/Downloads/publication_branch/scripts/verification/*.py scripts/verification/
```

---

## Step 3: Link Your Existing Scripts

Now you need to create wrapper scripts that point to your actual code. Here's how:

### Morphology Scripts

**identify_productive_stems.py** → Points to your Phase analysis

```python
#!/usr/bin/env python3
"""
Wrapper: Morphology Analysis
Points to actual implementation in N5v3_Morphology or Phase analysis
"""
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import your actual implementation
from N5v3_Morphology import morphological_analysis  # ADJUST THIS

if __name__ == "__main__":
    print("Running morphological analysis...")
    morphological_analysis.run()  # ADJUST THIS
    print("Results saved to: results/tables/table1_suffix_inventory.csv")
```

Save this as: `scripts/morphology/identify_productive_stems.py`

**OR** if you prefer symlinks:

```bash
# If your actual script is at: N5v3_Morphology/analyze_morphology.py
ln -s ../../N5v3_Morphology/analyze_morphology.py scripts/morphology/identify_productive_stems.py
```

### Compression Scripts

Your existing scripts:
- `c01_compare_compression.sh`
- `co2_compression_metrics.sh`

Create wrappers:

```bash
# scripts/compression/compress_latin.py
#!/usr/bin/env python3
"""Wrapper for Latin compression"""
import subprocess
subprocess.run(["bash", "../../c01_compare_compression.sh", "latin"], check=True)
```

```bash
# scripts/compression/compress_occitan.py
#!/usr/bin/env python3
"""Wrapper for Occitan compression"""
import subprocess
subprocess.run(["bash", "../../c01_compare_compression.sh", "occitan"], check=True)
```

### FSM Scripts

Your existing scripts:
- `p69_validate.py`
- `p69_rules_final.json`

Create wrappers:

```bash
# scripts/fsm/build_fsm.py
#!/usr/bin/env python3
import sys
sys.path.insert(0, "../..")
from Phase69 import build_fsm  # ADJUST
build_fsm.main()
```

```bash
# scripts/fsm/validate_fsm.py
#!/usr/bin/env python3
import subprocess
subprocess.run(["python", "../../p69_validate.py"], check=True)
```

---

## Step 4: Copy Data Files

```bash
# Create data directory
mkdir -p data

# Copy your corpus files (adjust paths as needed)
cp corpora/voynich_corpus.txt data/
cp corpora/latin_corpus.txt data/
cp corpora/occitan_corpus.txt data/

# Or symlink them
ln -s ../corpora/voynich_corpus.txt data/
ln -s ../corpora/latin_corpus.txt data/
ln -s ../corpora/occitan_corpus.txt data/
```

---

## Step 5: Copy Results

```bash
# Create results directory
mkdir -p results/tables
mkdir -p results/figures

# Copy or symlink your existing results
cp -r final_submission/figures/* results/figures/

# If you have table CSVs generated, copy them
cp results/*.csv results/tables/
```

---

## Step 6: Test the Setup

```bash
# Make scripts executable
chmod +x run_all_analyses.py
chmod +x scripts/**/*.py

# Test dependency check
python run_all_analyses.py --skip-deps --verify

# If that works, try running full pipeline
python run_all_analyses.py
```

---

## Step 7: Commit and Push

```bash
# Check what's in your branch
git status

# Add files
git add README.md LICENSE requirements.txt run_all_analyses.py
git add scripts/ data/ results/

# Commit
git commit -m "Add publication branch for paper-2025"

# Push to GitHub
git push -u origin paper-2025
```

---

## Step 8: Update Manuscript

Change the manuscript URL from:
```
github.com/digitalgoldfisj79/Voynich
```

To:
```
github.com/digitalgoldfisj79/Voynich/tree/paper-2025
```

---

## Troubleshooting

### Problem: Scripts not found

**Solution:** Check that wrapper scripts point to correct paths:

```python
# In wrapper scripts, adjust paths like:
sys.path.insert(0, "../../N5v3_Morphology")  # Two dirs up, then into folder
```

### Problem: Import errors

**Solution:** Make sure your actual scripts are Python modules:

```bash
# Add __init__.py to directories
touch N5v3_Morphology/__init__.py
touch Phase69/__init__.py
```

### Problem: Data files missing

**Solution:** Check symlinks or copy commands worked:

```bash
ls -la data/
# Should show voynich_corpus.txt, latin_corpus.txt, occitan_corpus.txt
```

### Problem: Verification fails

**Solution:** Generate the expected CSV files first:

```bash
# Run your actual analysis scripts to generate CSVs
python N5v3_Morphology/your_morphology_script.py

# This should create results/tables/table1_suffix_inventory.csv
# Then verification will work
```

---

## Quick Reference: File Mapping

| Manuscript Claims | Your Actual File | Action Needed |
|------------------|------------------|---------------|
| `identify_productive_stems.py` | `N5v3_Morphology/...` | Create wrapper |
| `compress_latin.py` | `c01_compare_compression.sh` | Create wrapper |
| `compress_occitan.py` | `c01_compare_compression.sh` | Create wrapper |
| `build_fsm.py` | Phase69 code | Create wrapper |
| `validate_fsm.py` | `p69_validate.py` | Symlink or wrapper |
| `generate_rugg_controls.py` | `rugg_analysis/...` | Create wrapper |

---

## Template Wrapper Script

Use this template for any script:

```python
#!/usr/bin/env python3
"""
Wrapper for [DESCRIBE WHAT THIS DOES]

Maps manuscript file name to actual implementation at:
[PATH TO YOUR ACTUAL SCRIPT]
"""

import sys
import subprocess
from pathlib import Path

# Method 1: Python import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ActualFolder"))
from actual_module import actual_function
actual_function()

# Method 2: Call bash script
# subprocess.run(["bash", "../../actual_script.sh"], check=True)

# Method 3: Call Python script directly
# subprocess.run(["python", "../../actual_script.py"], check=True)

if __name__ == "__main__":
    print("Starting analysis...")
    # Your code here
    print("Complete!")
```

---

## Final Checklist

- [ ] Publication branch created (`paper-2025`)
- [ ] README.md, LICENSE, requirements.txt copied
- [ ] Wrapper scripts created for all claimed files
- [ ] Data files copied or symlinked
- [ ] Results directory set up
- [ ] `run_all_analyses.py` tested
- [ ] Verification scripts pass
- [ ] Branch pushed to GitHub
- [ ] Manuscript URL updated

---

**Once complete, your publication branch will be clean, reviewer-friendly, and match all manuscript claims!**
