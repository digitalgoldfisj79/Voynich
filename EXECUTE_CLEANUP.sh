#!/bin/bash
# Final cleanup: Archive E-space contamination, preserve all V-space

set -e

echo "========================================="
echo "VOYNICHESE V-SPACE PRESERVATION"
echo "========================================="
echo ""

# Create ATTIC structure
mkdir -p ../ATTIC/semantic_pipeline
mkdir -p ../ATTIC/metadata_contaminated  
mkdir -p ../ATTIC/phases_experimental

echo "✅ KEEPING (N1-N2 Validated V-Space):"
echo "  - Phase69, Phase69_Validation (N1 morphology)"
echo "  - PhaseM (morphological expansion)"
echo "  - Phase70 (positional analysis)"
echo "  - Phase90 (token profiling)"
echo "  - Phase110, Phase111 (structural clustering)"
echo "  - PhaseC (compression analysis)"
echo "  - scripts/s0*, s29-s33* (core + slot-rung)"
echo "  - Clean metadata files"
echo ""

echo "📦 ARCHIVING (E-Space Contaminated):"

# Move semantic scripts
for pattern in s10 s11 s12 s13 s14; do
    if ls scripts/${pattern}* 1>/dev/null 2>&1; then
        echo "  Moving scripts/${pattern}*"
        mv scripts/${pattern}*.py ../ATTIC/semantic_pipeline/ 2>/dev/null || true
        mv scripts/${pattern}*.sh ../ATTIC/semantic_pipeline/ 2>/dev/null || true
    fi
done

# Move T3/T4/T5 scripts
for pattern in s100 s101 s102 s103 s104 s105 s106 s110 s112 s120 s130; do
    if ls scripts/${pattern}* 1>/dev/null 2>&1; then
        echo "  Moving scripts/${pattern}*"
        mv scripts/${pattern}*.sh ../ATTIC/semantic_pipeline/ 2>/dev/null || true
    fi
done

# Copy contaminated metadata (keep originals for reference)
echo "  Copying contaminated metadata to ATTIC"
cp metadata/stem_lexicon.tsv ../ATTIC/metadata_contaminated/ 2>/dev/null || true
cp metadata/latin_lemmas_by_domain.tsv ../ATTIC/metadata_contaminated/ 2>/dev/null || true
cp metadata/semantic_family_rules.tsv ../ATTIC/metadata_contaminated/ 2>/dev/null || true

# Move experimental phases
echo "  Moving experimental phases"
for phase in Phase00 Phase20 Phase58 Phase59 Phase71 Phase72 Phase73 Phase74 Phase75 Phase76 Phase77 Phase78 Phase79 Phase80 Phase81 Phase83 Phase95 Phase901; do
    if [ -d "$phase" ]; then
        echo "    - $phase"
        mv "$phase" ../ATTIC/phases_experimental/ 2>/dev/null || true
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Remaining active phases:"
ls -d Phase* 2>/dev/null | sort
echo ""
echo "Active scripts:"
ls scripts/s*.{py,sh} 2>/dev/null | wc -l
echo "scripts remain"

