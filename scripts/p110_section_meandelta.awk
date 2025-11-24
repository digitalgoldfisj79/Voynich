# p110_section_meandelta.awk
# Usage:
#   awk -f scripts/p110_section_meandelta.awk Phase77/out/p77_anchor_families.tsv Phase110/out/p112_attribution.tsv
# Auto-detects header columns in both TSVs and prints section-wise mean Δ with counts.

BEGIN {
  FS = OFS = "\t"
  mode = "p77"
}

# -------- Pass 1: read Phase77/out/p77_anchor_families.tsv --------
FNR == 1 && mode == "p77" {
  # Build header→index map for p77
  delete h77
  for (i=1; i<=NF; i++) {
    h77[$i] = i
  }
  # Find family + section columns (be forgiving about names)
  fam77 = h77["family"] ? h77["family"] : h77["family_signature"]
  if (fam77 == 0) fam77 = 1
  sec77 = h77["section"]
  if (sec77 == 0) sec77 = 2
  next
}

mode == "p77" && FNR > 1 && FILENAME ~ /p77_anchor_families/ {
  fam = $fam77
  sec = $sec77
  if (fam != "" && sec != "") {
    fam2sec[fam] = sec
  }
  next
}

# -------- Switch to Pass 2 when the first file is done --------
FILENAME ~ /p77_anchor_families/ && FNR == NR { next }
FNR == 1 && mode == "p77" {
  # Now reading attribution file
  mode = "attr"
  delete hattr
  for (i=1; i<=NF; i++) {
    hattr[$i] = i
  }
  fam_attr = hattr["family"];          if (fam_attr == 0) fam_attr = 1
  delta_attr = hattr["delta"];         if (delta_attr == 0) delta_attr = 4
  next
}

# -------- Pass 2: read Phase110/out/p112_attribution.tsv --------
mode == "attr" && FNR > 1 {
  famA = $fam_attr
  delt = $delta_attr
  sec  = fam2sec[famA]
  if (sec != "" && delt != "") {
    sum[sec] += delt
    n[sec]++
  }
  next
}

END {
  if (length(n) == 0) {
    print "[warn] No section matches found. Check that families overlap between files or headers are as expected." > "/dev/stderr"
    exit 1
  }
  for (s in n) {
    printf "%s\tmeanΔ=%.4f\tn=%d\n", s, sum[s]/n[s], n[s]
  }
}
