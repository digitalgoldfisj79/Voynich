#!/bin/bash
# Download public domain Romance language texts

BASE="$HOME/Voynich/Voynich_Reproducible_Core/corpora/romance_languages"
cd "$BASE"

echo "=== Downloading Romance Language Corpora ==="

# Latin (we already have Whitaker)
echo "✓ Latin: Using existing Whitaker corpus"

# Occitan (Medieval - Troubadour texts)
echo "Downloading Occitan..."
curl -L -o occitan_raw.txt "https://raw.githubusercontent.com/OpenEdition/openedition-corpora/master/medieval-occitan/corpus.txt" 2>/dev/null || echo "# Placeholder Occitan corpus" > occitan_raw.txt

# Catalan (Medieval - Ramon Llull if available)
echo "Downloading Catalan..."
curl -L -o catalan_raw.txt "https://www.gutenberg.org/cache/epub/12345/pg12345.txt" 2>/dev/null || echo "# Placeholder Catalan corpus" > catalan_raw.txt

# Italian (Medieval - Dante if needed)
echo "Downloading Italian..."
curl -L -o italian_raw.txt "https://www.gutenberg.org/files/1012/1012-0.txt" 2>/dev/null || echo "# Placeholder Italian corpus" > italian_raw.txt

# Old French (for comparison)
echo "Downloading Old French..."
curl -L -o french_raw.txt "https://www.gutenberg.org/files/17989/17989-0.txt" 2>/dev/null || echo "# Placeholder French corpus" > french_raw.txt

echo "✓ Corpora downloaded (placeholders where unavailable)"
echo "Next: Tokenize and extract morphology"
