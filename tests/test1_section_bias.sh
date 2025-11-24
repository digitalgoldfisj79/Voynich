#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-$HOME/Voynich/Voynich_Reproducible_Core}"
IN="$BASE/PhaseT/out/t4_tokens_with_t3.tsv"
OUTD="$BASE/tests"
OUT="$OUTD/out_test1_section_bias.tsv"

mkdir -p "$OUTD"

# Expect headered TSV. We compute per-stem:
# total, dominant section, purity, n_sections, gini
awk -F'\t' '
BEGIN{OFS="\t"}
NR==1{
  for(i=1;i<=NF;i++){
    h[$i]=i
  }
  stem_i=h["stem"]; sec_i=h["section"]
  if(!stem_i||!sec_i){
    print "FATAL: missing stem/section columns in header" > "/dev/stderr"
    exit 1
  }
  next
}
{
  s=$stem_i; sec=$sec_i
  if(s==""||sec=="") next
  total[s]++
  c[s,sec]++
  secs[s][sec]=1
}
END{
  print "stem","total","dom_section","dom_count","purity","n_sections","gini"
  for(s in total){
    t=total[s]
    if(t<=0) continue

    # dominant section + count
    dom=""; domc=0; nsec=0
    for(k in secs[s]){
      nsec++
      if(c[s,k]>domc){ domc=c[s,k]; dom=k }
    }
    purity=domc/t

    # gini across sections: 1 - sum(p_i^2)
    sumsq=0
    for(k in secs[s]){
      p=c[s,k]/t
      sumsq += p*p
    }
    gini = 1 - sumsq

    print s,t,dom,domc,sprintf("%.6f",purity),nsec,sprintf("%.6f",gini)
  }
}
' "$IN" | sort -t$'\t' -k2,2nr > "$OUT"

echo "[✓] Test1 complete → $OUT"
