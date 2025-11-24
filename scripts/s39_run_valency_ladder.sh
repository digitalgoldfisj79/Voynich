#!/data/data/com.termux/files/usr/bin/sh
# S39: Build valency-aware ladder table from S38
# Inputs:
#   PhaseS/out/s38_valency_table.tsv
# Outputs:
#   PhaseS/out/s39_valency_ladder.tsv
#   PhaseS/out/s39_valency_ladder.txt

set -eu

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"

IN_S38="$BASE/PhaseS/out/s38_valency_table.tsv"
OUT_TSV="$BASE/PhaseS/out/s39_valency_ladder.tsv"
OUT_TXT="$BASE/PhaseS/out/s39_valency_ladder.txt"
TMP_TSV="$OUT_TSV.tmp.$$"
TMP_TXT="$OUT_TXT.tmp.$$"

echo "[S39] BASE    = $BASE"
echo "[S39] IN_S38  = $IN_S38"
echo "[S39] OUT_TSV = $OUT_TSV"
echo "[S39] OUT_TXT = $OUT_TXT"

# Basic checks
if [ ! -s "$IN_S38" ]; then
  echo "[S39] ERROR: missing or empty $IN_S38" >&2
  exit 1
fi

# Build ladder TSV
awk -F'\t' '
BEGIN {
  OFS = "\t"
}
NR == 1 {
  # Expected S38 columns (by position):
  # 1 family
  # 2 agent_suffix
  # 3 patient_suffix
  # 4 n_templates
  # 5 total_clause_count
  # 6 approx_coverage
  # 7 valency_id
  # 8 ladder_pattern
  # (9+ may exist but we ignore them)
  print "family", "agent_suffix", "patient_suffix",
        "valency_id", "ladder_pattern",
        "valency_class", "verb_slot_hint",
        "confidence", "notes"
  next
}
{
  fam  = $1
  a_suf = $2
  p_suf = $3
  n_tpl = ($4 == "" ? 0 : $4 + 0)
  t_cnt = ($5 == "" ? 0 : $5 + 0)
  cov   = ($6 == "" ? 0 : $6 + 0)
  vid   = (NF >= 7 ? $7 : "")
  ladd  = (NF >= 8 ? $8 : "AGENT>PROCESS>PATIENT")

  # --- valency class based on approx_coverage ---
  # You can tighten these thresholds later if S37 grows.
  vc = "VAL_WEAK"
  conf = 0.50
  if (cov >= 3.0) {
    vc = "VAL_STRONG"
    conf = 0.90
  } else if (cov >= 2.0) {
    vc = "VAL_MEDIUM"
    conf = 0.70
  }

  # --- verb-slot hint: very simple for now ---
  # All of these are 3-place, transitive-ish clauses:
  #   AGENT (suffix a_suf) acts on PATIENT (suffix p_suf)
  vhint = "AGENT_ACTS_ON_PATIENT"

  # --- notes: compact human-readable summary ---
  notes = sprintf("n_templates=%d;total_count=%d;approx_cov=%.2f",
                  n_tpl, t_cnt, cov)

  print fam, a_suf, p_suf,
        vid, ladd,
        vc, vhint,
        conf, notes
}
' "$IN_S38" > "$TMP_TSV"

# Quick sanity: non-empty and more than header
lines=$(wc -l < "$TMP_TSV" || echo 0)
if [ "$lines" -le 1 ]; then
  echo "[S39] ERROR: produced ladder file has no data rows: $TMP_TSV" >&2
  rm -f "$TMP_TSV"
  exit 1
fi

# Build text summary
awk -F'\t' '
NR == 1 { next }
{
  fam = $1
  vc  = $6
  conf = $8 + 0
  fam_count[fam]++
  vc_count[vc]++
  fam_conf_sum[fam] += conf
}
END {
  printf "S39 valency ladder summary\n"
  printf "==========================\n\n"
  printf "Total valency rules: %d\n\n", NR-1

  printf "By valency class:\n"
  for (vc in vc_count) {
    printf "  - %s: %d\n", vc, vc_count[vc]
  }
  printf "\nBy family (with mean confidence):\n"
  for (fam in fam_count) {
    n = fam_count[fam]
    mean_c = (n > 0 ? fam_conf_sum[fam] / n : 0.0)
    printf "  - %s: n=%d, mean_conf=%.3f\n", fam, n, mean_c
  }
}
' "$TMP_TSV" > "$TMP_TXT"

# Atomic move
mv "$TMP_TSV" "$OUT_TSV"
mv "$TMP_TXT" "$OUT_TXT"

echo "[S39] Done. Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_TXT"
