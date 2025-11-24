#!/usr/bin/env sh
set -eu

BASE="${BASE:-"$HOME/Voynich/Voynich_Reproducible_Core"}"
T4="$BASE/PhaseT/out/t4_tokens_with_t3.tsv"
CAND="$BASE/PhaseT/out/t3_wave2_candidates.tsv"
OUT="$BASE/tests/out_test2_pmi.tsv"

echo "[*] Test2 – PMI(stem, section) → $OUT"
mkdir -p "$BASE/tests"

if [ ! -f "$T4" ]; then
  echo "[ERROR][Test2] Missing T4 file: $T4" >&2
  exit 1
fi

if [ ! -f "$CAND" ]; then
  echo "[ERROR][Test2] Missing candidates file: $CAND" >&2
  exit 1
fi

awk -F'\t' '
  NR==FNR {
    if (FNR==1) next
    stem_list[$1]=1
    next
  }

  FNR==1 {
    for (i=1;i<=NF;i++) {
      if ($i=="stem")    cStem=i
      if ($i=="section") cSec=i
    }
    next
  }

  {
    s=$cStem
    sec=$cSec
    all_total++
    sec_total[sec]++
    if (s in stem_list) {
      stem_total[s]++
      joint[s,sec]++
    }
  }

  END {
    OFS="\t"
    print "stem","dom_section","joint_count","pmi_bits"

    for (s in stem_total) {
      # find dominant section for this stem
      t = stem_total[s]
      if (t<=0) continue
      maxc = 0
      dom = ""
      for (key in joint) {
        split(key,a,SUBSEP)
        st=a[1]; sec=a[2]
        if (st!=s) continue
        c = joint[key]
        if (c>maxc) { maxc=c; dom=sec }
      }

      if (dom=="") {
        print s,"",0,"NA"
        continue
      }

      c_sd = maxc
      p_sd = c_sd / all_total
      p_s  = t / all_total
      p_d  = (dom in sec_total ? sec_total[dom] / all_total : 0)

      if (p_sd>0 && p_s>0 && p_d>0) {
        pmi = log(p_sd / (p_s * p_d)) / log(2)
        print s, dom, c_sd, pmi
      } else {
        print s, dom, c_sd, "NA"
      }
    }
  }
' "$CAND" "$T4" > "$OUT"

echo "[✓] Test2 complete → $OUT"
