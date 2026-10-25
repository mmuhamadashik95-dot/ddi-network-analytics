"""Community detection: find densely interacting medicine clusters.

Greedy modularity maximisation groups medicines that interact with each other
far more than with the rest of the network. A cluster dominated by one
mechanism (e.g. bleeding risk) is a clinically meaningful pattern in this
illustrative dataset — and a strong portfolio talking point.

Educational/demo only — not medical advice.

Run:  python analysis/communities.py
Writes: outputs/medicine_communities.csv, outputs/community_summary.csv
"""

from __future__ import annotations

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd

from analysis.build_network import build_graph, load_interactions, load_medicines

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"


def detect_communities(graph: nx.Graph) -> list[set[str]]:
    """Return communities sorted by size (largest first)."""
    communities = list(
        nx.community.greedy_modularity_communities(graph, weight="weight")
    )
    return sorted(communities, key=len, reverse=True)


def community_tables(
    graph: nx.Graph, communities: list[set[str]]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return per-medicine and per-community summary tables."""
    membership = {}
    for cid, members in enumerate(communities):
        for node in members:
            membership[node] = cid
    medicine_rows = [
        {
            "medicine": node,
            "category": graph.nodes[node]["category"],
            "community_id": membership[node],
            "degree": graph.degree[node],
        }
        for node in graph.nodes
    ]
    summary_rows = []
    for cid, members in enumerate(communities):
        subgraph = graph.subgraph(members)
        mechanisms = Counter(
            d["mechanism"] for _, _, d in subgraph.edges(data=True)
        )
        categories = Counter(graph.nodes[n]["category"] for n in members)
        summary_rows.append(
            {
                "community_id": cid,
                "size": len(members),
                "internal_edges": subgraph.number_of_edges(),
                "top_category": categories.most_common(1)[0][0],
                "top_category_share": round(
                    categories.most_common(1)[0][1] / len(members), 2
                ),
                "top_mechanism": mechanisms.most_common(1)[0][0]
                if mechanisms
                else "none (isolated medicine)",
                "members": ", ".join(sorted(members)),
            }
        )
    return (
        pd.DataFrame(medicine_rows).sort_values(
            ["community_id", "degree"], ascending=[True, False]
        ),
        pd.DataFrame(summary_rows),
    )


def main() -> None:
    """Detect communities and save both tables."""
    graph = build_graph(load_medicines(), load_interactions())
    communities = detect_communities(graph)
    medicine_frame, summary_frame = community_tables(graph, communities)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    medicine_frame.to_csv(OUTPUTS / "medicine_communities.csv", index=False)
    summary_frame.to_csv(OUTPUTS / "community_summary.csv", index=False)
    print(f"communities: {len(communities)}")
    print(
        summary_frame[["community_id", "size", "internal_edges",
                       "top_category", "top_mechanism"]].to_string(index=False)
    )


if __name__ == "__main__":
    main()
