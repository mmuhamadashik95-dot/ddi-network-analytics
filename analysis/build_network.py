"""Build the medicine-interaction graph from the CSV dataset.

Nodes are medicines (with category / typical-use attributes). Edges are
interactions (with severity / mechanism attributes). The graph is undirected:
an interaction between A and B is the same edge as B and A.

Educational/demo only — not medical advice.

Run:  python analysis/build_network.py
Writes: outputs/graph_stats.json
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"

SEVERITY_WEIGHT = {"major": 3, "moderate": 2, "minor": 1}
VALID_SEVERITIES = set(SEVERITY_WEIGHT)


def load_medicines(path: Path = DATA / "medicines.csv") -> pd.DataFrame:
    """Load and validate the medicines table."""
    meds = pd.read_csv(path)
    required = {"medicine_id", "generic_name", "category", "typical_use", "risk_note"}
    missing = required - set(meds.columns)
    if missing:
        raise ValueError(f"medicines.csv missing columns: {missing}")
    if meds["generic_name"].duplicated().any():
        raise ValueError("duplicate generic_name in medicines.csv")
    if meds.isna().any().any():
        raise ValueError("empty cells in medicines.csv")
    return meds


def load_interactions(path: Path = DATA / "interactions.csv") -> pd.DataFrame:
    """Load and validate the interactions table."""
    inter = pd.read_csv(path)
    required = {"drug_a", "drug_b", "severity", "mechanism", "evidence_note"}
    missing = required - set(inter.columns)
    if missing:
        raise ValueError(f"interactions.csv missing columns: {missing}")
    if not set(inter["severity"]).issubset(VALID_SEVERITIES):
        raise ValueError("invalid severity value in interactions.csv")
    if (inter["drug_a"] == inter["drug_b"]).any():
        raise ValueError("self-loop in interactions.csv")
    if inter.isna().any().any():
        raise ValueError("empty cells in interactions.csv")
    return inter


def build_graph(meds: pd.DataFrame, inter: pd.DataFrame) -> nx.Graph:
    """Build an undirected NetworkX graph from the two tables."""
    graph = nx.Graph()
    for row in meds.itertuples(index=False):
        graph.add_node(
            row.generic_name,
            medicine_id=row.medicine_id,
            category=row.category,
            typical_use=row.typical_use,
            risk_note=row.risk_note,
        )
    unknown = (set(inter["drug_a"]) | set(inter["drug_b"])) - set(graph.nodes)
    if unknown:
        raise ValueError(f"interactions reference unknown medicines: {sorted(unknown)}")
    for row in inter.itertuples(index=False):
        graph.add_edge(
            row.drug_a,
            row.drug_b,
            severity=row.severity,
            weight=SEVERITY_WEIGHT[row.severity],
            mechanism=row.mechanism,
            evidence_note=row.evidence_note,
        )
    return graph


def graph_stats(graph: nx.Graph) -> dict:
    """Return headline graph statistics as plain JSON-able values."""
    degrees = dict(graph.degree())
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(nx.density(graph), 4),
        "connected_components": nx.number_connected_components(graph),
        "largest_component_nodes": len(max(nx.connected_components(graph), key=len)),
        "average_degree": round(sum(degrees.values()) / len(degrees), 2),
        "max_degree": max(degrees.values()),
        "max_degree_medicines": sorted(
            [n for n, d in degrees.items() if d == max(degrees.values())]
        ),
        "severity_counts": {
            sev: sum(1 for _, _, d in graph.edges(data=True) if d["severity"] == sev)
            for sev in sorted(VALID_SEVERITIES)
        },
        "disclaimer": "Educational/demo only — not medical advice.",
    }


def main() -> None:
    """Build the graph and print/write its statistics."""
    meds = load_medicines()
    inter = load_interactions()
    graph = build_graph(meds, inter)
    stats = graph_stats(graph)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    with open(OUTPUTS / "graph_stats.json", "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
