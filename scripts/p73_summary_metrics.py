#!/usr/bin/env python3
import os
import math
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOKENS_PATH = os.path.join(BASE, "corpora", "p6_voynich_tokens.txt")
CLUSTERS_PATH = os.path.join(BASE, "Phase71", "out", "p71_rule_clusters.tsv")
PMI_PATH = os.path.join(BASE, "Phase72", "out", "p72_rule_pmi_network.tsv")

def load_tokens(path):
    tokens = []
    if not os.path.isfile(path):
        print(f"[WARN] Tokens file not found: {path}")
        return tokens
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                tokens.append(line)
    return tokens

def load_clusters(path):
    """
    Expecting p71_rule_clusters.tsv with header like:
    cluster_id  rule_id rule_type freq
    or similar tab-delimited structure.

    We’ll treat first line starting without '#' as header
    and look for columns by name if present; otherwise
    assume: cluster_id, rule_id, freq.
    """
    clusters = defaultdict(list)  # cluster_id -> [rule_ids]
    cluster_sizes = defaultdict(int)
    if not os.path.isfile(path):
        print(f"[WARN] Cluster file not found: {path}")
        return clusters, cluster_sizes

    with open(path, "r", encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if header is None:
                # Heuristic: if contains non-numeric labels, treat as header
                if any(col.lower() in ("cluster_id", "cluster", "rule_id", "rule", "freq") for col in parts):
                    header = [c.lower() for c in parts]
                    continue
                else:
                    # No header, assume fixed layout
                    header = None

            if header:
                row = dict(zip(header, parts))
                cid = row.get("cluster_id") or row.get("cluster") or row.get("clusterid")
                rid = row.get("rule_id") or row.get("rule") or row.get("ruleid")
                freq = row.get("freq") or row.get("count") or "0"
            else:
                # Fallback: cluster_id, rule_id, freq
                if len(parts) < 2:
                    continue
                cid = parts[0]
                rid = parts[1]
                freq = parts[2] if len(parts) > 2 else "0"

            if not cid or not rid:
                continue

            clusters[cid].append(rid)
            try:
                cluster_sizes[cid] += int(freq)
            except ValueError:
                pass

    return clusters, cluster_sizes

def load_pmi_edges(path):
    """
    Expecting p72_rule_pmi_network.tsv with header:
    #rule_i rule_j  freq_i  freq_j  cooc    PMI_bits
    """
    edges = []
    if not os.path.isfile(path):
        print(f"[WARN] PMI file not found: {path}")
        return edges

    with open(path, "r", encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                # detect header after '#'
                if line.startswith("#") and "rule_i" in line:
                    header = [c.strip("#").strip().lower() for c in line.split()]
                continue

            parts = line.split("\t")
            if header is None:
                # Try whitespace-split header if tab not used
                # But given your sample it's tabbed, so assume:
                header = ["rule_i", "rule_j", "freq_i", "freq_j", "cooc", "pmi_bits"]

            if len(parts) < 6:
                # Try splitting by whitespace if tab count is off
                parts = line.split()
                if len(parts) < 6:
                    continue

            try:
                rule_i = parts[0]
                rule_j = parts[1]
                freq_i = int(parts[2])
                freq_j = int(parts[3])
                cooc = int(parts[4])
                pmi = float(parts[5])
            except ValueError:
                continue

            edges.append((rule_i, rule_j, freq_i, freq_j, cooc, pmi))

    return edges

def compute_pmi_stats(edges):
    if not edges:
        return None
    pmis = [e[5] for e in edges]
    n = len(pmis)
    mean_pmi = sum(pmis) / n
    sorted_pmis = sorted(pmis)
    if n % 2 == 1:
        median_pmi = sorted_pmis[n // 2]
    else:
        median_pmi = 0.5 * (sorted_pmis[n // 2 - 1] + sorted_pmis[n // 2])
    max_pmi = sorted_pmis[-1]
    # simple unbiased variance
    if n > 1:
        var = sum((x - mean_pmi) ** 2 for x in pmis) / (n - 1)
    else:
        var = 0.0
    return {
        "count": n,
        "mean": mean_pmi,
        "median": median_pmi,
        "max": max_pmi,
        "stdev": math.sqrt(var),
    }

def compute_graph_stats(edges):
    if not edges:
        return {
            "num_nodes": 0,
            "num_edges": 0,
            "density": 0.0,
            "num_components": 0,
        }

    # Build undirected graph
    adj = defaultdict(set)
    for r_i, r_j, *_ in edges:
        if r_i == r_j:
            continue
        adj[r_i].add(r_j)
        adj[r_j].add(r_i)

    nodes = list(adj.keys())
    num_nodes = len(nodes)
    num_edges = sum(len(v) for v in adj.values()) // 2

    # Density for simple undirected graph
    if num_nodes > 1:
        density = (2.0 * num_edges) / (num_nodes * (num_nodes - 1))
    else:
        density = 0.0

    # Connected components (DFS)
    visited = set()
    def dfs(start):
        stack = [start]
        comp = []
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            comp.append(v)
            for w in adj[v]:
                if w not in visited:
                    stack.append(w)
        return comp

    components = []
    for n in nodes:
        if n not in visited:
            comp = dfs(n)
            components.append(comp)

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "density": density,
        "num_components": len(components),
        "component_sizes": [len(c) for c in components],
    }

def main():
    print("[INFO] Phase 73 summary metrics")
    # 1. Tokens
    tokens = load_tokens(TOKENS_PATH)
    if tokens:
        print(f"[TOKENS] Loaded {len(tokens)} Voynich tokens from {TOKENS_PATH}")
    else:
        print("[TOKENS] No tokens loaded; check path/config.")

    # 2. Clusters
    clusters, cluster_sizes = load_clusters(CLUSTERS_PATH)
    if clusters:
        num_clusters = len(clusters)
        nontrivial = [cid for cid, rules in clusters.items() if len(rules) > 1]
        print(f"[CLUSTERS] Loaded {num_clusters} clusters from {CLUSTERS_PATH}")
        print(f"[CLUSTERS] Non-trivial clusters (>=2 rules): {len(nontrivial)}")
    else:
        print(f"[CLUSTERS] No cluster data found in {CLUSTERS_PATH}")

    # 3. PMI edges
    edges = load_pmi_edges(PMI_PATH)
    if not edges:
        print(f"[PMI] No PMI edges found in {PMI_PATH}")
        return

    pmi_stats = compute_pmi_stats(edges)
    graph_stats = compute_graph_stats(edges)

    print(f"[PMI] Edges: {pmi_stats['count']}")
    print(f"[PMI] Mean PMI_bits:   {pmi_stats['mean']:.3f}")
    print(f"[PMI] Median PMI_bits: {pmi_stats['median']:.3f}")
    print(f"[PMI] Max PMI_bits:    {pmi_stats['max']:.3f}")
    print(f"[PMI] Stdev PMI_bits:  {pmi_stats['stdev']:.3f}")

    print(f"[GRAPH] Nodes (rules with edges): {graph_stats['num_nodes']}")
    print(f"[GRAPH] Undirected edges:         {graph_stats['num_edges']}")
    print(f"[GRAPH] Density:                  {graph_stats['density']:.3f}")
    print(f"[GRAPH] Connected components:     {graph_stats['num_components']}")
    if graph_stats["component_sizes"]:
        sizes = ", ".join(str(s) for s in sorted(graph_stats["component_sizes"], reverse=True))
        print(f"[GRAPH] Component sizes:          {sizes}")

    print("[OK] Phase 73 summary complete.")

if __name__ == "__main__":
    main()
