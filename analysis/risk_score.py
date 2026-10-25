"""Composite risk score: one transparent number per medicine.

risk_score = 0.5 * severity_weighted_degree (normalised)
           + 0.3 * degree_centrality
           + 0.2 * betweenness_centrality

Severity weights: major = 3, moderate = 2, minor = 1. Every component is
normalised to [0, 1] before weighting, so the score is comparable across
networks and the formula can be explained in one sentence. The score ranks
medicines *inside this illustrative dataset only* — it is not a clinical
risk rating for any patient.

Educational/demo only — not medical advice.

Run:  python analysis/risk_score.py
Writes: outputs/risk_scores.csv, outputs/top_hubs.csv (top 20)
"""

from __future__ import annotations

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from pathlib import Path

import pandas as pd

from analysis.build_network import (
    SEVERITY_WEIGHT,
    build_graph,
    load_interactions,
    load_medicines,
)
from analysis.centrality import compute_centrality

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"

WEIGHTS = {"severity_degree": 0.5, "degree_centrality": 0.3, "betweenness": 0.2}


def _normalise(series: pd.Series) -> pd.Series:
    """Min-max normalise to [0, 1]; all-zero series stays zero."""
    span = series.max() - series.min()
    if span == 0:
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / span


def compute_risk_scores(graph, centrality: pd.DataFrame) -> pd.DataFrame:
    """Return the risk-score table ranked highest first."""
    sev_degree = {}
    for node in graph.nodes:
        sev_degree[node] = sum(
            SEVERITY_WEIGHT[d["severity"]] for _, _, d in graph.edges(node, data=True)
        )
    frame = centrality.copy()
    frame["severity_weighted_degree"] = frame["medicine"].map(sev_degree)
    frame["risk_score"] = (
        WEIGHTS["severity_degree"] * _normalise(frame["severity_weighted_degree"])
        + WEIGHTS["degree_centrality"] * _normalise(frame["degree_centrality"])
        + WEIGHTS["betweenness"] * _normalise(frame["betweenness_centrality"])
    ).round(4)
    return frame.sort_values("risk_score", ascending=False).reset_index(drop=True)


def main() -> None:
    """Compute risk scores and save the full table + top-20 hubs."""
    graph = build_graph(load_medicines(), load_interactions())
    centrality = compute_centrality(graph)
    frame = compute_risk_scores(graph, centrality)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUTS / "risk_scores.csv", index=False)
    frame.head(20).to_csv(OUTPUTS / "top_hubs.csv", index=False)
    print(frame.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
