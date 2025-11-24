#!/usr/bin/env sh
# Fix S35 clause role patterns by restoring counts and coverage
# from S34 clause templates.

set -eu

# 1) Resolve BASE and paths (Termux-safe)
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN_TEMPL="${IN_TEMPL:-$BASE/PhaseS/out/s34_clause_templates.tsv}"
IN_ROLES="${IN_ROLES:-$BASE/PhaseS/out/s35_clause_role_patterns.tsv}"
OUT_TSV="${OUT_TSV:-$BASE/PhaseS/out/s35_clause_role_patterns_fixed.tsv}"
OUT_TXT="${OUT_TXT:-$BASE/PhaseS/out/s35_clause_role_patterns_fixed.txt}"

echo "[s35_fix] BASE     = $BASE"
echo "[s35_fix] IN_TEMPL = $IN_TEMPL"
echo "[s35_fix] IN_ROLES = $IN_ROLES"
echo "[s35_fix] OUT_TSV  = $OUT_TSV"
echo "[s35_fix] OUT_TXT  = $OUT_TXT"

# 2) Sanity checks
for p in "$IN_TEMPL" "$IN_ROLES"; do
  if [ ! -f "$p" ]; then
    echo "[s35_fix] ERROR: missing input: $p" >&2
    exit 1
  fi
done

tmp_tsv="${OUT_TSV}.tmp"

# 3) Join S34 (true counts) into S35 (role labels) by template_id
awk -F'\t' '
  ####################################################################
  # First pass: read S34 templates, remember count, family_total_instances,
  # and coverage_frac per template_id.
  ####################################################################
  NR==FNR {
    if (NR == 1) {
      for (i = 1; i <= NF; i++) {
        if ($i == "template_id")           c_tid  = i
        else if ($i == "count")            c_cnt  = i
        else if ($i == "family_total_instances") c_ftot = i
        else if ($i == "coverage_frac")    c_cov  = i
      }
      next
    }
    tid = $c_tid
    tmpl_cnt[tid]  = $c_cnt
    tmpl_ftot[tid] = $c_ftot
    tmpl_cov[tid]  = $c_cov
    next
  }

  ####################################################################
  # Second pass: S35 patterns; overwrite zero/blank count & coverage
  # using the S34 values where available.
  ####################################################################
  FNR == 1 {
    for (i = 1; i <= NF; i++) {
      if ($i == "template_id")             c_tid2  = i
      else if ($i == "count")              c_cnt2  = i
      else if ($i == "family_total_instances") c_ftot2 = i
      else if ($i == "coverage_frac")      c_cov2  = i
    }
    print $0
    next
  }

  tid = $c_tid2
  if (tid in tmpl_cnt) {
    $c_cnt2  = tmpl_cnt[tid]
    $c_ftot2 = tmpl_ftot[tid]
    $c_cov2  = tmpl_cov[tid]
  }
  print $0
' "$IN_TEMPL" "$IN_ROLES" > "$tmp_tsv"

mv "$tmp_tsv" "$OUT_TSV"

# 4) Compact text summary (optional, like the other S* summaries)
{
  echo "S35 clause role patterns (fixed counts)"
  echo "======================================="
  awk -F"\t" '
    NR == 1 {
      for (i = 1; i <= NF; i++) {
        if ($i == "family")              c_fam = i
        else if ($i == "clause_role_pattern") c_pat = i
        else if ($i == "coverage_frac")  c_cov = i
      }
      next
    }
    fam = $c_fam
    pat = $c_pat
    cov = ($c_cov == "" ? 0 : $c_cov + 0)
    key = fam "|" pat
    n[key]++
    covsum[key] += cov
    END {
      for (key in n) {
        split(key, a, "|")
        fam = a[1]
        pat = a[2]
        printf "Family: %s, pattern=%s, n_templates=%d, total_coverage≈%.4f\n",
               fam, pat, n[key], covsum[key]
      }
    }
  ' "$OUT_TSV" | sort
} > "$OUT_TXT"

echo "[s35_fix] Done. Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_TXT"
