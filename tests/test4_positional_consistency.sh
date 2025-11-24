#!/usr/bin/env sh
set -eu

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"
T4="$BASE/PhaseT/out/t4_tokens_with_t3.tsv"
CAND="$BASE/PhaseT/out/t3_wave2_candidates.tsv"
OUT="$BASE/tests/out_test4_positional.tsv"

echo "[*] Test4 – positional_role_label consistency → $OUT"
mkdir -p "$BASE/tests"

if [ ! -f "$T4" ]; then
  echo "[ERROR][Test4] Missing T4 file: $T4" >&2
  exit 1
fi

if [ ! -f "$CAND" ]; then
  echo "[ERROR][Test4] Missing candidates file: $CAND" >&2
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
      if ($i=="stem")                 cStem=i
      if ($i=="positional_role_label") cPos=i
    }
    next
  }

  {
    s=$cStem
    pos=$cPos
    if (!(s in stem_list)) next
    total[s]++
    pos_count[s,pos]++
  }

  END {
    OFS="\t"
    print "stem","total","dom_pos_label","dom_count","coverage","entropy_bits"

    for (s in total) {
      t = total[s]
      if (t<=0) continue

      maxc=0
      dom=""
      sumH=0.0

      for (key in pos_count) {
        split(key,a,SUBSEP)
        st=a[1]; pos=a[2]
        if (st!=s) continue
        c=pos_count[key]
        p=c/t
        if (p>0) sumH += -p * (log(p)/log(2))
        if (c>maxc) { maxc=c; dom=pos }
      }

      coverage=maxc/t
      print s, t, dom, maxc, coverage, sumH
    }
  }
' "$CAND" "$T4" > "$OUT"

echo "[✓] Test4 complete → $OUT"
