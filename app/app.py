"""DDI Network Analytics — Streamlit dashboard.

Pages (sidebar navigation):
  * Network overview — headline stats + the community network chart
  * Riskiest hubs — top-20 hub table + bar chart
  * Community explorer — pick a community, see its members and top mechanism
  * Medicine lookup — pick any medicine, see its interactions + risk score

Educational/demo only — not medical advice. The disclaimer is shown on
every page (sidebar + main area).

Run:  streamlit run app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"

DISCLAIMER = "Educational/demo only — not medical advice."

st.set_page_config(page_title="DDI Network Analytics", layout="wide")
st.sidebar.title("DDI Network Analytics")
st.sidebar.warning(DISCLAIMER)


@st.cache_data
def load_all() -> dict[str, pd.DataFrame]:
    """Load the dataset and precomputed outputs (cached per session)."""
    return {
        "medicines": pd.read_csv(DATA / "medicines.csv"),
        "interactions": pd.read_csv(DATA / "interactions.csv"),
        "risk": pd.read_csv(OUTPUTS / "risk_scores.csv"),
        "top_hubs": pd.read_csv(OUTPUTS / "top_hubs.csv"),
        "communities": pd.read_csv(OUTPUTS / "community_summary.csv"),
        "membership": pd.read_csv(OUTPUTS / "medicine_communities.csv"),
    }


try:
    tables = load_all()
except FileNotFoundError as exc:
    st.error(f"Missing output file: {exc}. Run `python analysis/run_all.py` first.")
    st.stop()

page = st.sidebar.radio(
    "Explore",
    ["Network overview", "Riskiest hubs", "Community explorer", "Medicine lookup"],
)

if page == "Network overview":
    st.title("Medicine Interaction Network Intelligence")
    st.caption(DISCLAIMER)
    meds, inter = tables["medicines"], tables["interactions"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Medicines", len(meds))
    col2.metric("Interactions", len(inter))
    col3.metric("Communities", len(tables["communities"]))
    col4.metric("Major interactions",
                int((inter["severity"] == "major").sum()))
    st.image(
        str(OUTPUTS / "network_by_community.png"),
        caption="Interaction network — colour: community, size: risk score, "
                "red edges: major severity",
        use_container_width=True,
    )
    st.subheader("Severity mix")
    st.bar_chart(inter["severity"].value_counts())
    st.subheader("Degree distribution")
    st.image(str(OUTPUTS / "degree_distribution.png"),
             use_container_width=True)

elif page == "Riskiest hubs":
    st.title("Riskiest hub medicines")
    st.caption(DISCLAIMER)
    st.write("Ranked by the transparent composite risk score: 0.5 × "
             "severity-weighted degree + 0.3 × degree centrality + "
             "0.2 × betweenness centrality (each component normalised).")
    st.dataframe(tables["top_hubs"], use_container_width=True)
    st.image(str(OUTPUTS / "top_hubs.png"), use_container_width=True)

elif page == "Community explorer":
    st.title("Community explorer")
    st.caption(DISCLAIMER)
    summary = tables["communities"]
    choice = st.selectbox(
        "Choose a community",
        options=summary["community_id"].tolist(),
        format_func=lambda cid: (
            f"Community {cid} — "
            f"{summary.loc[summary['community_id'] == cid, 'size'].iloc[0]} "
            f"medicines"),
    )
    row = summary[summary["community_id"] == choice].iloc[0]
    st.metric("Size", int(row["size"]))
    st.metric("Internal edges", int(row["internal_edges"]))
    st.write(f"**Top category:** {row['top_category']}")
    st.write(f"**Top mechanism:** {row['top_mechanism']}")
    members = tables["membership"]
    members = members[members["community_id"] == choice]
    st.dataframe(members, use_container_width=True)

else:  # Medicine lookup
    st.title("Medicine lookup")
    st.caption(DISCLAIMER)
    meds, inter, risk = (
        tables["medicines"], tables["interactions"], tables["risk"])
    name = st.selectbox("Choose a medicine", sorted(meds["generic_name"]))
    info = meds[meds["generic_name"] == name].iloc[0]
    score_row = risk[risk["medicine"] == name]
    st.write(f"**Category:** {info['category']}")
    st.write(f"**Typical use:** {info['typical_use']}")
    st.write(f"**Risk note:** {info['risk_note']}")
    if not score_row.empty:
        row = score_row.iloc[0]
        st.metric("Risk score (0–1)", float(row["risk_score"]))
        st.metric("Degree", int(row["degree"]))
        st.metric("Severity-weighted degree",
                  int(row["severity_weighted_degree"]))
    hits = inter[(inter["drug_a"] == name) | (inter["drug_b"] == name)].copy()
    hits["other"] = hits.apply(
        lambda r: r["drug_b"] if r["drug_a"] == name else r["drug_a"], axis=1)
    st.subheader(f"Interactions for {name} ({len(hits)})")
    if hits.empty:
        st.info("No interactions in this illustrative dataset — "
                "this medicine is a network isolate here.")
    else:
        st.dataframe(
            hits[["other", "severity", "mechanism"]].sort_values(
                "severity", ascending=False),
            use_container_width=True,
        )

st.sidebar.caption(DISCLAIMER)
