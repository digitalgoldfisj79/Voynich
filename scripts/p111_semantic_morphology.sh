#!/usr/bin/env bash

File: scripts/p111_semantic_morphology.sh

Purpose: Phase 111 – join Phase110 attribution with Phase69 morphology and Phase83 semantics;

compute affix-wise and semantic-wise Δ (Latin–Arabic) and an affix×semantic grid.

Env: POSIX + python3 only (no pip). Termux-safe; atomic writes; deterministic sorts.

Usage: BASE=~/Voynich bash scripts/p111_semantic_morphology.sh

set -eu

---------- Config ----------

BASE=${BASE:-$HOME/Voynich} IN110="${BASE}/Phase110/out/p112_attribution_with_sections.tsv" IN69J="${BASE}/Phase69/out/p69_rules_calibrated.json" IN83="${BASE}/Phase83/out/p83_semantic_map.tsv" OUTD="${BASE}/Phase111/out" TMPD="${BASE}/Phase111/.tmp" LOGF="${BASE}/Phase111/p111_run.log"

mkdir -p "$OUTD" "$TMPD" : > "$LOGF"

log(){ printf '%s\n' "$" | tee -a "$LOGF"; } fail(){ log "[error] $"; exit 1; }

a_is_file(){ [ -f "$1" ] && [ -r "$1" ]; }

---------- Preflight ----------

log "[p111] Preflight checks" (a_is_file "$IN110" && a_is_file "$IN69J" && a_is_file "$IN83") || fail "Missing inputs.\n110: $IN110\n69: $IN69J\n83: $IN83"

Expect headers

head -n1 "$IN110" | grep -Eq '\b(ID|family|stem|token)\b' || fail "Phase110 header missing stem/token id" head -n1 "$IN83"  | grep -Eq '\b(ID|stem|token|semantic_class)\b' || fail "Phase83 header missing semantic_class"

---------- Step 1: Normalize Phase69 rules (JSON -> TSV) ----------

Output columns: ID\tprefix\tsuffix\trule_weight

P69_TSV="$TMPD/p69_rules_calibrated.tsv" python3 - "$IN69J" "$P69_TSV" <<'PY' import json,sys jpath,out=sys.argv[1],sys.argv[2] with open(jpath,'r',encoding='utf-8') as f: data=json.load(f)

Accept either list of rule-assignments or mapping ID->attrs

rows=[('ID','prefix','suffix','rule_weight')] if isinstance(data,dict) and 'assignments' in data: it=data['assignments'] elif isinstance(data,list): it=data elif isinstance(data,dict): it=[{'ID':k,**(v if isinstance(v,dict) else {})} for k,v in data.items()] else: it=[] for rec in it: ID=str(rec.get('ID') or rec.get('id') or rec.get('token') or rec.get('stem') or '') pre=rec.get('prefix','') suf=rec.get('suffix','') wt=rec.get('weight',rec.get('rule_weight',1.0)) rows.append((ID,str(pre),str(suf),str(wt))) with open(out,'w',encoding='utf-8') as g: for r in rows: g.write('\t'.join(r)+'\n') PY

---------- Step 2: Harmonize IDs ----------

We try to detect the ID column name used in Phase110 (stem or token or family_id)

idcol=$(head -n1 "$IN110" | awk -F'\t' '{for(i=1;i<=NF;i++)if($i=="ID"||$i=="id"||$i=="stem"||$i=="token"||$i=="family"||$i=="family_id") {print $i; exit}}') [ -n "$idcol" ] || fail "Could not detect ID column in p112_attribution_with_sections.tsv"

Extract a minimal attribution table: ID, section, delta, n (if available)

ATTR_MIN="$TMPD/p110_attr_min.tsv" awk -F'\t' -v IDCOL="$idcol" 'NR==1{for(i=1;i<=NF;i++){h[$i]=i} printf "ID\tsection\tdelta\tn\n"; next} { id=$h[IDCOL]; if(id=="") next; sec=$h["section"]; if(sec=="") sec=$h["Section"]; d=$h["delta"]; if(d=="") d=$h["mean_delta"]; n=$h["n"]; if(n=="") n=1; print $id"\t"sec"\t"d"\t"n" }' "$IN110" > "$ATTR_MIN"

---------- Step 3: Join attribution with morphology and semantics ----------

JOIN1="$TMPD/p111_join_attr_morph.tsv" python3 - "$ATTR_MIN" "$P69_TSV" "$JOIN1" <<'PY' import csv,sys attr, morph, out = sys.argv[1:4] A={} with open(attr, newline='', encoding='utf-8') as f: r=csv.DictReader(f, delimiter='\t') for row in r: A[row['ID']] = row with open(morph, newline='', encoding='utf-8') as f: r=csv.DictReader(f, delimiter='\t') rows=[x for x in r]

Some IDs may repeat; emit one per record

with open(out,'w',encoding='utf-8',newline='') as g: w=csv.writer(g, delimiter='\t') w.writerow(['ID','section','delta','n','prefix','suffix','rule_weight']) for m in rows: id=m['ID'] a=A.get(id) if not a: continue w.writerow([id,a['section'],a['delta'],a['n'],m['prefix'],m['suffix'],m.get('rule_weight','1')]) PY

JOIN2="$TMPD/p111_join_attr_morph_sem.tsv" python3 - "$JOIN1" "$IN83" "$JOIN2" <<'PY' import csv,sys jm, sem, out = sys.argv[1:4] S={}  # ID -> semantic class with open(sem, newline='', encoding='utf-8') as f: r=csv.DictReader(f, delimiter='\t') # look for semantic column heuristics for row in r: sid=row.get('ID') or row.get('id') or row.get('stem') or row.get('token') semv=row.get('semantic_class') or row.get('sem_class') or row.get('class') or '' if sid: S[sid]=semv with open(jm, newline='', encoding='utf-8') as f, open(out,'w',encoding='utf-8',newline='') as g: r=csv.DictReader(f, delimiter='\t') w=csv.writer(g, delimiter='\t') w.writerow(r.fieldnames+['semantic_class']) for row in r: semv=S.get(row['ID'],'') w.writerow([row[k] for k in r.fieldnames]+[semv]) PY

---------- Step 4: Aggregations ----------

AFFIX_OUT="$OUTD/p111_affix_delta.tsv" python3 - "$JOIN2" "$AFFIX_OUT" <<'PY' import csv,sys,statistics inp,out=sys.argv[1:3] from collections import defaultdict acc=defaultdict(list) with open(inp,newline='',encoding='utf-8') as f: r=csv.DictReader(f, delimiter='\t') for row in r: try: d=float(row['delta']) except: continue for k in ('prefix','suffix'): v=row.get(k,'') if v!='': acc[(k,v)].append(d) rows=[('affix_type','affix','n','mean_delta','median_delta','stdev_delta')] for (k,v),vals in acc.items(): n=len(vals); mu=sum(vals)/n med=statistics.median(vals) sd=statistics.pstdev(vals) if n>1 else 0.0 rows.append((k,v,str(n),f"{mu:.6f}",f"{med:.6f}",f"{sd:.6f}")) rows.sort(key=lambda x:(x[0],-float(x[3]) if x[0]!='affix_type' else 0)) with open(out,'w',encoding='utf-8') as g: for r in rows: g.write('\t'.join(r)+'\n') PY

SEM_OUT="$OUTD/p111_semclass_delta.tsv" python3 - "$JOIN2" "$SEM_OUT" <<'PY' import csv,sys,statistics inp,out=sys.argv[1:3] from collections import defaultdict acc=defaultdict(list) with open(inp,newline='',encoding='utf-8') as f: r=csv.DictReader(f, delimiter='\t') for row in r: try: d=float(row['delta']) except: continue s=row.get('semantic_class','') acc[s].append(d) rows=[('semantic_class','n','mean_delta','median_delta','stdev_delta')] for s,vals in acc.items(): n=len(vals); mu=sum(vals)/n med=statistics.median(vals) sd=statistics.pstdev(vals) if n>1 else 0.0 rows.append((s,str(n),f"{mu:.6f}",f"{med:.6f}",f"{sd:.6f}")) rows.sort(key=lambda x:(x[0]=="semantic_class", -float(x[2]) if x[0]!="semantic_class" else 0)) with open(out,'w',encoding='utf-8') as g: for r in rows: g.write('\t'.join(r)+'\n') PY

GRID_OUT="$OUTD/p111_affix_semantic_grid.tsv" python3 - "$JOIN2" "$GRID_OUT" <<'PY' import csv,sys inp,out=sys.argv[1:3] from collections import defaultdict A=defaultdict(lambda: defaultdict(list)) Aff=set(); Sem=set() with open(inp,newline='',encoding='utf-8') as f: r=csv.DictReader(f, delimiter='\t') for row in r: try: d=float(row['delta']) except: continue sem=row.get('semantic_class','') for t in ('prefix','suffix'): a=row.get(t,'') if a=='': continue A[(t,a)][sem].append(d) Aff.add((t,a)); Sem.add(sem)

order

aff_list=sorted(Aff) sem_list=sorted(Sem) with open(out,'w',encoding='utf-8') as g: g.write('affix_type\taffix\t'+'\t'.join(sem_list)+'\n') for (t,a) in aff_list: row=[t,a] for s in sem_list: vals=A[(t,a)][s] row.append(f"{(sum(vals)/len(vals)):.6f}" if vals else '') g.write('\t'.join(row)+'\n') PY

---------- Step 5: Summary ----------

SUMMARY="$OUTD/p111_summary.txt" { echo "Phase 111 – Semantic Morphology & Latin vs Arabic" echo "Inputs:"; echo "  - $IN110"; echo "  - $IN69J"; echo "  - $IN83"; echo echo "Top Latin-leaning affixes (by mean Δ):" (awk -F'\t' 'NR>1&&$1=="suffix"{print $0}' "$AFFIX_OUT" | sort -t'\t' -k4,4gr | head -n 10) || true echo echo "Top Arabic-leaning affixes (by mean Δ ascending):" (awk -F'\t' 'NR>1&&$1=="suffix"{print $0}' "$AFFIX_OUT" | sort -t'\t' -k4,4g | head -n 10) || true echo echo "Semantic classes ranked by mean Δ:" (awk -F'\t' 'NR>1{print $0}' "$SEM_OUT" | sort -t'\t' -k3,3gr) || true } > "$SUMMARY"

---------- Finalize (atomic move already ensured by writing into OUTD) ----------

Emit manifest

MANI="$OUTD/p111_manifest.tsv" { echo -e "path\tsize" for f in "$AFFIX_OUT" "$SEM_OUT" "$GRID_OUT" "$SUMMARY" "$LOGF"; do [ -f "$f" ] && printf "%s\t%s\n" "$f" "$(wc -c < "$f")" done | sort } > "$MANI"

log "[p111] Done. Outputs:" log " - $AFFIX_OUT" log " - $SEM_OUT" log " - $GRID_OUT" log " - $SUMMARY" log " - $MANI"
