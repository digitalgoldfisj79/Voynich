# p110_section_meandelta_v2.awk
# Usage:
#   awk -f scripts/p110_section_meandelta_v2.awk Phase77/out/p77_anchor_families.tsv Phase110/out/p112_attribution.tsv
#
# Does:
#   - Auto-detect headers in BOTH files
#   - Supports family columns named: family | family_signature | signature
#   - Supports section columns named: section | dominant_section
#   - Canonicalises family keys (sort dash-separated parts) so "he-che" == "che-he"
#   - Aggregates mean Δ per section
#   - Prints diagnostics to STDERR

BEGIN {
  FS = OFS = "\t"
  mode = "p77"
}

function trim(s){ sub(/^[ \t\r\n]+/,"",s); sub(/[ \t\r\n]+$/,"",s); return s }
function tolower_str(s){ gsub(/[A-Z]/, "", s); return tolower(s) } # busybox awk ok with tolower()
function canon_key(k,   n,i,parts,tmp,swapped,j) {
  # split on '-', lower-case, trim, then simple bubble sort
  n = split(k, parts, /-/)
  for (i=1; i<=n; i++) parts[i]=tolower(parts[i])
  # bubble sort (n small)
  do {
    swapped=0
    for (i=1; i<n; i++) {
      if (parts[i] > parts[i+1]) {
        tmp = parts[i]; parts[i]=parts[i+1]; parts[i+1]=tmp; swapped=1
      }
    }
  } while (swapped)
  # join back
  out=""
  for (i=1; i<=n; i++) {
    parts[i]=trim(parts[i])
    if (parts[i]=="") continue
    out = (out=="" ? parts[i] : out "-" parts[i])
  }
  return out
}

# ---------- PASS 1: p77 anchors (family -> section) ----------
FNR==1 && mode=="p77" {
  delete h77
  for (i=1; i<=NF; i++) h77[$i]=i
  fam77 = (h77["family"] ? h77["family"] :
          (h77["family_signature"] ? h77["family_signature"] :
          (h77["signature"] ? h77["signature"] : 0)))
  if (fam77==0) fam77=1
  sec77 = (h77["section"] ? h77["section"] :
          (h77["dominant_section"] ? h77["dominant_section"] : 0))
  if (sec77==0) sec77=2
  next
}

mode=="p77" && FNR>1 {
  fam_raw = trim($fam77)
  sec     = trim($sec77)
  if (fam_raw!="") {
    fam2sec_raw[fam_raw] = sec
    fam2sec_norm[canon_key(fam_raw)] = sec
    p77_seen++
  }
  next
}

# ---------- SWITCH TO PASS 2 ----------
FILENAME ~ /p77_/ && mode=="p77" { next }
FNR==1 && mode=="p77" {
  mode="attr"
  delete hattr
  for (i=1; i<=NF; i++) hattr[$i]=i
  fam_attr   = (hattr["family"] ? hattr["family"] :
               (hattr["family_signature"] ? hattr["family_signature"] :
               (hattr["signature"] ? hattr["signature"] : 0)))
  if (fam_attr==0) fam_attr=1
  delta_attr = (hattr["delta"] ? hattr["delta"] : 0)
  if (delta_attr==0) delta_attr=4
  next
}

# ---------- PASS 2: attribution (family -> delta) ----------
mode=="attr" && FNR>1 {
  famA = trim($fam_attr)
  delt = $delta_attr
  if (famA=="") next
  sec  = ""
  if (fam2sec_raw[famA]!="") sec=fam2sec_raw[famA]
  else {
    famA_c = canon_key(famA)
    if (fam2sec_norm[famA_c]!="") sec=fam2sec_norm[famA_c]
  }
  if (sec!="") {
    sum[sec] += delt
    n[sec]++
    matched++
  } else {
    if (unmatched<10) unmatched_ex[unmatched++] = famA
  }
  attr_seen++
  next
}

END {
  if (matched==0) {
    print "[warn] No section matches found.", \
          "p77 rows:", p77_seen, \
          "attr rows:", attr_seen > "/dev/stderr"
    if (unmatched>0) {
      print "[hint] First few unmatched families from attribution:" > "/dev/stderr"
      for (i=0; i<unmatched; i++) print "  -", unmatched_ex[i] > "/dev/stderr"
    }
    print "[hint] Check that the 'family' signatures use the same ordering and separators in both files." > "/dev/stderr"
    exit 1
  }
  # Print results
  for (s in n) printf "%s\tmeanΔ=%.6f\tn=%d\n", s, (sum[s]/n[s]), n[s]
  # Diagnostics
  print "[ok] Matched families:", matched, " / attribution rows:", attr_seen, "| anchors in p77:", p77_seen > "/dev/stderr"
}
