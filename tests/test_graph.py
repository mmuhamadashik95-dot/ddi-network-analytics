"""Tests for graph building and data validation.

Run:  pytest tests/ -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.build_network import (  # noqa: E402
    VALID_SEVERITIES,
    build_graph,
    load_interactions,
    load_medicines,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def tables():
    """Load the dataset once for the whole module."""
    return load_medicines(), load_interactions()


@pytest.fixture(scope="module")
def graph(tables):
    """Build the graph once for the whole module."""
    meds, inter = tables
    return build_graph(meds, inter)


def test_medicine_count_in_range(tables):
    """Dataset holds 150–200 medicines."""
    meds, _ = tables
    assert 150 <= len(meds) <= 200


def test_interaction_count_in_range(tables):
    """Dataset holds 400–600 interactions."""
    _, inter = tables
    assert 400 <= len(inter) <= 600


def test_no_empty_cells(tables):
    """No empty cells anywhere in either CSV."""
    meds, inter = tables
    assert not meds.isna().any().any()
    assert not inter.isna().any().any()


def test_severity_values_valid(tables):
    """Every severity is major, moderate, or minor."""
    _, inter = tables
    assert set(inter["severity"]).issubset(VALID_SEVERITIES)


def test_no_self_loops(tables):
    """No medicine interacts with itself."""
    _, inter = tables
    assert (inter["drug_a"] != inter["drug_b"]).all()


def test_no_duplicate_undirected_pairs(tables):
    """No pair appears twice in either direction."""
    _, inter = tables
    keys = inter.apply(
        lambda r: tuple(sorted((r["drug_a"], r["drug_b"]))), axis=1)
    assert not keys.duplicated().any()


def test_all_interaction_endpoints_are_medicines(tables):
    """Every interaction endpoint exists in medicines.csv."""
    meds, inter = tables
    known = set(meds["generic_name"])
    assert set(inter["drug_a"]).issubset(known)
    assert set(inter["drug_b"]).issubset(known)


def test_graph_matches_tables(graph, tables):
    """Graph node/edge counts match the CSVs exactly."""
    meds, inter = tables
    assert graph.number_of_nodes() == len(meds)
    assert graph.number_of_edges() == len(inter)


def test_graph_has_no_isolated_majority(graph):
    """Most medicines are connected (isolates are a small minority)."""
    isolates = [n for n, d in graph.degree() if d == 0]
    assert len(isolates) <= 10


def test_every_node_has_category(graph):
    """Every node carries its category attribute."""
    assert all("category" in graph.nodes[n] for n in graph.nodes)


def test_every_edge_has_severity_and_weight(graph):
    """Every edge carries severity and a positive severity weight."""
    for _, _, data in graph.edges(data=True):
        assert data["severity"] in VALID_SEVERITIES
        assert data["weight"] > 0


def test_outputs_exist():
    """The pipeline's headline outputs are present and non-empty."""
    for name in ("top_hubs.csv", "community_summary.csv",
                 "centrality.csv", "risk_scores.csv"):
        path = ROOT / "outputs" / name
        assert path.exists() and path.stat().st_size > 0, name
    assert len(pd.read_csv(ROOT / "outputs" / "top_hubs.csv")) == 20
