#!/usr/bin/env bash
set -euo pipefail
IN="$1"; OUT="$2"; TMP="$OUT.tmp.$$"; trap 'rm -f "$TMP"' EXIT
awk -F'\t' -v OFS='\t' '
NR==1{
  for(i=1;i<=NF;i++){k=tolower($i); h[k]=i}
  pi=(h["prefix"]?h["prefix"]:(h["pref"]?h["pref"]:(h["pre"]?h["pre"]:0)))
  si=(h["suffix"]?h["suffix"]:(h["suf"]?h["suf"]:(h["sfx"]?h["sfx"]:0)))
  wi=(h["weight"]?h["weight"]:(h["count"]?h["count"]:(h["freq"]?h["freq"]:0)))
  if(!pi||!si){print "[error] missing prefix/suffix headers" > "/dev/stderr"; exit 1}
  hasW=wi?1:0; print "prefix","suffix","weight" > "'$TMP'"; next
}
{ p=$pi; s=$si; w=(hasW?$wi:1); if(p!=""&&s!="") print p,s,w >> "'$TMP'" }
END{ close("'$TMP'") }' "$IN"
mv "$TMP" "$OUT"
echo "[ok] wrote $OUT"
