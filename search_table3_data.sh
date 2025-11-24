#!/bin/bash
set -eu

OUTPUT="TABLE3_SEARCH_RESULTS.txt"

echo "=== SYSTEMATIC SEARCH FOR TABLE 3 DATA ===" > "$OUTPUT"
echo "" >> "$OUTPUT"

echo "1. Searching for the specific KL values from Table 3:" >> "$OUTPUT"
echo "   (9.850, 10.047, 10.283, 10.785, 10.931, 11.048)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Search all TSV files
find . -name "*.tsv" -type f 2>/dev/null | while read f; do
    if grep -q "9.85\|10.047\|10.283\|10.785\|10.931\|11.048" "$f" 2>/dev/null; then
        echo "FOUND in: $f" >> "$OUTPUT"
        grep "9.85\|10.047\|10.283\|10.785\|10.931\|11.048" "$f" >> "$OUTPUT"
        echo "" >> "$OUTPUT"
    fi
done

echo "" >> "$OUTPUT"
echo "2. Searching for scripts that calculate KL divergence:" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Search all Python and shell scripts
find . -name "*.py" -o -name "*.sh" 2>/dev/null | while read f; do
    if grep -qi "kl.*divergence\|divergence.*kl\|currier.*language\|hand.*romance" "$f" 2>/dev/null; then
        echo "Potential match: $f" >> "$OUTPUT"
        grep -n -i "kl\|divergence\|currier.*language\|hand.*romance" "$f" 2>/dev/null | head -5 >> "$OUTPUT"
        echo "" >> "$OUTPUT"
    fi
done

echo "" >> "$OUTPUT"
echo "3. Looking for TSV files with 'currier' or 'hand' and 'language' or 'romance':" >> "$OUTPUT"
echo "" >> "$OUTPUT"

find . -name "*.tsv" -type f 2>/dev/null | while read f; do
    if grep -qi "currier.*latin\|currier.*french\|currier.*occitan\|hand.*latin\|hand.*french" "$f" 2>/dev/null; then
        echo "FOUND: $f" >> "$OUTPUT"
        head -5 "$f" >> "$OUTPUT"
        echo "..." >> "$OUTPUT"
        echo "" >> "$OUTPUT"
    fi
done

echo "" >> "$OUTPUT"
echo "4. List all TSV files in PhaseS, PhaseM, and ATTIC:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
find ./PhaseS ./N4_Frozen_Model/PhaseM ../ATTIC -name "*.tsv" -type f 2>/dev/null | sort >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "5. Check for any files with 'entropy' or 'KL' in the name:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
find . -name "*entropy*" -o -name "*KL*" -o -name "*divergence*" 2>/dev/null >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "6. Check PhaseS/out directory specifically:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
ls -lah PhaseS/out/*.tsv 2>/dev/null >> "$OUTPUT" || echo "PhaseS/out not found" >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "7. Check ../ATTIC/PhaseS_dir/out directory:" >> "$OUTPUT"
echo "" >> "$OUTPUT"
ls -lah ../ATTIC/PhaseS_dir/out/*.tsv 2>/dev/null >> "$OUTPUT" || echo "ATTIC/PhaseS_dir/out not found" >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "SEARCH COMPLETE" >> "$OUTPUT"

