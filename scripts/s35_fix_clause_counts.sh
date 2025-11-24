#!/usr/bin/env bash
# s35_fix_clause_counts.sh
# Patch clause counts in s35_clause_role_patterns.tsv
# using triple counts from S32 (cross-position dependencies).

set -eu

# 1) Resolve BASE
if [ -n "${BASE:-}" ]; then
  BASE="$BASE"
else
  BASE="$(pwd)"
fi

echo "[s35_fix] BASE     = $BASE"

# 2) Locate S32 (cross-position) file
P32_CROSS="$BASE/PhaseS/out/s32_cross_position.tsv"
P32_SLOT="$BASE/PhaseS/out/s32_slot_dependencies.tsv"

if [ -f "$P32_CROSS" ]; then
  P32="$P32_CROSS"
elif [ -f "$P32_SLOT" ]; then
  P32="$P32_SLOT"
else
  echo "[s35_fix] ERROR: no S32 file found."
  echo "  Tried:"
  echo "    $P32_CROSS"
  echo "    $P32_SLOT"
  exit 1
fi

# 3) Locate S35 roles file
P35="$BASE/PhaseS/out/s35_clause_role_patterns.tsv"

if [ ! -s "$P35" ]; then
  echo "[s35_fix] ERROR: missing or empty $P35"
  exit 1
fi

OUT_TMP="$BASE/PhaseS/out/s35_clause_role_patterns.tmp.tsv"
OUT_FINAL="$P35"

echo "[s35_fix] P32      = $P32"
echo "[s35_fix] P35      = $P35"
echo "[s35_fix] OUT_TMP  = $OUT_TMP"
echo "[s35_fix] OUT_FINAL= $OUT_FINAL"

# 4) Build key->count map from S32 and patch S35
awk -F'\t' -v OFS='\t' '
  BEGIN {
    # nothing
  }

  # --- Pass 1: S32 (cross-position / slot dependencies) ---
  FNR==1 && NR==1 {
    # first file header (S32) – detect column indices
    for (i=1; i<=NF; i++) {
      if ($i=="left_token")   lt_i=i
      else if ($i=="centre_token" || $i=="center_token") ct_i=i
      else if ($i=="right_token")  rt_i=i
      else if ($i=="triple_count") tc_i=i
    }
    next
  }

  NR==FNR {
    # still in first file (S32 data)
    if (lt_i==0 || ct_i==0 || rt_i==0 || tc_i==0) next
    if ($lt_i=="" || $ct_i=="" || $rt_i=="") next
    key = $lt_i "|" $ct_i "|" $rt_i
    # accumulate triple_count in case of duplicates
    cnt[key] += ($tc_i=="" ? 0 : $tc_i+0)
    next
  }

  # --- Pass 2: S35 (roles file) ---
  FNR==1 {
    # header for S35 – detect indices; print as-is
    for (i=1; i<=NF; i++) {
      if ($i=="count")         count_i=i
      else if ($i=="family_total_instances") fam_i=i
      else if ($i=="coverage_frac")          cov_i=i
      else if ($i=="L_token")               lt2_i=i
      else if ($i=="C_token")               ct2_i=i
      else if ($i=="R_token")               rt2_i=i
    }
    print
    next
  }

  {
    # data rows in S35
    if (lt2_i==0 || ct2_i==0 || rt2_i==0 || count_i==0) {
      # something is wrong with header – just print original
      print
      next
    }

    l = $lt2_i
    c = $ct2_i
    r = $rt2_i
    key = l "|" c "|" r

    new_count = (key in cnt ? cnt[key] : 0)

    # update count
    $count_i = new_count

    # update coverage_frac if family_total_instances is available
    if (cov_i > 0 && fam_i > 0 && $fam_i != "" && $fam_i != "NA") {
      fam = $fam_i + 0
      if (fam > 0) {
        cov = new_count / fam
        $cov_i = cov
      } else {
        $cov_i = ""
      }
    }

    print
  }
' "$P32" "$P35" > "$OUT_TMP"

# 5) Atomic move
mv "$OUT_TMP" "$OUT_FINAL"

echo "[s35_fix] Done. Patched counts into: $OUT_FINAL"
