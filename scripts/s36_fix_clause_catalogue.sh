#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

IN="$BASE/PhaseS/out/s36_clause_role_catalogue.tsv"
OUT_TMP="$BASE/PhaseS/out/s36_clause_role_catalogue.fixed.tmp.tsv"
OUT_FINAL="$BASE/PhaseS/out/s36_clause_role_catalogue.tsv"

echo "[s36_fix] BASE     = $BASE"
echo "[s36_fix] IN       = $IN"
echo "[s36_fix] OUT_TMP  = $OUT_TMP"
echo "[s36_fix] OUT_FINAL= $OUT_FINAL"

if [ ! -s "$IN" ]; then
  echo "[s36_fix] ERROR: missing or empty $IN" >&2
  exit 1
fi

awk -F'\t' '
NR==1 {
  # Force a clean 8-column header
  print "family\trole_group\ttemplate_id\tpattern\tcount\tfamily_total_instances\tcoverage_frac\tclause_role_pattern";
  next
}
{
  fam   = $1
  rg    = $2
  tid   = $3
  pat   = $4
  raw   = $5
  ftotal = ($6 == "" ? "" : $6)
  cov    = ($7 == "" ? "" : $7)
  role   = ($8 == "" ? "" : $8)

  # If count and role are glued like "3AGENT_CAND-...", split them
  count = raw
  if (role == "" && match(raw, /^[0-9]+/)) {
    count = substr(raw, 1, RLENGTH)
    role  = substr(raw, RLENGTH+1)
  }

  # Trim spaces
  gsub(/^ +| +$/, "", count)
  gsub(/^ +| +$/, "", role)
  gsub(/^ +| +$/, "", ftotal)
  gsub(/^ +| +$/, "", cov)

  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",
         fam, rg, tid, pat, count, ftotal, cov, role
}' "$IN" > "$OUT_TMP"

mv "$OUT_TMP" "$OUT_FINAL"
echo "[s36_fix] Done. Patched: $OUT_FINAL"
