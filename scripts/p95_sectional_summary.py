import pandas as pd
df = pd.read_csv("Phase95/out/p95_line_metrics.tsv", sep="\t")
meta = pd.read_csv("meta/folio_sections.tsv", sep="\t")  # folio→section
df = df.merge(meta, on="folio", how="left")
section_stats = df.groupby("section").agg(
    lines=('n_tokens','count'),
    mean_tokens=('n_tokens','mean'),
    mean_len=('mean_token_length','mean'),
    mean_rule=('frac_with_rule','mean'),
    mean_entropy=('mean_H1_local_bits','mean')
).reset_index()
section_stats.to_csv("Phase95/out/p95_section_summary.tsv", sep="\t", index=False)
