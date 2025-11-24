#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
cd "$BASE/scripts"

############################################
# 1) Update s20_run_core_context_windows.sh
############################################

cat > s20_run_core_context_windows.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"

CORE_PATH="$BASE/PhaseS/out/s13_semantic_core_report.tsv"
# Default to the *folio-aware* token file
TOKENS_PATH="${TOKENS_PATH:-$BASE/PhaseS/out/p6_folio_tokens.tsv}"
OUT_PATH="$BASE/PhaseS/out/s20_core_context_windows.tsv"

echo "[S20] BASE        = $BASE"
echo "[S20] CORE_PATH   = $CORE_PATH"
echo "[S20] TOKENS_PATH = $TOKENS_PATH"
echo "[S20] OUT_PATH    = $OUT_PATH"

python3 "$BASE/scripts/s20_build_core_context_windows.py" \
  "$CORE_PATH" "$TOKENS_PATH" "$OUT_PATH"
SH

chmod +x s20_run_core_context_windows.sh

############################################
# 2) Update s20_build_core_context_windows.py
#    to understand p6_folio_tokens.tsv format
############################################

cat > s20_build_core_context_windows.py <<'PY'
#!/usr/bin/env python3
import sys
import csv

def load_core_stems(core_path):
    """
    Read core stems from s13_semantic_core_report.tsv.
    Required columns: token, semantic_family, role_group
    """
    core = {}
    with open(core_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            token = row.get("token")
            if not token:
                continue
            family = row.get("semantic_family", "")
            role_group = row.get("role_group", "")
            core[token] = (family, role_group)
    return core

def load_tokens_p6_style(tokens_path):
    """
    Load tokens from PhaseS/out/p6_folio_tokens.tsv.

    Format (no header), e.g.:
      ykal    f1r>    <! $Q=A ... $X=V   1   2

    We only care about:
      token = col[0]
      folio = col[1]
      line  = last-but-one column (int)
      pos   = last column (int)
    """
    tokens = []
    with open(tokens_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            token = parts[0].strip()
            folio = parts[1].strip()
            try:
                line_idx = int(parts[-2])
                pos_idx = int(parts[-1])
            except ValueError:
                line_idx = -1
                pos_idx = -1
            tokens.append({
                "token": token,
                "folio": folio,
                "line": line_idx,
                "pos": pos_idx,
            })
    return tokens

def build_windows(tokens, core_stems, window=2):
    """
    For each core token, capture a ±2 window:
      left2, left1, right1, right2, plus folio/line/pos.
    """
    rows = []
    n = len(tokens)
    for i, tok in enumerate(tokens):
        t = tok["token"]
        if t not in core_stems:
            continue
        family, role_group = core_stems[t]

        left = []
        right = []
        for offset in range(1, window + 1):
            j = i - offset
            left.append(tokens[j]["token"] if j >= 0 else "")
        for offset in range(1, window + 1):
            j = i + offset
            right.append(tokens[j]["token"] if j < n else "")

        row = {
            "center_token": t,
            "family": family,
            "role_group": role_group,
            "left2": left[1] if len(left) > 1 else "",
            "left1": left[0] if len(left) > 0 else "",
            "right1": right[0] if len(right) > 0 else "",
            "right2": right[1] if len(right) > 1 else "",
            "folio": tok["folio"],
            "line": tok["line"],
            "pos": tok["pos"],
        }
        rows.append(row)

    return rows

def main():
    if len(sys.argv) != 4:
        print("Usage: s20_build_core_context_windows.py CORE_TSV TOKENS_TSV OUT_TSV", file=sys.stderr)
        sys.exit(1)

    core_path, tokens_path, out_path = sys.argv[1:4]

    core_stems = load_core_stems(core_path)
    print(f"[S20] Core stems: {len(core_stems)}", file=sys.stderr)

    tokens = load_tokens_p6_style(tokens_path)
    print(f"[S20] Total tokens loaded: {len(tokens)}", file=sys.stderr)

    rows = build_windows(tokens, core_stems, window=2)
    print(f"[S20] Windows built: {len(rows)}", file=sys.stderr)

    fieldnames = [
        "center_token", "family", "role_group",
        "left2", "left1", "right1", "right2",
        "folio", "line", "pos",
    ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

if __name__ == "__main__":
    main()
PY

chmod +x s20_build_core_context_windows.py

echo "[S20-PATCH] Updated s20_run_core_context_windows.sh and s20_build_core_context_windows.py to use PhaseS/out/p6_folio_tokens.tsv."
