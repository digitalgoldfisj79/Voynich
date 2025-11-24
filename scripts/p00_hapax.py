import collections

TOKFILE = "p6_voynich_tokens.txt"

freq = collections.Counter()
with open(TOKFILE, "r", encoding="utf-8") as f:
    for line in f:
        t = line.strip()
        if t:
            freq[t] += 1

types = len(freq)
hapax = sum(1 for t,c in freq.items() if c == 1)
print("Types:", types)
print("Hapax:", hapax)
print("Hapax % of types:", hapax / types * 100)
