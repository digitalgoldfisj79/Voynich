#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
OUT="$BASE/metadata/t3_form_similarity_merged.tsv"

# Input files
S80="$BASE/PhaseT/out/s80_form_similarity.tsv"
S81="$BASE/PhaseT/out/s81_extended_form_similarity.tsv"
S82="$BASE/PhaseT/out/s82_charonly_similarity.tsv"
S83="$BASE/PhaseT/out/s83_charonly_fixed.tsv"

# Sanity checks
for f in "$S80" "$S81" "$S82" "$S83"; do
    if [ ! -s "$f" ]; then
        echo "[s84] ERROR: missing input: $f"
        exit 1
    fi
done

# Merge with awk — prefer S83 > S82 > S81 > S80
# Expected columns:
# stem  latin_candidate  char_cosine  edit_similarity  combined_score  rank  note

awk '
BEGIN {
    FS=OFS="\t"
}
NR==FNR {
    key=$1
    if ( !best[key] || $6 < best_rank[key] ) {
        best[key]=$0
        best_rank[key]=$6
    }
    next
}
{
    key=$1
    if ( !best[key] || $6 < best_rank[key] ) {
        best[key]=$0
        best_rank[key]=$6
    }
}
END {
    print "stem","latin_candidate","char_cosine","edit_similarity","combined_score","rank","note"
    for (k in best) print best[k]
}
' "$S83" "$S82" "$S81" "$S80" > "$OUT.tmp"

mv "$OUT.tmp" "$OUT"

echo "[s84] Wrote merged form similarity to $OUT"
