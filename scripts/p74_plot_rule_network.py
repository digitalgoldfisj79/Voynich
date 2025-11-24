#!/usr/bin/env python3
"""
Phase 74: Rule PMI Network Export

Reads:
  - Phase71/out/p71_rule_clusters.tsv
  - Phase72/out/p72_rule_pmi_network.tsv

Writes:
  - Phase74/out/p74_rule_network_nodes.tsv
  - Phase74/out/p74_rule_network_edges.tsv
  - Phase74/out/p74_rule_network_layout.tsv
  - Phase74/out/p74_rule_network.gexf

Use:
  cd Voynich_Reproducible_Core
  python3 scripts/p74_plot_rule_network.py

The outputs are suitable for:
  - Gephi (TSV or GEXF)
  - Cytoscape
  - Static plotting in later phases
"""

import os
import math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P71_CLUSTERS = os.path.join(BASE, "Phase71", "out", "p71_rule_clusters.tsv")
P72_PMI = os.path.join(BASE, "Phase72", "out", "p72_rule_pmi_network.tsv")

OUT_DIR = os.path.join(BASE, "Phase74", "out")
NODES_TSV = os.path.join(OUT_DIR, "p74_rule_network_nodes.tsv")
EDGES_TSV = os.path.join(OUT_DIR, "p74_rule_network_edges.tsv")
LAYOUT_TSV = os.path.join(OUT_DIR, "p74_rule_network_layout.tsv")
GEXF_FILE = os.path.join(OUT_DIR, "p74_rule_network.gexf")


def ensure_outdir():
    os.makedirs(OUT_DIR, exist_ok=True)


def load_clusters(path):
    """
    p71_rule_clusters.tsv format (from p71_cluster_rules.py), expected:

    rule_id label   freq    cluster_id

    Returns:
      clusters: dict[rule_id] = cluster_id
      labels:   dict[rule_id] = label
      freqs:    dict[rule_id] = int freq
    """
    clusters = {}
    labels = {}
    freqs = {}
    if not os.path.isfile(path):
        print(f"[WARN] Cluster file not found: {path}")
        return clusters, labels, freqs

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            if line.startswith("#") or line.lower().startswith("rule_id"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            rid, label, freq, cid = parts[0], parts[1], parts[2], parts[3]
            try:
                freqs[rid] = int(freq)
            except ValueError:
                continue
            clusters[rid] = cid
            labels[rid] = label

    print(f"[INFO] Loaded {len(labels)} clustered rules from {path}")
    return clusters, labels, freqs


def load_pmi_edges(path):
    """
    p72_rule_pmi_network.tsv format, expected:

    #rule_i rule_j  freq_i  freq_j  cooc    PMI_bits

    Returns:
      edges: list of (ri, rj, cooc, pmi)
    """
    edges = []
    if not os.path.isfile(path):
        print(f"[WARN] PMI network file not found: {path}")
        return edges

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            if line.startswith("#") or line.lower().startswith("rule_i"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 6:
                continue
            ri, rj = parts[0], parts[1]
            try:
                cooc = int(parts[4])
                pmi = float(parts[5])
            except ValueError:
                continue
            if ri == "" or rj == "":
                continue
            edges.append((ri, rj, cooc, pmi))

    print(f"[INFO] Loaded {len(edges)} PMI edges from {path}")
    return edges


def build_graph(edges):
    """
    Build adjacency and degree dicts from edge list.
    Returns:
      adj: dict[rule_id] = set(neighbors)
      weight_sum: dict[rule_id] = sum PMI of incident edges
    """
    adj = {}
    weight_sum = {}
    for ri, rj, cooc, pmi in edges:
        if ri not in adj:
            adj[ri] = set()
            weight_sum[ri] = 0.0
        if rj not in adj:
            adj[rj] = set()
            weight_sum[rj] = 0.0
        adj[ri].add(rj)
        adj[rj].add(ri)
        weight_sum[ri] += pmi
        weight_sum[rj] += pmi
    return adj, weight_sum


def write_nodes(nodes_path, layout_path, clusters, labels, freqs, adj, weight_sum):
    """
    Writes:
      - nodes TSV with metadata
      - layout TSV with deterministic 2D coordinates
    """
    # Use all nodes that appear in adjacency
    node_ids = sorted(adj.keys())

    # Simple circular layout, radius scaled by log-degree
    n = len(node_ids)
    if n == 0:
        print("[WARN] No nodes to write.")
        return

    with open(nodes_path, "w", encoding="utf-8") as fn, \
         open(layout_path, "w", encoding="utf-8") as fl:

        fn.write("node_id\tlabel\tcluster_id\tfreq\tdegree\tpmi_weight_sum\n")
        fl.write("node_id\tx\ty\n")

        for idx, rid in enumerate(node_ids):
            label = labels.get(rid, rid)
            cid = clusters.get(rid, "NA")
            freq = freqs.get(rid, 0)
            deg = len(adj[rid])
            wsum = weight_sum.get(rid, 0.0)

            # position on circle
            angle = 2.0 * math.pi * idx / n
            # radius: base 1.0 plus scaled log-degree
            radius = 1.0 + (math.log(deg + 1.0) if deg > 0 else 0.0) * 0.2
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            fn.write(f"{rid}\t{label}\t{cid}\t{freq}\t{deg}\t{wsum:.3f}\n")
            fl.write(f"{rid}\t{x:.4f}\t{y:.4f}\n")

    print(f"[OK] Wrote nodes → {nodes_path}")
    print(f"[OK] Wrote layout → {layout_path}")


def write_edges(edges_path, edges):
    """
    Writes edge list TSV.
    """
    with open(edges_path, "w", encoding="utf-8") as fe:
        fe.write("source\ttarget\tcooc\tPMI_bits\n")
        for ri, rj, cooc, pmi in edges:
            fe.write(f"{ri}\t{rj}\t{cooc}\t{pmi:.4f}\n")
    print(f"[OK] Wrote edges → {edges_path}")


def write_gexf(gexf_path, clusters, labels, freqs, adj, weight_sum, edges):
    """
    Optional: Write a minimal GEXF file for Gephi.

    No external dependencies. Only uses nodes present in adj.
    """
    node_ids = sorted(adj.keys())
    if not node_ids:
        print("[WARN] No nodes, skipping GEXF.")
        return

    node_index = {rid: i for i, rid in enumerate(node_ids)}

    with open(gexf_path, "w", encoding="utf-8") as fx:
        fx.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fx.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
        fx.write('  <graph mode="static" defaultedgetype="undirected">\n')

        # Attributes
        fx.write('    <attributes class="node">\n')
        fx.write('      <attribute id="0" title="label" type="string"/>\n')
        fx.write('      <attribute id="1" title="cluster" type="string"/>\n')
        fx.write('      <attribute id="2" title="freq" type="integer"/>\n')
        fx.write('      <attribute id="3" title="degree" type="integer"/>\n')
        fx.write('      <attribute id="4" title="pmi_weight_sum" type="float"/>\n')
        fx.write('    </attributes>\n')

        # Nodes
        fx.write('    <nodes>\n')
        for rid in node_ids:
            label = labels.get(rid, rid)
            cid = clusters.get(rid, "NA")
            freq = freqs.get(rid, 0)
            deg = len(adj[rid])
            wsum = weight_sum.get(rid, 0.0)
            fx.write(f'      <node id="{node_index[rid]}" label="{label}">\n')
            fx.write('        <attvalues>\n')
            fx.write(f'          <attvalue for="0" value="{label}"/>\n')
            fx.write(f'          <attvalue for="1" value="{cid}"/>\n')
            fx.write(f'          <attvalue for="2" value="{freq}"/>\n')
            fx.write(f'          <attvalue for="3" value="{deg}"/>\n')
            fx.write(f'          <attvalue for="4" value="{wsum:.3f}"/>\n')
            fx.write('        </attvalues>\n')
            fx.write('      </node>\n')
        fx.write('    </nodes>\n')

        # Edges
        fx.write('    <edges>\n')
        for eid, (ri, rj, cooc, pmi) in enumerate(edges):
            if ri not in node_index or rj not in node_index:
                continue
            s = node_index[ri]
            t = node_index[rj]
            fx.write(f'      <edge id="{eid}" source="{s}" target="{t}" weight="{pmi:.4f}"/>\n')
        fx.write('    </edges>\n')

        fx.write('  </graph>\n')
        fx.write('</gexf>\n')

    print(f"[OK] Wrote GEXF → {gexf_path}")


def main():
    ensure_outdir()

    clusters, labels, freqs = load_clusters(P71_CLUSTERS)
    edges = load_pmi_edges(P72_PMI)

    if not edges:
        print("[WARN] No edges loaded; nothing to export.")
        return

    adj, weight_sum = build_graph(edges)

    write_nodes(NODES_TSV, LAYOUT_TSV, clusters, labels, freqs, adj, weight_sum)
    write_edges(EDGES_TSV, edges)
    write_gexf(GEXF_FILE, clusters, labels, freqs, adj, weight_sum, edges)

    print("[OK] Phase 74 export complete.")


if __name__ == "__main__":
    main()
