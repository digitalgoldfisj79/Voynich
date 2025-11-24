#!/bin/bash

OUTPUT="FOLIO_LEVEL_DATA_SEARCH.txt"

echo "=== SEARCHING FOR FOLIO-LEVEL TOKEN/SUFFIX DATA ===" > "$OUTPUT"
echo "" >> "$OUTPUT"

echo "1. Looking for folio-level suffix distributions:" >> "$OUTPUT"
find . ~/Voynich/ATTIC -name "*folio*suffix*" -o -name "*suffix*folio*" 2>/dev/null >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "2. Looking for per-folio token files:" >> "$OUTPUT"
find . ~/Voynich/ATTIC -name "*folio*token*" -o -name "*token*folio*" 2>/dev/null | head -20 >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "3. Check PhaseM for folio-level analysis:" >> "$OUTPUT"
find N4_Frozen_Model/PhaseM -name "*folio*" 2>/dev/null >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "4. Check if EVA transcription has folio markers:" >> "$OUTPUT"
head -50 corpora/voynich_eva.txt 2>/dev/null | grep -i "folio\|<f" >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "5. Look for the actual EVA file with folio markers:" >> "$OUTPUT"
find . ~/Voynich/ATTIC -name "*.eva" -o -name "*voynich*.txt" -o -name "*transcription*" 2>/dev/null | head -10 >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "6. Check metadata directory:" >> "$OUTPUT"
ls -la metadata/ 2>/dev/null >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "SEARCH COMPLETE" >> "$OUTPUT"

