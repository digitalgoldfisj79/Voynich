#!/usr/bin/env bash
#
# C02 – Compression comparison: Voynich vs Latin (compressed/expanded)
# Uses token lists to compute:
# - n_tokens, n_types
# - mean token length
# - raw bytes
# - gzip-compressed bytes
# - compression ratio (gz_bytes / raw_bytes)
#
# Inputs (expected):
#   $BASE/p6_voynich_tokens.txt
#   $BASE/corpora/latin_abbrev_compressed.txt
#   $BASE/corpora/latin_abbrev_expanded.txt
#
# Output:
#   $BASE/PhaseS/out/c02_compression_metrics.tsv

set -eu

# --- Resolve BASE safely ----------------------------------------------------

if [ "${BASE:-}" = "" ]; then
  BASE="$(pwd)"
fi

OUT_DIR="$BASE/PhaseS/out"
mkdir -p "$OUT_DIR"

OUT_TSV="$OUT_DIR/c02_compression_metrics.tsv"
TMP_TSV="$OUT_TSV.tmp"

# --- Helper: die with message ----------------------------------------------

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

# --- Check inputs -----------------------------------------------------------

VOYNICH_TOKENS="$BASE/p6_voynich_tokens.txt"

CORPORA_DIR="$BASE/corpora"
LATIN_COMPRESSED="$CORPORA_DIR/latin_abbrev_compressed.txt"
LATIN_EXPANDED="$CORPORA_DIR/latin_abbrev_expanded.txt"

[ -s "$VOYNICH_TOKENS" ]       || die "[c02] ERROR: missing or empty $VOYNICH_TOKENS"
[ -s "$LATIN_COMPRESSED" ]     || die "[c02] ERROR: missing or empty $LATIN_COMPRESSED"
[ -s "$LATIN_EXPANDED" ]       || die "[c02] ERROR: missing or empty $LATIN_EXPANDED"

# --- Function to compute metrics for a tokens file -------------------------
# Expects: one token per line (empty lines ignored)
# Prints a single TSV line to stdout:
#   corpus_name  n_tokens  n_types  mean_len  raw_bytes  gz_bytes  gz_ratio

compute_metrics() {
  corpus_name="$1"
  file_path="$2"

  # Guard: file should be non-empty, but we already checked above
  if [ ! -s "$file_path" ]; then
    return 0
  fi

  # token + type counts and mean length via awk + sort
  # We ignore blank lines defensively.
  stats="$(awk '
    NF > 0 {
      n_tokens++;
      n_chars += length($0);
      freq[$0]++;
    }
    END {
      n_types = 0;
      for (t in freq) { n_types++ }
      if (n_tokens > 0) {
        mean_len = n_chars / n_tokens;
      } else {
        mean_len = 0;
      }
      printf "%d\t%d\t%.6f\n", n_tokens, n_types, mean_len;
    }
  ' "$file_path")"

  n_tokens=$(printf '%s\n' "$stats" | awk -F'\t' '{print $1}')
  n_types=$(printf '%s\n'  "$stats" | awk -F'\t' '{print $2}')
  mean_len=$(printf '%s\n' "$stats" | awk -F'\t' '{print $3}')

  # raw bytes
  raw_bytes=$(wc -c < "$file_path" | awk '{print $1}')

  # gzip-compressed bytes (no tmp files; stream to wc)
  gz_bytes=$(gzip -c "$file_path" | wc -c | awk '{print $1}')

  # compression ratio
  if [ "$raw_bytes" -gt 0 ]; then
    # use awk for portable float division
    gz_ratio=$(printf '%s\t%s\n' "$gz_bytes" "$raw_bytes" | awk '
      { printf "%.6f\n", $1 / $2 }
    ')
  else
    gz_ratio="0.000000"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$corpus_name" "$n_tokens" "$n_types" "$mean_len" "$raw_bytes" "$gz_bytes" "$gz_ratio"
}

# --- Write header -----------------------------------------------------------

{
  printf 'corpus_name\tn_tokens\tn_types\tmean_token_length\traw_bytes\tgz_bytes\tgz_ratio\n'

  compute_metrics "VOYNICH_CORE"          "$VOYNICH_TOKENS"
  compute_metrics "LATIN_COMPRESSED"      "$LATIN_COMPRESSED"
  compute_metrics "LATIN_EXPANDED"        "$LATIN_EXPANDED"

} > "$TMP_TSV"

mv "$TMP_TSV" "$OUT_TSV"

printf '[c02] Wrote compression metrics to: %s\n' "$OUT_TSV"
