# scripts/p110_plot_section_deltas.py
import sys
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print("usage: python3 p110_plot_section_deltas.py <joined_attribution.tsv>")
    sys.exit(1)

path = sys.argv[1]
df = pd.read_csv(path, sep="\t")

# expect columns: family, sim_latin, sim_arabic, delta, label, section
df = df[df["section"] != "Unknown"]
summary = (
    df.groupby("section")["delta"]
      .agg(["mean", "count", "std"])
      .reset_index()
      .sort_values("mean", ascending=False)
)
summary["se"] = summary["std"] / summary["count"] ** 0.5
summary["lower"] = summary["mean"] - 1.96 * summary["se"]
summary["upper"] = summary["mean"] + 1.96 * summary["se"]

print(summary.to_string(index=False, float_format="%.4f"))

plt.figure(figsize=(6,4))
plt.bar(summary["section"], summary["mean"], yerr=1.96*summary["se"], capsize=5)
plt.ylabel("Mean Δ (sim_latin − sim_arabic)")
plt.xlabel("Manuscript Section")
plt.title("Latin vs Arabic Attribution by Section")
plt.tight_layout()
plt.savefig("Phase110/out/p110_section_deltas.png", dpi=200)
plt.show()
