"""Run the full pipeline: graph, centrality, communities, risk scores, charts.

Charts (all saved to outputs/):
  * network_by_community.png — spring layout, nodes coloured by community,
    sized by degree, major edges drawn darker.
  * degree_distribution.png — histogram of node degrees.
  * top_hubs.png — horizontal bar chart of the 15 riskiest medicines.

Educational/demo only — not medical advice.

Run:  python analysis/run_all.py
"""

from __future__ import annotations

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from analysis.build_network import (
    build_graph,
    graph_stats,
    load_interactions,
    load_medicines,
)
from analysis.centrality import compute_centrality
from analysis.communities import community_tables, detect_communities
from analysis.risk_score import compute_risk_scores

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"

NAVY = "#072A43"
TEAL = "#0A6E78"
AMBER = "#FFB020"
PALETTE = ["#0A6E78", "#FFB020", "#E4572E", "#6A4C93", "#2A9D8F",
           "#F4A261", "#457B9D", "#E76F51", "#8AB17D", "#F2CC8F"]


def plot_network(graph: nx.Graph, membership: dict[str, int],
                 risk: pd.DataFrame, path: Path) -> None:
    """Draw the network coloured by community, sized by risk score."""
    pos = nx.spring_layout(graph, seed=42, k=0.35)
    risk_map = dict(zip(risk["medicine"], risk["risk_score"]))
    sizes = [120 + 900 * risk_map[n] for n in graph.nodes]
    colors = [PALETTE[membership[n] % len(PALETTE)] for n in graph.nodes]
    major_edges = [(u, v) for u, v, d in graph.edges(data=True)
                   if d["severity"] == "major"]
    other_edges = [(u, v) for u, v, d in graph.edges(data=True)
                   if d["severity"] != "major"]
    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.18,
                           edge_color="#9AA5B1", ax=ax)
    nx.draw_networkx_edges(graph, pos, edgelist=major_edges, alpha=0.45,
                           edge_color="#C0392B", width=1.2, ax=ax)
    nx.draw_networkx_nodes(graph, pos, node_size=sizes, node_color=colors,
                           alpha=0.9, ax=ax)
    top_labels = risk.head(12)["medicine"].tolist()
    nx.draw_networkx_labels(
        graph, pos, labels={n: n for n in top_labels},
        font_size=7, font_color=NAVY, ax=ax)
    ax.set_title("Medicine Interaction Network — colour: community, "
                 "size: risk score, red edges: major severity",
                 fontsize=12, color=NAVY)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_degree_distribution(graph: nx.Graph, path: Path) -> None:
    """Draw a histogram of node degrees."""
    degrees = [d for _, d in graph.degree()]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(degrees, bins=range(0, max(degrees) + 2), color=TEAL,
            edgecolor="white")
    ax.set_xlabel("Degree (number of interacting medicines)")
    ax.set_ylabel("Number of medicines")
    ax.set_title("Degree distribution — a few hubs, many low-degree medicines",
                 color=NAVY)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_top_hubs(risk: pd.DataFrame, path: Path) -> None:
    """Draw a bar chart of the 15 highest risk scores."""
    top = risk.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top["medicine"], top["risk_score"], color=AMBER,
            edgecolor=NAVY)
    ax.set_xlabel("Composite risk score (0–1)")
    ax.set_title("Top 15 riskiest hub medicines (illustrative dataset)",
                 color=NAVY)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    """Run every analysis step and write all outputs."""
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    graph = build_graph(load_medicines(), load_interactions())
    stats = graph_stats(graph)
    centrality = compute_centrality(graph)
    communities = detect_communities(graph)
    medicine_frame, summary_frame = community_tables(graph, communities)
    risk = compute_risk_scores(graph, centrality)

    import json
    with open(OUTPUTS / "graph_stats.json", "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    centrality.to_csv(OUTPUTS / "centrality.csv", index=False)
    medicine_frame.to_csv(OUTPUTS / "medicine_communities.csv", index=False)
    summary_frame.to_csv(OUTPUTS / "community_summary.csv", index=False)
    risk.to_csv(OUTPUTS / "risk_scores.csv", index=False)
    risk.head(20).to_csv(OUTPUTS / "top_hubs.csv", index=False)

    membership = {row.medicine: row.community_id
                  for row in medicine_frame.itertuples(index=False)}
    plot_network(graph, membership, risk, OUTPUTS / "network_by_community.png")
    plot_degree_distribution(graph, OUTPUTS / "degree_distribution.png")
    plot_top_hubs(risk, OUTPUTS / "top_hubs.png")

    print(f"nodes={stats['nodes']} edges={stats['edges']} "
          f"communities={len(communities)}")
    print("TOP 10 HUBS:")
    print(risk.head(10)[["medicine", "category", "degree",
                         "severity_weighted_degree", "risk_score"]]
          .to_string(index=False))
    print("\nCOMMUNITIES:")
    print(summary_frame[["community_id", "size", "internal_edges",
                         "top_category", "top_mechanism"]].to_string(index=False))


if __name__ == "__main__":
    main()
