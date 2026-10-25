"""Centrality analysis: which medicines are the network's riskiest hubs?

Three complementary measures are computed for every medicine:
  * degree centrality      — how many other medicines it interacts with
  * betweenness centrality — how often it sits on shortest paths between
                             other medicines (a "bridge" medicine)
  * eigenvector centrality — whether it interacts with other hubs

Educational/demo only — not medical advice.

Run:  python analysis/centrality.py
Writes: outputs/centrality.csv (all medicines, ranked by degree)
"""

from __future__ import annotations

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from pathlib import Path

import networkx as nx
import pandas as pd

from analysis.build_network import build_graph, load_interactions, load_medicines

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"


def compute_centrality(graph: nx.Graph) -> pd.DataFrame:
    """Return a DataFrame with degree, betweenness and eigenvector centrality."""
    degree = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph, weight="weight", seed=42)
    try:
        eigenvector = nx.eigenvector_centrality(graph, weight="weight", max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        eigenvector = {node: 0.0 for node in graph.nodes}
    rows = [
        {
            "medicine": node,
            "category": graph.nodes[node]["category"],
            "degree": graph.degree[node],
            "degree_centrality": round(degree[node], 4),
            "betweenness_centrality": round(betweenness[node], 4),
            "eigenvector_centrality": round(eigenvector[node], 4),
        }
        for node in graph.nodes
    ]
    frame = pd.DataFrame(rows)
    return frame.sort_values(
        ["degree", "betweenness_centrality"], ascending=False
    ).reset_index(drop=True)


def main() -> None:
    """Compute centrality and save the ranked table."""
    graph = build_graph(load_medicines(), load_interactions())
    frame = compute_centrality(graph)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUTS / "centrality.csv", index=False)
    print(frame.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
