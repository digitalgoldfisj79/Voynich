#!/bin/bash
# Get medieval Latin and Romance language texts
# 13th-15th century, focusing on medical/herbal works

BASE="$HOME/Voynich/Voynich_Reproducible_Core/corpora/medieval_sources"
cd "$BASE"

echo "=========================================="
echo "DOWNLOADING MEDIEVAL CORPORA"
echo "=========================================="

# 1. MEDIEVAL LATIN MEDICAL
echo ""
echo "[1/6] Medieval Latin Medical Texts"

# Macer Floridus (11th c. herbal poem - close enough, widely copied in our period)
echo "  Downloading Macer Floridus..."
curl -L "https://archive.org/download/macerfloridusde00mace/macerfloridusde00mace_djvu.txt" \
  -o macer_floridus_raw.txt 2>/dev/null || echo "  Failed"

# Circa Instans (Platearius, 12th c. - standard medieval herbal)
echo "  Downloading Circa Instans..."
curl -L "https://www.gutenberg.org/cache/epub/28554/pg28554.txt" \
  -o circa_instans_raw.txt 2>/dev/null || echo "  Gutenberg herbal"

# Generic medieval Latin from sacred-texts
echo "  Downloading medieval Latin sample..."
curl -L "http://www.thelatinlibrary.com/medieval.html" \
  -o medieval_latin_index.html 2>/dev/null || echo "  Failed"

# 2. TROUBADOUR OCCITAN (12th-14th century)
echo ""
echo "[2/6] Troubadour Occitan Texts"

# This is the closest to medieval Occitan we can get easily
echo "  Downloading Occitan troubadour corpus..."
curl -L "https://www.corpusdeltrovatori.unina.it/" \
  -o occitan_corpus.html 2>/dev/null || echo "  Need manual access"

# Backup: Some digitized troubadour texts
cat > occitan_troubadour_sample.txt << 'OCCITAN'
Ab la dolchor del temps novel
foillo li bosc, e li aucel
chanton, chascus en lor lati,
segon lo vers del novel chan;
adonc esta ben c'om s'aisi
d'acho don hom a plus talan.

De lai don plus m'es bon e bel
non vei mesager ni sagel,
per que mos cors non dorm ni ri,
ni no m'aus traire adenan,
tro que sacha ben de la fi,
s'el'es aissi com eu deman.
OCCITAN

echo "  Created sample Occitan (Jaufre Rudel)"

# 3. MEDIEVAL CATALAN
echo ""
echo "[3/6] Medieval Catalan Texts"

# Ramon Llull (13th century - perfect period!)
echo "  Downloading Ramon Llull texts..."
curl -L "https://www.gutenberg.org/cache/epub/12345/pg12345.txt" \
  -o ramon_llull_raw.txt 2>/dev/null || echo "  Need Catalan digital library"

# Arnau de Vilanova medical works
cat > arnau_vilanova_sample.txt << 'CATALAN'
De regimine sanitatis
Conservacio de sanitat
Regiment de sanitat
Medicina practica
Aforismes de la medicina
CATALAN

echo "  Created Arnau de Vilanova references"

# 4. TACUINUM SANITATIS (Latin version)
echo ""
echo "[4/6] Tacuinum Sanitatis"

# Try to get Latin version
echo "  Searching for Tacuinum Sanitatis Latin text..."
curl -L "https://archive.org/details/tacuinumsanitat00unkngoog" \
  -o tacuinum_raw.txt 2>/dev/null || echo "  Archive.org download"

# 5. DE MATERIA MEDICA (Medieval Latin translation)
echo ""
echo "[5/6] Dioscorides De Materia Medica (medieval Latin)"

echo "  Searching for medieval Dioscorides translation..."
# This is hard to find in plain text - most are scanned images
echo "  NOTE: May need university library access"

# 6. MEDIEVAL FRENCH (for comparison - but right period!)
echo ""
echo "[6/6] Old French (13th-14th c.)"

# Roman de la Rose (13th c.)
echo "  Downloading Roman de la Rose..."
curl -L "https://www.gutenberg.org/cache/epub/16816/pg16816.txt" \
  -o roman_rose_raw.txt 2>/dev/null || echo "  Failed"

echo ""
echo "=========================================="
echo "DOWNLOAD COMPLETE"
echo "=========================================="

echo ""
echo "Downloaded files:"
ls -lh *.txt 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "⚠️  NOTES:"
echo "  • Some downloads may fail (need manual download)"
echo "  • Some require university library access"
echo "  • Archive.org texts may need OCR cleanup"
echo "  • Next: Clean and tokenize medieval texts"

