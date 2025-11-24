#!/usr/bin/env bash
#
# t01_compile_translations.sh
#
# Minimal Reproducible-Core translation compiler (register- & suffix-aware).
# Inputs:
#   PhaseS/out/p6_folio_tokens.tsv             (tokens with folio,line,pos)
#   PhaseS/out/s50_folio_register_matrix.tsv   (folio -> register, section, currier)
#   PhaseS/out/s46_stem_semantic_envelopes.tsv (stem -> semantic family, role_group,…)
#   metadata/stem_lexicon.tsv                  (stem,register,gloss,notes) [user-editable]
#   metadata/suffix_lexicon.tsv                (suffix,register,role,pos_tag,english_affix) [user-editable]
#
# Output:
#   PhaseT/out/t01_translations.tsv

set -euo pipefail

# --- Locate BASE (repo root) ---
# Assume this script lives in $BASE/scripts
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "${SCRIPT_DIR}/.." && pwd)"

OUTD="${BASE}/PhaseT/out"
mkdir -p "${OUTD}"

P6="${BASE}/PhaseS/out/p6_folio_tokens.tsv"
REGM="${BASE}/PhaseS/out/s50_folio_register_matrix.tsv"
S46="${BASE}/PhaseS/out/s46_stem_semantic_envelopes.tsv"

STEM_LEX="${BASE}/metadata/stem_lexicon.tsv"
SUFFIX_LEX="${BASE}/metadata/suffix_lexicon.tsv"

FOLIO_FILTER="${1:-}"   # optional: limit to one folio like f103r

echo "[t01] BASE:        ${BASE}"
echo "[t01] OUTD:        ${OUTD}"
echo "[t01] P6 tokens:   ${P6}"
echo "[t01] Reg matrix:  ${REGM}"
echo "[t01] S46 stems:   ${S46}"
echo "[t01] Stem lex:    ${STEM_LEX}"
echo "[t01] Suffix lex:  ${SUFFIX_LEX}"
if [ -n "${FOLIO_FILTER}" ]; then
  echo "[t01] Folio filter: ${FOLIO_FILTER}"
fi

# --- Input sanity checks ---
if [ ! -s "${P6}" ]; then
  echo "[t01][ERROR] Missing or empty ${P6}" >&2
  exit 1
fi

if [ ! -s "${REGM}" ]; then
  echo "[t01][ERROR] Missing or empty ${REGM}" >&2
  exit 1
fi

if [ ! -s "${S46}" ]; then
  echo "[t01][ERROR] Missing or empty ${S46}" >&2
  exit 1
fi

mkdir -p "${BASE}/metadata"

# If stem/suffix lexicons don’t exist, create templates so you can fill them.
if [ ! -f "${STEM_LEX}" ]; then
  echo "[t01] Creating template stem lexicon at ${STEM_LEX}"
  {
    echo -e "stem\tregister\tgloss\tnotes"
    # You can later fill this properly; we just seed header.
  } > "${STEM_LEX}"
fi

if [ ! -f "${SUFFIX_LEX}" ]; then
  echo "[t01] Creating template suffix lexicon at ${SUFFIX_LEX}"
  {
    echo -e "suffix\tregister\trole\tpos_tag\tenglish_affix"
    # e.g. "y\tREGISTER_B\tINF_VERB\tV\tto <STEM>"
  } > "${SUFFIX_LEX}"
fi

OUT_TSV="${OUTD}/t01_translations.tsv"

echo "[t01] Writing translations to: ${OUT_TSV}"

python3 << 'PY'
import sys
from pathlib import Path
import pandas as pd

# ------- Config from environment (injected by shell) -------
BASE = Path(".__BASE_PLACEHOLDER__")
OUTD = Path(".__OUTD_PLACEHOLDER__")
P6 = Path(".__P6_PLACEHOLDER__")
REGM = Path(".__REGM_PLACEHOLDER__")
S46 = Path(".__S46_PLACEHOLDER__")
STEM_LEX = Path(".__STEM_LEX_PLACEHOLDER__")
SUFFIX_LEX = Path(".__SUFFIX_LEX_PLACEHOLDER__")
OUT_TSV = Path(".__OUT_TSV_PLACEHOLDER__")
FOLIO_FILTER = ".__FOLIO_FILTER_PLACEHOLDER__"

# The placeholders are replaced below by the shell before python runs.
PY
# now substitute placeholders with real values (safe because we used single-quoted heredoc)
# (We re-open python with the real values)
python3 << PY
from pathlib import Path
import pandas as pd

BASE = Path(r"${BASE}")
OUTD = Path(r"${OUTD}")
P6 = Path(r"${P6}")
REGM = Path(r"${REGM}")
S46 = Path(r"${S46}")
STEM_LEX = Path(r"${STEM_LEX}")
SUFFIX_LEX = Path(r"${SUFFIX_LEX}")
OUT_TSV = Path(r"${OUT_TSV}")
FOLIO_FILTER = r"${FOLIO_FILTER}"

print(f"[t01] (py) BASE = {BASE}")
OUTD.mkdir(parents=True, exist_ok=True)

# ---------- Helpers ----------

def normalise_folio(series):
  """Strip folio markers like 'f103r>    <! ...' down to 'f103r'."""
  return series.astype(str).str.extract(r'^(f[0-9rv]+)', expand=False)

def segment_token(token, suffix_list):
  """
  Very simple longest-suffix match.
  Returns (stem, suffix). If nothing matches, suffix is "" and stem is token.
  """
  t = str(token)
  best_suf = ""
  for suf in suffix_list:
    if t.endswith(suf) and len(suf) > len(best_suf):
      best_suf = suf
  if best_suf:
    stem = t[:-len(best_suf)]
    if stem == "":
      stem = t  # degenerate case; keep full token
      best_suf = ""
  else:
    stem = t
  return stem, best_suf

# ---------- Load inputs ----------

print(f"[t01] (py) Loading tokens from {P6}")
df_tokens = pd.read_csv(P6, sep="\t", dtype=str)
expected_cols = {"token", "folio", "meta", "line", "pos"}
missing = expected_cols - set(df_tokens.columns)
if missing:
  raise ValueError(f"[t01] p6_folio_tokens.tsv missing columns: {missing}")

df_tokens["folio_norm"] = normalise_folio(df_tokens["folio"])

if FOLIO_FILTER and FOLIO_FILTER != "":
  df_tokens = df_tokens[df_tokens["folio_norm"] == FOLIO_FILTER]
  print(f"[t01] (py) After folio filter {FOLIO_FILTER}: {len(df_tokens)} tokens")
  if df_tokens.empty:
    raise SystemExit(f"[t01] No tokens for folio {FOLIO_FILTER}")

print(f"[t01] (py) Tokens loaded: {len(df_tokens)}")

print(f"[t01] (py) Loading register matrix from {REGM}")
df_reg = pd.read_csv(REGM, sep="\t", dtype=str)
if "folio" not in df_reg.columns:
  raise ValueError("[t01] s50_folio_register_matrix.tsv missing 'folio' column")
df_reg["folio_norm"] = normalise_folio(df_reg["folio"])

# Keep only folio-level columns we need
reg_keep = ["folio_norm", "register", "section", "currier", "dominant_semantic_register"]
reg_present = [c for c in reg_keep if c in df_reg.columns]
df_reg = df_reg[reg_present].drop_duplicates()

print(f"[t01] (py) Register rows: {len(df_reg)}")

# Join tokens + register
df = df_tokens.merge(df_reg, on="folio_norm", how="left")
print(f"[t01] (py) After join tokens+reg: {len(df)} rows")
if df["register"].isna().all():
  raise ValueError("[t01] All joined rows have missing register; check s50_folio_register_matrix.tsv")

# ---------- Load S46 stem semantics ----------
print(f"[t01] (py) Loading stem semantic envelopes from {S46}")
df_s46 = pd.read_csv(S46, sep="\t", dtype=str)
# We expect at least these:
# token, structural_class, semantic_family, role_group, primary_section, positional_role_label, best_position
s46_key_cols = set(df_s46.columns)
# Build a lookup by stem (we’ll join after segmentation)
# Use 'token' as stem placeholder; we’ll map by stem name.
if "token" not in df_s46.columns:
  print("[t01] (py) WARNING: S46 missing 'token' column; semantic_family will be NA")
df_s46 = df_s46.rename(columns={"token": "stem"})

df_s46_core = df_s46[["stem"] + [c for c in [
  "structural_class",
  "semantic_family",
  "role_group",
  "primary_section",
  "positional_role_label",
  "best_position"
] if c in df_s46.columns]].drop_duplicates()

print(f"[t01] (py) Unique stems in S46: {df_s46_core['stem'].nunique()}")

# ---------- Load lexicons ----------
print(f"[t01] (py) Loading stem lexicon from {STEM_LEX}")
df_stemlex = pd.read_csv(STEM_LEX, sep="\t", dtype=str)
stemlex_cols = set(df_stemlex.columns)
if not {"stem", "register", "gloss"}.issubset(stemlex_cols):
  print("[t01] (py) WARNING: stem_lexicon.tsv is missing some expected columns; using what we have")

print(f"[t01] (py) Loading suffix lexicon from {SUFFIX_LEX}")
df_suflex = pd.read_csv(SUFFIX_LEX, sep="\t", dtype=str)
suflex_cols = set(df_suflex.columns)
if "suffix" not in suflex_cols:
  print("[t01] (py) WARNING: suffix_lexicon.tsv missing 'suffix' column; suffix roles will be blank")

# Build suffix list for segmentation (longest first)
suffix_list = sorted(
  [s for s in df_suflex.get("suffix", pd.Series([], dtype=str)).dropna().unique() if s != ""],
  key=len,
  reverse=True,
)
# If lexicon empty, fall back to some common suffixes
if not suffix_list:
  suffix_list = ["aiin", "iin", "ain", "am", "al", "ody", "ol", "or", "y"]
  print(f"[t01] (py) Using fallback suffix list: {suffix_list}")
else:
  print(f"[t01] (py) Using suffix list from lexicon ({len(suffix_list)} entries)")

# ---------- Segment tokens ----------
stems = []
suffixes = []
for tok in df["token"]:
  stem, suf = segment_token(tok, suffix_list)
  stems.append(stem)
  suffixes.append(suf)
df["stem"] = stems
df["suffix"] = suffixes

print(f"[t01] (py) Example segmentation (first 5):")
print(df[["folio_norm", "line", "pos", "token", "stem", "suffix"]].head())

# ---------- Attach stem semantics ----------
df = df.merge(df_s46_core, on="stem", how="left", suffixes=("", "_s46"))

# ---------- Attach stem lexicon (register-aware) ----------
# If stem_lexicon has a 'register' column, join on (stem, register).
# If not, join on stem only.
if "register" in df_stemlex.columns:
  df_stemlex_use = df_stemlex.rename(columns={"register": "lex_register"})
  df = df.merge(
    df_stemlex_use,
    left_on=["stem", "register"],
    right_on=["stem", "lex_register"],
    how="left",
    suffixes=("", "_stemlex"),
  )
else:
  df = df.merge(df_stemlex, on="stem", how="left", suffixes=("", "_stemlex"))

# ---------- Attach suffix lexicon (register-aware) ----------
if "register" in df_suflex.columns:
  df_suflex_use = df_suflex.rename(columns={"register": "suf_register"})
  df = df.merge(
    df_suflex_use,
    left_on=["suffix", "register"],
    right_on=["suffix", "suf_register"],
    how="left",
    suffixes=("", "_suflex"),
  )
else:
  df = df.merge(df_suflex, on="suffix", how="left", suffixes=("", "_suflex"))

# ---------- Build a crude English phrase ----------
def build_phrase(row):
  stem = row.get("stem", "")
  suf = row.get("suffix", "")
  reg = row.get("register", "")
  fam = row.get("semantic_family", "")
  role_group = row.get("role_group", "")
  gloss = row.get("gloss", "")
  suf_role = row.get("role", "")
  english_affix = row.get("english_affix", "")

  # Base stem label
  if isinstance(gloss, str) and gloss.strip():
    base = gloss.strip()
  else:
    # fallback to "stem[family]"
    fam_part = fam if isinstance(fam, str) and fam.strip() else "?"
    base = f"{stem}[{fam_part}]"

  # Suffix annotation
  if isinstance(english_affix, str) and english_affix.strip():
    # allow patterns like "to <STEM>" where we insert base
    if "<STEM>" in english_affix:
      phrase = english_affix.replace("<STEM>", base)
    else:
      phrase = f"{base} {english_affix.strip()}"
  elif isinstance(suf_role, str) and suf_role.strip():
    phrase = f"{base} ({suf_role.strip()})"
  elif suf:
    phrase = f"{base}-{suf}"
  else:
    phrase = base

  # Optionally tag register & role_group in brackets
  extra = []
  if isinstance(reg, str) and reg:
    extra.append(reg)
  if isinstance(role_group, str) and role_group:
    extra.append(role_group)
  if extra:
    phrase = f"{phrase} [{'|'.join(extra)}]"

  return phrase

df["english_phrase"] = df.apply(build_phrase, axis=1)

# ---------- Select and write output ----------
cols = [
  "folio_norm",
  "folio",
  "line",
  "pos",
  "section",
  "currier",
  "register",
  "dominant_semantic_register",
  "token",
  "stem",
  "suffix",
  "semantic_family",
  "role_group",
  "structural_class",
  "positional_role_label",
  "best_position",
  "gloss",
  "role",
  "english_affix",
  "english_phrase",
]

present_cols = [c for c in cols if c in df.columns]
df_out = df[present_cols].copy()
df_out = df_out.sort_values(["folio_norm", "line", "pos"], na_position="last")

df_out.to_csv(OUT_TSV, sep="\t", index=False)
print(f"[t01] (py) Wrote {len(df_out)} rows to {OUT_TSV}")
PY

echo "[t01] Done."
