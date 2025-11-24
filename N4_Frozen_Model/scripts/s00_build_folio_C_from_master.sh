#!/usr/bin/env sh
#
# s00 – build folio C-files from IVTFF master transliteration
#
# Usage:
#   BASE="$HOME/Voynich/Voynich_Reproducible_Core" \
#     ./scripts/s00_build_folio_C_from_master.sh \
#       /path/to/voynich_transliteration.txt \
#       f20r f20v f21r f21v
#
# This will create:
#   PhaseS/in/f20r_C.txt
#   PhaseS/in/f20v_C.txt
#   PhaseS/in/f21r_C.txt
#   PhaseS/in/f21v_C.txt
#
# Notes:
#   – Expects IVTFF-style tags like <f21r.1,@P0> etc.
#   – Each C-file contains only the line-level text for that folio
#     (no header line); s41b will happily strip the tags and split on dots.
#

set -eu

if [ "${BASE-}" = "" ]; then
  BASE="$(pwd)"
fi

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 /path/to/voynich_transliteration.txt folio1 [folio2 ...]" >&2
  echo "Example: $0 Phase0/in/voynich_transliteration.txt f20r f20v f21r f21v" >&2
  exit 1
fi

MASTER="$1"
shift

if [ ! -f "$MASTER" ]; then
  echo "[err] master transliteration not found: $MASTER" >&2
  exit 1
fi

OUTD="$BASE/PhaseS/in"
mkdir -p "$OUTD"

for FOLIO in "$@"; do
  OUTFILE="$OUTD/${FOLIO}_C.txt"
  TMP_OUT="${OUTFILE}.tmp"

  echo "[s00] building $OUTFILE from $MASTER"

  # Extract only the line-level records for this folio:
  #   <f21r.1,@P0> ... etc.
  # Keep them as-is; s41b will strip <...> tags and split on dots.
  awk -v folio="$FOLIO" '
    BEGIN { FS = OFS = "\t" }
    $1 ~ "^<"folio"\\." { print $0 }
  ' "$MASTER" > "$TMP_OUT"

  if [ ! -s "$TMP_OUT" ]; then
    echo "[warn] no lines found for folio " "$FOLIO" " in " "$MASTER" >&2
    rm -f "$TMP_OUT"
    continue
  fi

  mv "$TMP_OUT" "$OUTFILE"
  echo "[s00] wrote: $OUTFILE"
done
