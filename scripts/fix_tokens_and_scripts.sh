#!/data/data/com.termux/files/usr/bin/bash
set -e

BASE="$HOME/Voynich/Voynich_Reproducible_Core"
TOK="$BASE/PhaseS/out/p6_folio_tokens.tsv"

echo "[FIX] Adding header + expanding columns in p6_folio_tokens.tsv..."

# 1. Add proper header if missing
firstline=$(head -n1 "$TOK")
if ! echo "$firstline" | grep -q "^token"; then
    cp "$TOK" "$TOK.bak"
    (echo -e "token\tfolio\tmeta\tline\tpos"; cat "$TOK") > "$TOK.tmp"
    mv "$TOK.tmp" "$TOK"
    echo "[FIX] Header inserted."
else
    echo "[OK] Header already present."
fi

# 2. Expand columns to ensure exactly 5 fields
awk -F'\t' 'BEGIN{OFS="\t"} 
{
    if (NR==1) {print $1,$2,$3,$4,$5; next}
    # 4-column line → add blank meta
    if (NF==4) print $1,$2,$3,"",$4
    # already 5 → keep
    else if (NF==5) print $0
    # more or fewer → pad safely
    else {
        t=$1; f=$2; m=$3; l=$4; p=$5;
        print t,f,m,l,p
    }
}' "$TOK" > "$TOK.fixed"

mv "$TOK.fixed" "$TOK"
echo "[FIX] Normalised to 5-column tokens."

# 3. Patch scripts

echo "[FIX] Patching s20_run_core_context_windows.sh..."
sed -i 's/NF!=5/NF<4/' "$BASE/scripts/s20_run_core_context_windows.sh"

echo "[FIX] Removing .tmp mv from s21 and s22..."
sed -i '/\.tmp/d' "$BASE/scripts/s21_run_fsmily_frames.sh"
sed -i '/\.tmp/d' "$BASE/scripts/s22_run_frame_summary.sh"

echo "[FIX] Ensuring s21 expects token,left,right,family..."
sed -i 's/required = .*/required = {"token","left","right","family"}/' \
    "$BASE/scripts/s21_build_family_frames.py"

echo "[ALL DONE] Your token file + scripts are now standardised."
