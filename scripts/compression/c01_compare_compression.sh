#!/usr/bin/env sh
# c01_compare_compression.sh
# Compare token-length / compression stats for:
#  - Voynich EVA tokens (p6_voynich_tokens.txt)
#  - Latin expanded corpus (corpora/latin_abbrev_expanded.txt)
#  - Latin compressed corpus (corpora/latin_abbrev_compressed.txt)
#
# Outputs:
#   PhaseC/out/c01_token_length_stats.tsv

set -eu

BASE=${BASE:-"$PWD"}

VOY_TOKENS="$BASE/p6_voynich_tokens.txt"
LAT_EXP="$BASE/corpora/latin_abbrev_expanded.txt"
LAT_COMP="$BASE/corpora/latin_abbrev_compressed.txt"
OUT_DIR="$BASE/PhaseC/out"
OUT_TSV="$OUT_DIR/c01_token_length_stats.tsv"

mkdir -p "$OUT_DIR"

echo "[c01] BASE     = $BASE"
echo "[c01] VOY_TOK  = $VOY_TOKENS"
echo "[c01] LAT_EXP  = $LAT_EXP"
echo "[c01] LAT_COMP = $LAT_COMP"
echo "[c01] OUT_TSV  = $OUT_TSV"

# QC: existence + non-empty
for f in "$VOY_TOKENS" "$LAT_EXP" "$LAT_COMP"; do
  if [ ! -s "$f" ]; then
    echo "[c01][ERROR] missing or empty: $f" >&2
    exit 1
  fi
done

# Helper: compute stats for a "token per line" file, with optional count column
# stdin: lines; if 2nd field is integer, treat as count; else count=1
compute_stats() {
  corpus_label="$1"
  awk -v label="$corpus_label" '
    function is_int(s) { return (s ~ /^[0-9]+$/) }
    BEGIN{
      total_tokens=0;
      total_chars=0;
      long_tokens=0;  # len >=5
      short_tokens=0; # len <=2
    }
    {
      token=$1;
      if (token == "" || token ~ /^#/) next;

      if (NF >= 2 && is_int($2)) {
        c=$2;
      } else {
        c=1;
      }

      len = length(token);
      total_tokens += c;
      total_chars  += c * len;

      if (len >= 5) long_tokens += c;
      if (len <= 2) short_tokens += c;
    }
    END{
      if (total_tokens == 0) {
        mean_len = 0;
        p_ge5 = 0;
        p_le2 = 0;
      } else {
        mean_len = total_chars / total_tokens;
        p_ge5 = long_tokens / total_tokens;
        p_le2 = short_tokens / total_tokens;
      }
      printf("%s\t%d\t%d\t%.6f\t%.6f\t%.6f\n",
             label, total_tokens, total_chars, mean_len, p_ge5, p_le2);
    }
  '
}

# Prepare Latin corpora as "token per line" on the fly (Termux-safe, POSIX)
tmp_exp="$OUT_DIR/c01_latin_exp.tmp"
tmp_comp="$OUT_DIR/c01_latin_comp.tmp"

# Normalise Latin: keep letters only, break on non-letters, lowercase
tr -cs '[:alpha:]' '\n' < "$LAT_EXP"  | tr 'A-Z' 'a-z' | grep -v '^$' > "$tmp_exp"
tr -cs '[:alpha:]' '\n' < "$LAT_COMP" | tr 'A-Z' 'a-z' | grep -v '^$' > "$tmp_comp"

# Header
echo -e "corpus\tN_tokens\tN_chars\tmean_len\tp_len_ge5\tp_len_le2" > "$OUT_TSV"

# Voynich
compute_stats "voynich_eva" < "$VOY_TOKENS" >> "$OUT_TSV"

# Latin expanded (one token per line, no counts)
compute_stats "latin_expanded" < "$tmp_exp" >> "$OUT_TSV"

# Latin compressed
compute_stats "latin_compressed" < "$tmp_comp" >> "$OUT_TSV"

rm -f "$tmp_exp" "$tmp_comp"

echo "[c01] Wrote token-length stats to: $OUT_TSV"
