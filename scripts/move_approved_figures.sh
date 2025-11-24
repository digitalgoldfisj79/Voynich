#!/usr/bin/env bash
# POSIX-safe; builds "manuscript_approved" folder with renamed copies of valid figures
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
FIGSRC="$BASE/figures"
FIGDST="$FIGSRC/manuscript_approved"
MANIFEST="$FIGDST/manifest.tsv"

mkdir -p "$FIGDST"

# helper to copy & hash
copy_fig () {
  local src="$1"
  local newname="$2"
  local dest="$FIGDST/$newname"
  if [ ! -f "$src" ]; then
    echo "[warn] missing: $src" >&2
    return
  fi
  cp "$src" "$dest"
  local hash
  hash=$(md5sum "$dest" | awk '{print $1}')
  printf "%s\t%s\t%s\n" "$newname" "$src" "$hash" >> "$MANIFEST"
  echo "[ok] $newname"
}

# reset manifest
echo -e "filename\toriginal_path\tmd5" > "$MANIFEST"

# === MAIN TEXT FIGURES ===
copy_fig "$FIGSRC/Paper6_Fig1_pipeline.png"                  "fig2_1_pipeline.png"
copy_fig "$FIGSRC/fig2_2a_tokens.png"                       "fig2_2a_tokens.png"
copy_fig "$FIGSRC/fig2_2b_types.png"                        "fig2_2b_types.png"
copy_fig "$FIGSRC/fig2_3_entropy_mi.png"                    "fig2_3_entropy_mi.png"
copy_fig "$FIGSRC/fig2_4_conditional_entropy.png"            "fig2_4_conditional_entropy.png"
copy_fig "$FIGSRC/fig2_5_prefix_suffix_heatmap.png"          "fig2_5_prefix_suffix_heatmap.png"
copy_fig "$FIGSRC/Paper4_Fig1_zipf_curve.png"                "fig4_1_zipf_curve.png"
copy_fig "$FIGSRC/Paper2_Fig2_entropy_mi_comparison.png"     "fig6_1_entropy_mi_comparison.png"
copy_fig "$FIGSRC/Paper3_Fig1_sectional_enrichment.png"      "fig7_x_sectional_enrichment.png"
copy_fig "$FIGSRC/fig7_1_prefix_suffix_network.png"          "fig7_1_prefix_suffix_network.png"
copy_fig "$FIGSRC/fig7_2_entropy_by_pos.png"                 "fig7_2_entropy_by_pos.png"
copy_fig "$FIGSRC/fig7_3_stem_suffix_matrix.png"             "fig7_3_stem_suffix_matrix.png"
copy_fig "$FIGSRC/Paper6_Fig3_directional_vectors.png"       "fig8_1_directional_vectors.png"
copy_fig "$FIGSRC/Paper6_Fig6_multilanguage_map.png"         "fig8_2_multilanguage_map.png"

# === APPENDIX FIGURES ===
copy_fig "$FIGSRC/Paper2_Fig1_transliteration_correlation.png" "figB1_transliteration_correlation.png"
copy_fig "$FIGSRC/Paper3_Fig2_cooccurrence_network.png"        "figC1_cooccurrence_network.png"
copy_fig "$FIGSRC/Paper5_Fig4_null_distribution.png"           "figA2_null_distribution.png"
copy_fig "$FIGSRC/Paper6_Fig7_reproducibility.png"             "figA1_reproducibility.png"
copy_fig "$FIGSRC/Paper6_Fig5_uid_mi1.png"                     "figA3_uid_mi1.png"

echo "[done] All approved figures copied to $FIGDST"
echo "[manifest] $(wc -l < "$MANIFEST") entries written to $MANIFEST"
