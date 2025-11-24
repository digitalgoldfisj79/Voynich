#!/bin/bash
# Convert markdown to PDF using pandoc (if available)

if command -v pandoc &> /dev/null; then
    echo "Converting to PDF with pandoc..."
    
    pandoc final_submission/manuscript.md \
           -o final_submission/manuscript.pdf \
           --pdf-engine=pdflatex \
           -V geometry:margin=1in \
           -V fontsize=12pt \
           --toc
    
    echo "✓ Created: final_submission/manuscript.pdf"
else
    echo "pandoc not found. Options:"
    echo "  1. Install pandoc: pkg install pandoc"
    echo "  2. Copy text to Google Docs and export as PDF"
    echo "  3. Use online converter: markdown-to-pdf.com"
fi
