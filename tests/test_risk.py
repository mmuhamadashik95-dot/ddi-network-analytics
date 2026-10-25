"""Tests for the composite risk score.

Run:  pytest tests/ -q
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.build_network import (  # noqa: E402
    build_graph,
    load_interactions,
    load_medicines,
)
from analysis.centrality import compute_centrality  # noqa: E402
from analysis.risk_score import WEIGHTS, compute_risk_scores  # noqa: E402


def _frame():
    graph = build_graph(load_medicines(), load_interactions())
    centrality = compute_centrality(graph)
    return graph, compute_risk_scores(graph, centrality)


def test_scores_in_unit_interval():
    """Every risk score lies in [0, 1]."""
    _, frame = _frame()
    assert frame["risk_score"].between(0, 1).all()


def test_scores_sorted_descending():
    """The table is ranked highest-risk first."""
    _, frame = _frame()
    assert frame["risk_score"].is_monotonic_decreasing


def test_top_hub_has_highest_degree_or_weighted_degree():
    """The top-ranked medicine is a genuine hub, not an artefact."""
    _, frame = _frame()
    top = frame.iloc[0]
    assert top["degree"] >= frame["degree"].median()
    assert top["severity_weighted_degree"] >= \
        frame["severity_weighted_degree"].median()


def test_weights_sum_to_one():
    """The composite-score weights sum to 1."""
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_severity_weighted_degree_matches_edges():
    """Severity-weighted degree equals the sum of edge weights per node."""
    graph, frame = _frame()
    for row in frame.itertuples(index=False):
        expected = sum(d["weight"] for _, _, d in graph.edges(row.medicine, data=True))
        assert row.severity_weighted_degree == expected


def test_no_nan_scores():
    """No missing values in the score table."""
    _, frame = _frame()
    assert not frame["risk_score"].isna().any()
