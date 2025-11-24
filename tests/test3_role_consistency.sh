#!/usr/bin/env sh
set -eu

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"
T4="$BASE/PhaseT/out/t4_tokens_with_t3.tsv"
CAND="$BASE/PhaseT/out/t3_wave2_candidates.tsv"
OUT="$BASE/tests/out_test3_role_consistency.tsv"

echo "[*] Test3 – role_group consistency → $OUT"
mkdir -p "$BASE/tests"

if [ ! -f "$T4" ]; then
  echo "[ERROR][Test3] Missing T4 file: $T4" >&2
  exit 1
fi

if [ ! -f "$CAND" ]; then
  echo "[ERROR][Test3] Missing candidates file: $CAND" >&2
  exit 1
fi

awk -F"\t" '
  NR==FNR {
    if (FNR==1) next
    stem_list[$1]=1
    next
  }

  FNR==1 {
    for (i=1;i<=NF;i++) {
      if ($i=="stem")       cStem=i
      if ($i=="role_group") cRole=i
    }
    next
  }

  {
    s=$cStem
    rg=$cRole
    if (!(s in stem_list)) next
    total[s]++
    role_count[s,rg]++
  }

  END {
    OFS="\t"
    print "stem","total","dom_role_group","dom_count","coverage","entropy_bits"

    for (s in total) {
      t = total[s]
      if (t<=0) continue

      maxc=0
      dom=""
      sumH=0.0

      # pass 1: find dom + entropy
      for (key in role_count) {
        split(key,a,SUBSEP)
        st=a[1]; rg=a[2]
        if (st!=s) continue
        c = role_count[key]
        p = c / t
        if (p>0) sumH += -p * (log(p)/log(2))
        if (c>maxc) { maxc=c; dom=rg }
      }

      coverage = maxc / t
      print s, t, dom, maxc, coverage, sumH
    }
  }
' "$CAND" "$T4" > "$OUT"

echo "[✓] Test3 complete → $OUT"
