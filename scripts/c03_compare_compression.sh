#!/usr/bin/env sh
#
# c03_compare_compression.sh
#
# Use c02_compression_metrics.tsv to derive:
#  - bits per char / token (raw & gz)
#  - compression gain
#  - ratios relative to VOYNICH_CORE
#

set -eu

BASE="${BASE:-$PWD}"
OUTD="$BASE/PhaseS/out"
IN="$OUTD/c02_compression_metrics.tsv"
OUT_TSV="$OUTD/c03_compression_comparison.tsv"
OUT_TXT="$OUTD/c03_compression_summary.txt"

echo "[c03] BASE   = $BASE"
echo "[c03] IN     = $IN"
echo "[c03] OUT_TSV= $OUT_TSV"
echo "[c03] OUT_TXT= $OUT_TXT"

if [ ! -s "$IN" ]; then
  echo "[c03] ERROR: missing or empty input: $IN" >&2
  exit 1
fi

# 1) Make TSV with derived metrics
awk -F'\t' '
  NR==1 {
    # header
    print "corpus_name\tn_tokens\tn_types\tmean_token_length\traw_bytes\tgz_bytes\tgz_ratio\tbits_per_char_raw\tbits_per_char_gz\tbits_per_token_raw\tbits_per_token_gz\tcompression_gain\trel_gz_ratio_vs_voynich";
    next;
  }
  NR==2 {
    # assume first data row is VOYNICH_CORE
    voy_gz_ratio = $7 + 0.0;
  }
  {
    corpus   = $1;
    ntok     = $2 + 0.0;
    ntypes   = $3 + 0.0;
    meanlen  = $4 + 0.0;
    rawb     = $5 + 0.0;
    gzb      = $6 + 0.0;
    gzratio  = $7 + 0.0;

    # approximate char count as tokens * mean length
    chars = ntok * meanlen;
    if (chars <= 0 || rawb <= 0 || gzb <= 0) {
      # guard against division by zero
      bpc_raw  = 0;
      bpc_gz   = 0;
      bpt_raw  = 0;
      bpt_gz   = 0;
      gain     = 0;
      rel      = (voy_gz_ratio > 0 ? gzratio / voy_gz_ratio : 0);
    } else {
      bpc_raw  = (rawb * 8.0) / chars;
      bpc_gz   = (gzb  * 8.0) / chars;
      bpt_raw  = (rawb * 8.0) / ntok;
      bpt_gz   = (gzb  * 8.0) / ntok;
      gain     = 1.0 - gzratio;
      rel      = (voy_gz_ratio > 0 ? gzratio / voy_gz_ratio : 0);
    }

    printf "%s\t%d\t%d\t%.6f\t%d\t%d\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n",
           corpus, ntok, ntypes, meanlen, rawb, gzb, gzratio,
           bpc_raw, bpc_gz, bpt_raw, bpt_gz, gain, rel;
  }
' "$IN" > "$OUT_TSV"

# 2) Make a short plain-text summary for the paper
{
  echo "c03 compression comparison summary"
  echo "================================="
  echo
  while IFS=$'\t' read -r corpus ntok ntypes meanlen rawb gzb gzratio bpc_raw bpc_gz bpt_raw bpt_gz gain rel; do
    case "$corpus" in
      corpus_name) continue ;;
    esac
    printf "Corpus: %s\n" "$corpus"
    printf "  tokens:            %s\n" "$ntok"
    printf "  types:             %s\n" "$ntypes"
    printf "  mean token length: %s\n" "$meanlen"
    printf "  gz_ratio:          %.6f (compression gain = %.6f)\n" "$gzratio" "$gain"
    printf "  bits/char (raw):   %.3f\n" "$bpc_raw"
    printf "  bits/char (gz):    %.3f\n" "$bpc_gz"
    printf "  bits/token (raw):  %.3f\n" "$bpt_raw"
    printf "  bits/token (gz):   %.3f\n" "$bpt_gz"
    printf "  rel gz_ratio vs VOYNICH_CORE: %.3f\n" "$rel"
    echo
  done < "$OUT_TSV"
} > "$OUT_TXT"

echo "[c03] Wrote:"
echo "  - $OUT_TSV"
echo "  - $OUT_TXT"
