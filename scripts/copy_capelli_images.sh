#!/usr/bin/env bash
set -euo pipefail

# Root of your Voynich repo
BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

# Source directory on Android (note the quotes for spaces)
SRC="/storage/emulated/0/hazel zip extractor/extracted/cappelli/img_abbr"

# Destination inside the repo
DEST="$BASE/capelli_imgs"

# List of page_ids to copy (one per line)
LIST="$BASE/capelli_page_ids.list"

mkdir -p "$DEST"

if [ ! -r "$LIST" ]; then
  cat << 'LEND' > "$LIST"
# Put one page number per line (these map to N.jpg in SRC)
# Example starter set from our figure plan:
1
2
3
68
185
199
212
261
264
300
301
302
310
363
366
LEND
  echo "[info] Created $LIST. Edit this file to adjust the page numbers, then rerun this script."
fi

echo "[info] Copying Capelli images listed in $LIST"
while IFS= read -r nid; do
  case "$nid" in
    ""|\#*) continue ;;  # skip empty lines and comments
  esac

  # strip any whitespace
  id=$(printf '%s' "$nid" | tr -d '[:space:]')

  src_file="$SRC/$id.jpg"
  if [ ! -f "$src_file" ]; then
    echo "[warn] missing source: $src_file" >&2
    continue
  fi

  # Normalise name as capelli_XXXX.jpg (zero-padded)
  dest_file=$(printf '%s/cappelli_%04d.jpg' "$DEST" "$id")

  cp "$src_file" "$dest_file"
  echo "[ok] copied $src_file -> $dest_file"
done < "$LIST"

echo "[done] Capelli images are now in: $DEST"
