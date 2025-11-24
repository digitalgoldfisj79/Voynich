#!/usr/bin/env bash
set -euo pipefail

# Phase 111 – Semantic Morphology & Latin vs Arabic (hotfix)
# Inputs:
#   $BASE/Phase110/out/p112_attribution_with_sections.tsv
#   $BASE/Phase69/out/p69_rules_calibrated.json
#   $BASE/Phase83/out/p83_semantic_map.tsv
# Outputs:
#   $BASE/Phase111/out/p111_affix_delta.tsv
#   $BASE/Phase111/out/p111_semclass_delta.tsv
#   $BASE/Phase111/out/p111_affix_semantic_grid.tsv
#   $BASE/Phase111/out/p111_summary.txt
#   $BASE/Phase111/out/p111_manifest.tsv

BASE="${BASE:-$HOME/Voynich}"
IN110="$BASE/Phase110/out/p112_attribution_with_sections.tsv"
IN69J="$BASE/Phase69/out/p69_rules_calibrated.json"
IN83="$BASE/Phase83/out/p83_semantic_map.tsv"
OUTD="$BASE/Phase111/out"
TMPD="$BASE/Phase111/.tmp"
LOGF="$BASE/Phase111/p111_run.log"

mkdir -p "$OUTD" "$TMPD"
: > "$LOGF"

log(){ printf '%s\n' "$*" | tee -a "$LOGF" ; }
die(){ log "[error] $*"; exit 1; }

[ -r "$IN110" ] || die "missing $IN110"
[ -r "$IN69J" ] || die "missing $IN69J"
[ -r "$IN83"  ] || die "missing $IN83"

# Step 1: Phase69 JSON -> TSV
P69_TSV="$TMPD/p69_rules_calibrated.tsv"
python3 - <<'PY' "$IN69J" "$P69_TSV"
import json,sys,csv
jpath,out=sys.argv[1],sys.argv[2]
with open(jpath,'r',encoding='utf-8') as f: data=json.load(f)
rows=[('ID','prefix','suffix','rule_weight')]
if isinstance(data,dict) and 'assignments' in data:
    it=data['assignments']
elif isinstance(data,list):
    it=data
elif isinstance(data,dict):
    it=[{'ID':k,**(v if isinstance(v,dict) else {})} for k,v in data.items()]
else:
    it=[]
for rec in it:
    ID=str(rec.get('ID') or rec.get('id') or rec.get('token') or rec.get('stem') or '')
    pre=str(rec.get('prefix',''))
    suf=str(rec.get('suffix',''))
    wt=str(rec.get('weight',rec.get('rule_weight',1.0)))
    rows.append((ID,pre,suf,wt))
with open(out,'w',encoding='utf-8',newline='') as g:
    csv.writer(g,delimiter='\t').writerows(rows)
PY

# Step 2: detect ID/section/delta headers in Phase110
idcol=$(head -n1 "$IN110" | awk -F'\t' '
  {for(i=1;i<=NF;i++) if($i=="ID"||$i=="id"||$i=="stem"||$i=="token"||$i=="family"||$i=="family_id"){print $i; exit}}
')
[ -n "$idcol" ] || die "could not detect ID column in p112_attribution_with_sections.tsv"

ATTR_MIN="$TMPD/p110_attr_min.tsv"
awk -F'\t' -v IDCOL="$idcol" '
NR==1{
  for(i=1;i<=NF;i++){h[$i]=i}
  print "ID\tsection\tdelta\tn"
  next
}
{
  id = (IDCOL in h)? $h[IDCOL] : ""
  if(id=="") next
  sec = (("section" in h)? $h["section"] : (("Section" in h)? $h["Section"] : ""))
  d   = (("delta" in h)? $h["delta"] : (("mean_delta" in h)? $h["mean_delta"] : ""))
  n   = (("n" in h)? $h["n"] : 1)
  print id "\t" sec "\t" d "\t" n
}' "$IN110" > "$ATTR_MIN"

# Step 3: Join attr + morph
JOIN1="$TMPD/p111_join_attr_morph.tsv"
python3 - <<'PY' "$ATTR_MIN" "$P69_TSV" "$JOIN1"
import sys,csv
attr,morph,out=sys.argv[1:4]
A={}
with open(attr,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f,delimiter='\t')
    for row in r: A[row['ID']]=row
with open(morph,newline='',encoding='utf-8') as f, open(out,'w',encoding='utf-8',newline='') as g:
    rm=csv.DictReader(f,delimiter='\t')
    w=csv.writer(g,delimiter='\t'); w.writerow(['ID','section','delta','n','prefix','suffix','rule_weight'])
    for m in rm:
        a=A.get(m['ID']); 
        if not a: continue
        w.writerow([m['ID'],a['section'],a['delta'],a['n'],m['prefix'],m['suffix'],m.get('rule_weight','1')])
PY

# Step 4: Join semantics
JOIN2="$TMPD/p111_join_attr_morph_sem.tsv"
python3 - <<'PY' "$JOIN1" "$IN83" "$JOIN2"
import sys,csv
jm,sem,out=sys.argv[1:4]
S={}
with open(sem,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f,delimiter='\t')
    for row in r:
        sid=row.get('ID') or row.get('id') or row.get('stem') or row.get('token')
        if sid: S[sid]=row.get('semantic_class') or row.get('sem_class') or row.get('class') or ''
with open(jm,newline='',encoding='utf-8') as f, open(out,'w',encoding='utf-8',newline='') as g:
    r=csv.DictReader(f,delimiter='\t')
    w=csv.writer(g,delimiter='\t'); w.writerow(r.fieldnames+['semantic_class'])
    for row in r: w.writerow([row[k] for k in r.fieldnames]+[S.get(row['ID'],'')])
PY

# Step 5: Aggregations
AFFIX_OUT="$OUTD/p111_affix_delta.tsv"
python3 - <<'PY' "$JOIN2" "$AFFIX_OUT"
import sys,csv,statistics
inp,out=sys.argv[1:3]
from collections import defaultdict
acc=defaultdict(list)
with open(inp,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f,delimiter='\t')
    for row in r:
        try: d=float(row['delta'])
        except: continue
        for k in ('prefix','suffix'):
            v=row.get(k,'')
            if v!='': acc[(k,v)].append(d)
rows=[('affix_type','affix','n','mean_delta','median_delta','stdev_delta')]
for (k,v),vals in sorted(acc.items()):
    n=len(vals); mu=sum(vals)/n
    med=statistics.median(vals)
    sd=statistics.pstdev(vals) if n>1 else 0.0
    rows.append((k,v,str(n),f"{mu:.6f}",f"{med:.6f}",f"{sd:.6f}"))
with open(out,'w',encoding='utf-8',newline='') as g:
    csv.writer(g,delimiter='\t').writerows(rows)
PY

SEM_OUT="$OUTD/p111_semclass_delta.tsv"
python3 - <<'PY' "$JOIN2" "$SEM_OUT"
import sys,csv,statistics
inp,out=sys.argv[1:3]
from collections import defaultdict
acc=defaultdict(list)
with open(inp,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f,delimiter='\t')
    for row in r:
        acc[row.get('semantic_class','')].append(float(row['delta']))
rows=[('semantic_class','n','mean_delta','median_delta','stdev_delta')]
for s,vals in sorted(acc.items()):
    n=len(vals); mu=sum(vals)/n
    med=statistics.median(vals)
    sd=statistics.pstdev(vals) if n>1 else 0.0
    rows.append((s,str(n),f"{mu:.6f}",f"{med:.6f}",f"{sd:.6f}"))
with open(out,'w',encoding='utf-8',newline='') as g:
    csv.writer(g,delimiter='\t').writerows(rows)
PY

GRID_OUT="$OUTD/p111_affix_semantic_grid.tsv"
python3 - <<'PY' "$JOIN2" "$GRID_OUT"
import sys,csv
from collections import defaultdict
inp,out=sys.argv[1:3]
A=defaultdict(lambda: defaultdict(list)); Aff=set(); Sem=set()
with open(inp,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f,delimiter='\t')
    for row in r:
        try: d=float(row['delta'])
        except: continue
        sem=row.get('semantic_class','')
        for t in ('prefix','suffix'):
            a=row.get(t,'')
            if a=='': continue
            A[(t,a)][sem].append(d); Aff.add((t,a)); Sem.add(sem)
aff_list=sorted(Aff); sem_list=sorted(Sem)
with open(out,'w',encoding='utf-8',newline='') as g:
    w=csv.writer(g,delimiter='\t'); w.writerow(['affix_type','affix']+list(sem_list))
    for (t,a) in aff_list:
        row=[t,a]
        for s in sem_list:
            vals=A[(t,a)][s]
            row.append(f"{(sum(vals)/len(vals)):.6f}" if vals else '')
        w.writerow(row)
PY

SUMMARY="$OUTD/p111_summary.txt"
{
  echo "Phase 111 - Semantic Morphology & Latin vs Arabic"
  echo "Inputs:"; echo "  - $IN110"; echo "  - $IN69J"; echo "  - $IN83"; echo
  echo "Top suffixes by mean_delta (descending):"
  awk -F'\t' 'NR>1&&$1=="suffix"{print $0}' "$AFFIX_OUT" | sort -t$'\t' -k4,4gr | head -n 12
  echo
  echo "Semantic classes by mean_delta (descending):"
  awk -F'\t' 'NR>1{print $0}' "$SEM_OUT" | sort -t$'\t' -k3,3gr | head -n 20
} > "$SUMMARY"

# Manifest
MANI="$OUTD/p111_manifest.tsv"
{
  echo -e "path\tsize"
  for f in "$AFFIX_OUT" "$SEM_OUT" "$GRID_OUT" "$SUMMARY" "$LOGF"; do
    [ -f "$f" ] && printf "%s\t%s\n" "$f" "$(wc -c < "$f")"
  done | sort
} > "$MANI"

log "[p111] done"
log " - $AFFIX_OUT"
log " - $SEM_OUT"
log " - $GRID_OUT"
log " - $SUMMARY"
log " - $MANI"
