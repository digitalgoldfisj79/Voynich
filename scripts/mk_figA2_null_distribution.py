#!/usr/bin/env python3
# POSIX-safe, Termux-safe null distribution generator
# Computes H1 and MI1 for shuffled Voynich tokens
# Produces: null_distribution.tsv + figA2_null_distribution.png

import sys, os, random, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ───────────────────────────────────────────────────────────────
#  Helpers
# ───────────────────────────────────────────────────────────────

def entropy_H1(tokens):
    """Compute character entropy H1 (bits/char)."""
    s = "".join(tokens)
    counts = {}
    for c in s:
        counts[c] = counts.get(c, 0) + 1
    total = len(s)
    return -sum((v/total) * math.log2(v/total) for v in counts.values())

def mutual_information_MI1(tokens):
    """Compute bigram mutual information MI1."""
    s = "".join(tokens)
    N = len(s)
    if N < 3:
        return 0.0

    # Char frequencies
    c_freq = {}
    for c in s:
        c_freq[c] = c_freq.get(c, 0) + 1

    # Bigram frequencies
    b_freq = {}
    for i in range(N - 1):
        bg = s[i:i+2]
        b_freq[bg] = b_freq.get(bg, 0) + 1

    H1 = -sum((c_freq[c]/N) * math.log2(c_freq[c]/N) for c in c_freq)
    H2 = -sum((b_freq[b]/(N-1)) * math.log2(b_freq[b]/(N-1)) for b in b_freq)

    # MI1 = 2H1 − H2
    return 2*H1 - H2

# ───────────────────────────────────────────────────────────────
#  Locate project paths
# ───────────────────────────────────────────────────────────────

BASE = os.environ.get("BASE", os.path.expanduser("~/Voynich/Voynich_Reproducible_Core"))
TOKENS = f"{BASE}/corpora/p6_voynich_tokens.txt"
OUTD = f"{BASE}/figures"

if not os.path.exists(TOKENS):
    print(f"[error] cannot find token file: {TOKENS}")
    sys.exit(1)

os.makedirs(OUTD, exist_ok=True)

# ───────────────────────────────────────────────────────────────
#  Load Voynich tokens
# ───────────────────────────────────────────────────────────────

with open(TOKENS, "r") as f:
    tokens = [line.strip() for line in f if line.strip()]

print(f"[info] loaded {len(tokens)} tokens")

# Compute true values for comparison
true_H1 = entropy_H1(tokens)
true_MI1 = mutual_information_MI1(tokens)

print(f"[info] true H1={true_H1:.4f}, MI1={true_MI1:.4f}")

# ───────────────────────────────────────────────────────────────
#  Null distribution (shuffling)
# ───────────────────────────────────────────────────────────────

N = 500   # number of shuffled controls
rows = []

chars = list("".join(tokens))

print("[info] computing null distribution (this may take a few seconds)…")

for i in range(N):
    random.shuffle(chars)
    shuffled = ["".join(chars[j:j+5]) for j in range(0, len(chars), 5)]  # arbitrary chunking

    h = entropy_H1(shuffled)
    m = mutual_information_MI1(shuffled)

    rows.append((i, h, m))
    if i % 50 == 0:
        print(f"[{i}/{N}] …")

df = pd.DataFrame(rows, columns=["iter", "H1", "MI1"])
out_tsv = f"{OUTD}/null_distribution.tsv"
df.to_csv(out_tsv, sep="\t", index=False)

print(f"[ok] wrote {out_tsv}")

# ───────────────────────────────────────────────────────────────
#  Plot
# ───────────────────────────────────────────────────────────────

plt.figure(figsize=(8,6))
plt.scatter(df["H1"], df["MI1"], s=10, alpha=0.4, label="Shuffled controls")

plt.scatter(true_H1, true_MI1, c="red", s=100, label="Voynich (true)")

plt.xlabel("Entropy H₁ (bits/char)")
plt.ylabel("Mutual Information MI₁ (bits)")
plt.title("Figure A2 – Null Distribution of Information Metrics\nVoynich vs Shuffled Controls")
plt.legend()

out_png = f"{OUTD}/figA2_null_distribution.png"
plt.savefig(out_png, dpi=200)
print(f"[ok] wrote {out_png}")
