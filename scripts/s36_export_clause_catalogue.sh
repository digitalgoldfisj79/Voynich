#!/usr/bin/env bash
set -eu

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
IN="$BASE/PhaseS/out/s35_clause_role_patterns.tsv"
OUT="$BASE/PhaseS/out/s36_clause_role_catalogue.tsv"

if [ ! -f "$IN" ]; then
  echo "[s36] ERROR: missing input: $IN" >&2
  exit 1
fi

mkdir -p "$BASE/PhaseS/out"

tmp_body="$OUT.body.tmp"
tmp_out="$OUT.tmp"

# Project just the columns we care about, drop header for sorting
# Expected s35 header:
# family role_group template_id pattern count family_total_instances coverage_frac L_token C_token R_token L_role C_role R_role clause_role_pattern
awk -F'\t' 'NR>1 {
  print $1 FS $2 FS $3 FS $4 FS $5 FS $6 FS $7 FS $14
}' "$IN" > "$tmp_body"

{
  printf 'family\trole_group\ttemplate_id\tpattern\tcount\tfamily_total_instances\tcoverage_frac\tclause_role_pattern\n'
  # Sort by family then descending coverage
  sort -t '	' -k1,1 -k7,7nr "$tmp_body"
} > "$tmp_out"

mv "$tmp_out" "$OUT"
rm -f "$tmp_body"

echo "[s36] Wrote catalogue to: $OUT"
