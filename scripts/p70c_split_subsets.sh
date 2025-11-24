#!/bin/sh
mkdir -p Phase70/out
awk '$2=="C"{print $1}' Phase70/out/p70a_token_flags.tsv > Phase70/out/p70c_tokens_covered.txt
awk '$2=="U"{print $1}' Phase70/out/p70a_token_flags.tsv > Phase70/out/p70c_tokens_uncovered.txt
python3 scripts/p6_compute_entropy_mi.py Phase70/out/p70c_tokens_covered.txt > Phase70/out/p70c_stats_covered.txt
python3 scripts/p6_compute_entropy_mi.py Phase70/out/p70c_tokens_uncovered.txt > Phase70/out/p70c_stats_uncovered.txt
echo "[OK] Computed entropy/MI for subsets."
