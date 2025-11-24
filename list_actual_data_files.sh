#!/bin/bash

echo "=== FILES WE ACTUALLY HAVE ==="
echo ""
echo "1. In ATTIC/PhaseS_dir/out:"
ls -lh ~/Voynich/ATTIC/PhaseS_dir/out/*folio* 2>/dev/null | head -20

echo ""
echo "2. Specifically looking for p6_folio_tokens.tsv:"
find ~/Voynich -name "p6_folio_tokens.tsv" 2>/dev/null

echo ""
echo "3. Looking for s49b folio-level file:"
find ~/Voynich -name "s49b_folio*" 2>/dev/null

echo ""
echo "4. Check if these exist and show first 5 lines:"
for file in \
    ~/Voynich/ATTIC/PhaseS_dir/out/p6_folio_tokens.tsv \
    ~/Voynich/ATTIC/PhaseS_dir/out/s49b_folio_hand_currier_section.tsv
do
    if [ -f "$file" ]; then
        echo ""
        echo "=== $file ==="
        head -5 "$file"
    else
        echo ""
        echo "NOT FOUND: $file"
    fi
done

