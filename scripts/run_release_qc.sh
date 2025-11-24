# scripts/run_release_qc.sh
#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
OUTD="$BASE/figures"; SCRIPTD="$BASE/scripts"
echo "[1/5] Checking core files exist..."
while read -r f; do [ -s "$BASE/$f" ] || { echo "[err] missing $f"; exit 1; }; done < "$BASE/release_core.list"

echo "[2/5] Rebuilding figures from frozen TSVs..."
IN="$BASE/Phase58/out/prefix_suffix_freq.tsv" OUTD="$OUTD" python3 "$SCRIPTD/mk_fig2_5_prefix_suffix_heatmap.py"
IN="$BASE/Phase59/out/prefix_suffix_edges.tsv" OUTD="$OUTD" python3 "$SCRIPTD/mk_fig7_1_prefix_suffix_network.py"
IN="$BASE/Phase70/out/entropy_by_pos.tsv"     OUTD="$OUTD" python3 "$SCRIPTD/mk_fig7_2_entropy_by_pos.py"
IN="$BASE/Phase00/out/section_counts.tsv"     OUTD="$OUTD" python3 "$SCRIPTD/mk_fig2_2_section_counts.py" || true
IN="$BASE/Phase110/out/p110_entropy_mi.tsv"   OUTD="$OUTD" python3 "$SCRIPTD/mk_fig2_3_entropy_mi_scatter.py" || true
IN="$BASE/Phase20/out/conditional_entropy.tsv" OUTD="$OUTD" python3 "$SCRIPTD/mk_fig2_4_conditional_entropy.py" || true
IN="$BASE/Phase59/out/stem_suffix_matrix.tsv" OUTD="$OUTD" python3 "$SCRIPTD/mk_fig7_3_stem_suffix_matrix.py" || true

echo "[3/5] Move figures into manuscript_approved + manifest..."
bash "$SCRIPTD/move_approved_figures.sh"

echo "[4/5] Create release manifest (hashes of critical artefacts)..."
MAN="$BASE/release_manifest.tsv"; echo -e "relpath\tmd5" > "$MAN"
while read -r f; do md5sum "$BASE/$f" | awk '{print $2"\t"$1}'; done < "$BASE/release_core.list" >> "$MAN"
find "$BASE/figures/manuscript_approved" -maxdepth 1 -type f -printf "%P\n" \
  | while read -r img; do md5sum "$BASE/figures/manuscript_approved/$img" | awk '{print "figures/manuscript_approved/"$2"\t"$1}'; done >> "$MAN"

echo "[5/5] Sanity checks (metrics constants)..."
awk -F'\t' 'NR>1{h=$2+0; mi=$3+0} END{ if (mi<1.48 || mi>1.52) {print "[err] MI1 not ~1.50"; exit 1} else print "[ok] MI1 ≈ 1.50"}' "$BASE/Phase110/out/p110_entropy_mi.tsv"
echo "[done] QC complete."
