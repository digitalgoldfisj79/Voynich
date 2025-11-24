#!/usr/bin/env python3
"""
Finalize paper with actual GitHub URL
"""

import re

github_url = "https://github.com/digitalgoldfisj79/voynich-morphology-compression"

print("Finalizing paper with GitHub URL...")

# Read the submission-ready paper
with open('PAPER_SECTION_3_SUBMISSION_READY.md', 'r') as f:
    paper = f.read()

# Replace placeholder with actual URL
paper = paper.replace('[GITHUB_URL]', github_url)
paper = paper.replace('[GITHUB_REPOSITORY_URL]', github_url)

# Save final version
with open('PAPER_SECTION_3_FINAL_SUBMISSION.md', 'w') as f:
    f.write(paper)

print(f"✓ Updated paper with: {github_url}")
print("✓ Created: PAPER_SECTION_3_FINAL_SUBMISSION.md")

# Count placeholders remaining
placeholders = [
    ('[Your names]', 'author names'),
    ('[Your email]', 'contact email'),
    ('[your email]', 'contact email'),
]

remaining = []
for placeholder, desc in placeholders:
    if placeholder in paper:
        remaining.append(desc)

if remaining:
    print("\n⚠️  Still need to add:")
    for item in remaining:
        print(f"    - {item}")
else:
    print("\n✓ All placeholders filled!")

