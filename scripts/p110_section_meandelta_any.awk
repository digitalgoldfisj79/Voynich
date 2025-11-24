# p110_section_meandelta_any.awk
# Usage:
#   awk -f scripts/p110_section_meandelta_any.awk <family_section.tsv> <p112_attribution.tsv>
#
# Requirements:
#   family_section.tsv -> columns: family [tab] section (headers allowed)
#   p112_attribution.tsv -> columns: family, sim_latin, sim_arabic, delta, label (headers allowed)
#
# Robustness:
#   - Accepts tabs or spaces (FS = "[ \t]+")
#   - Canonicalises family keys (sort dash-separated parts), so "he-che" == "che-he"
#   - Prints mean Δ per section + diagnostics

BEGIN {
  FS = "[ \t]+"
  OFS = "\t"
  phase = 1
}

function trim(s){ gsub(/^[ \t\r\n]+|[ \t\r\n]+$/,"",s); return s }
function canon(k,  n,i,a,tmp,swapped,out) {
  # split on '-', lower, bubble-sort
  n = split(k, a, /-/)
  for (i=1;i<=n;i++){ a[i]=tolower(trim(a[i])) }
  do {
    swapped=0
    for (i=1;i<n;i++){
      if (a[i] > a[i+1]) { tmp=a[i]; a[i]=a[i+1]; a[i+1]=tmp; swapped=1 }
    }
  } while(swapped)
  out=""
  for (i=1;i<=n;i++){ if (a[i]!="") out=(out==""?a[i]:out "-" a[i]) }
  return out
}

# ------- PASS 1: family→section map -------
phase==1 && FNR==1 {
  # Heuristics: if line has "family" and "section", treat as header and skip
  header_line = $0
  if (match(tolower(header_line), /family/) && match(tolower(header_line), /section/)) { next }
}
phase==1 {
  fam = trim($1); sec = trim($2)
  if (fam!="" && sec!="") {
    fam2sec_raw[fam] = sec
    fam2sec_can[canon(fam)] = sec
    nmap++
  }
  next
}

# ------- SWITCH TO PASS 2 -------
FNR==1 { phase=2; next }

# ------- PASS 2: attribution (family,delta) -------
phase==2 && FNR==1 {
  # header? (if first field is "family" or "delta" present)
  if (match(tolower($0), /^family/) || match(tolower($0), /delta/)) next
}

phase==2 {
  fam = trim($1)
  delt = trim($4)      # 4th col is "delta"
  if (fam=="") next
  sec = ""
  if (fam2sec_raw[fam]!="") sec=fam2sec_raw[fam]
  else {
    famc = canon(fam)
    if (fam2sec_can[famc]!="") sec = fam2sec_can[famc]
  }
  if (sec!="") {
    sum[sec] += delt
    cnt[sec]++
    matched++
  } else {
    if (nomatch < 10) miss[nomatch++] = fam
  }
  seen++
  next
}

END {
  if (matched==0) {
    print "[warn] No section matches. Map rows:", nmap, " | attribution rows:", seen > "/dev/stderr"
    if (nomatch>0) {
      print "[hint] First unmatched fam keys from attribution:" > "/dev/stderr"
      for (i=0;i<nomatch;i++) print "  -", miss[i] > "/dev/stderr"
    }
    exit 1
  }
  # Results
  for (s in cnt) printf "%s\tmeanΔ=%.6f\tn=%d\n", s, (sum[s]/cnt[s]), cnt[s]
  print "[ok] matched:", matched, "/", seen, "| map size:", nmap > "/dev/stderr"
}
