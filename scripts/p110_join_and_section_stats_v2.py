#!/usr/bin/env python3
# POSIX-safe, no external deps beyond stdlib + pandas
import sys, os, pandas as pd

def norm(sig: str) -> str:
    if not isinstance(sig, str):
        return ""
    parts = [p.strip() for p in sig.replace("—","-").replace("–","-").split("-") if p.strip()]
    if not parts:
        return ""
    parts = sorted(parts)
    # remove duplicates while preserving sorted order
    dedup = []
    for p in parts:
        if not dedup or dedup[-1] != p:
            dedup.append(p)
    return "-".join(dedup)

def load_attrib(path):
    df = pd.read_csv(path, sep="\t")
    # expected cols: family, sim_latin, sim_arabic, delta, label
    need = {"family","sim_latin","sim_arabic","delta","label"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"[ERR] {path} missing columns: {missing}")
    df["family_norm"] = df["family"].map(norm)
    return df

def load_sections(path, family_col="family", section_col="section"):
    df = pd.read_csv(path, sep="\t")
    if family_col not in df.columns or section_col not in df.columns:
        raise SystemExit(f"[ERR] {path} must have columns '{family_col}' and '{section_col}'")
    df["family_norm"] = df[family_col].map(norm)
    # keep only (family_norm, section)
    return df[["family_norm", section_col]].rename(columns={section_col:"section"})

def main():
    base = "Phase110/out"
    a_path  = os.path.join(base, "p112_attribution.tsv")
    fs_pref = "Phase77/out/p77_family_section.tsv"
    fs_alt  = "Phase77/out/p77_anchor_families.tsv"

    if len(sys.argv) >= 2:
        a_path = sys.argv[1]
    if len(sys.argv) >= 3:
        fs_pref = sys.argv[2]

    print(f"=== Join attribution → sections ===")
    print(f"[INFO] Attribution: {a_path}")
    print(f"[INFO] Preferred section map: {fs_pref}")
    print(f"[INFO] Alternate (anchors): {fs_alt}")

    if not os.path.exists(a_path):
        raise SystemExit(f"[ERR] Not found: {a_path}")

    attrib = load_attrib(a_path)

    # try preferred, else anchors
    if os.path.exists(fs_pref):
        sections = load_sections(fs_pref, family_col="family", section_col="section")
        src = "p77_family_section"
    elif os.path.exists(fs_alt):
        sections = load_sections(fs_alt, family_col="family", section_col="section")
        src = "p77_anchor_families"
    else:
        raise SystemExit("[ERR] No section map found (neither p77_family_section.tsv nor p77_anchor_families.tsv).")

    print(f"[INFO] Section source: {src}")
    # inner join to count true matches; left join to retain all families
    j = attrib.merge(sections, on="family_norm", how="left")

    out = os.path.join(base, "p112_attribution_with_sections.tsv")
    j.to_csv(out, sep="\t", index=False)
    print(f"[OK] Joined → {out}")

    n_tot = len(attrib)
    n_matched = j["section"].notna().sum()
    n_unknown = (j["section"].fillna("Unknown")=="Unknown").sum()

    print(f"[INFO] Families in attribution: {n_tot}")
    print(f"[INFO] Matched to a section:    {n_matched}")
    print(f"[INFO] Section='Unknown':       {n_unknown}")

    # per-section mean Δ (only for rows with a section)
    jj = j.dropna(subset=["section"]).copy()
    if len(jj):
        per = jj.groupby("section")["delta"].agg(["count","mean"]).reset_index()
        per = per.sort_values("mean", ascending=False)
        print("=== Sectional mean Δ (sim_latin - sim_arabic) ===")
        for _, r in per.iterrows():
            print(f"{r['section']}\tmeanΔ={r['mean']:.4f}\tn={int(r['count'])}")
    else:
        print("[warn] No families with real sections in the section map; everything is Unknown. Rebuild your p77 section files.")

if __name__ == "__main__":
    main()
