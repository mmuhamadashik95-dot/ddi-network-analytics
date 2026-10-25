# DDI Network Analytics — Medicine Interaction Network Intelligence

> **Educational/demo only — not medical advice.** Every dataset, chart, and
> dashboard page in this project is an illustrative teaching artefact. No
> interaction shown here is a verified clinical fact, and nothing here
> should guide real prescribing, dispensing, or self-medication. For real
> medicine questions, consult a qualified pharmacist or doctor.

## The problem

A prescription is not a list — it is a **network**. Every medicine a patient
takes can interact with every other one, and the danger concentrates in a
few "hub" medicines that interact with dozens of others. Traditional
drug-interaction tools answer one pair at a time ("does A interact with
B?"). This project answers the network question: **which medicines are the
hubs, which clusters interact densely, and where does risk concentrate?**

## Why this is novel (not another Titanic tutorial)

- **Graph analytics on a domain that is naturally a network.** Most
  beginner analytics projects are tabular (predict a price, classify a
  passenger). Here the data structure *is* the insight: centrality,
  communities, and bridges.
- **A transparent, defensible risk score** — one formula, explained in one
  sentence, not a black-box model.
- **A real, runnable dashboard** with a medicine lookup, not just a
  notebook.
- **Honest data provenance** — curated textbook pairs + documented
  category rules, with limitations stated up front (see
  `data/DATA_DICTIONARY.md`).

## Dataset

- `data/medicines.csv` — **152** common generic medicines across
  **24 categories** (anticoagulants, NSAIDs, antibiotics, SSRIs, statins…).
- `data/interactions.csv` — **500** undirected medicine pairs:
  **156 major, 337 moderate, 7 minor**, each with a mechanism and an
  evidence note.
- Built deterministically (`analysis/generate_data.py`, seed 42) from
  ~80 curated well-known pairs plus category-level rules
  (e.g. anticoagulant × NSAID → bleeding risk; QT-prolonger ×
  QT-prolonger → QT risk). Full details in `data/DATA_DICTIONARY.md`.

## Method

1. **Build the graph** (`analysis/build_network.py`) — medicines are nodes,
   interactions are edges weighted by severity (major = 3, moderate = 2,
   minor = 1). Validation rejects self-loops, duplicates, unknown
   medicines, and invalid severities.
2. **Centrality** (`analysis/centrality.py`) — degree, betweenness, and
   eigenvector centrality per medicine.
3. **Communities** (`analysis/communities.py`) — greedy modularity
   detection finds densely interacting clusters.
4. **Risk score** (`analysis/risk_score.py`) — one transparent number:

   `risk = 0.5 × severity-weighted degree + 0.3 × degree centrality +
   0.2 × betweenness centrality` (each component normalised to [0, 1]).

## Key findings (from the actual run)

Network: **152 medicines, 500 interactions, density 0.0436, average
degree 6.58, largest connected component 146 medicines.**

### Top 10 riskiest hub medicines

| # | Medicine | Category | Degree | Severity-weighted degree | Risk score |
|---|----------|----------|--------|--------------------------|------------|
| 1 | ketorolac | NSAID | 29 | 63 | 0.8958 |
| 2 | ibuprofen | NSAID | 26 | 58 | 0.8320 |
| 3 | naproxen | NSAID | 26 | 60 | 0.8132 |
| 4 | warfarin | anticoagulant | 16 | 42 | 0.6989 |
| 5 | clarithromycin | antibiotic | 17 | 46 | 0.6820 |
| 6 | indomethacin | NSAID | 22 | 47 | 0.6422 |
| 7 | diclofenac | NSAID | 21 | 46 | 0.6177 |
| 8 | citalopram | SSRI | 18 | 45 | 0.5864 |
| 9 | meloxicam | NSAID | 20 | 43 | 0.5823 |
| 10 | mefenamic acid | NSAID | 20 | 44 | 0.5749 |

**Reading this:** NSAIDs dominate the hub list — not because any single
NSAID is the "most dangerous" drug, but because the NSAID class touches
anticoagulants, SSRIs, ACE inhibitors, diuretics, lithium, and
methotrexate at once. Warfarin ranks 4th despite a modest degree (16)
because its edges are disproportionately *major* — exactly what the
severity weighting is designed to surface. Clarithromycin is the top
non-NSAID hub: a classic enzyme inhibitor that raises levels of statins,
colchicine, and QT-prolonging drugs.

### Communities: 9 clusters, 5 connected components

| Community | Size | Internal edges | Dominant pattern |
|-----------|------|----------------|------------------|
| 0 | 63 | 243 | Bleeding-risk cluster (anticoagulants, NSAIDs, SSRIs, antiplatelets) |
| 1 | 36 | 88 | Sedation cluster (opioids, benzodiazepines, antipsychotics) |
| 2 | 20 | 40 | Hypoglycemia cluster (antidiabetics + enzyme inhibitors) |
| 3 | 15 | 44 | QT-prolongation cluster |
| 4 | 12 | 19 | Bradycardia / heart-block cluster |
| 5 | 3 | 2 | Severe-hypotension cluster (sildenafil + nitrates) |
| 6–8 | 1 each | 0 | Isolates (see below) |

**The most dangerous cluster is Community 0** — 63 medicines, 243 internal
edges, dominated by bleeding risk. It is the network's core: remove its
hubs and the network fragments.

**The isolates are a finding, not a bug:** the only medicines with zero
interactions in this teaching set are cetirizine, loratadine, and
fexofenadine — second-generation antihistamines, which genuinely have
few documented interactions. A beginner project would hide this; a
role-model project explains it.

## How to run

```bash
cd ddi-network-analytics
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. (Re)generate the dataset — optional, CSVs are already included
python analysis/generate_data.py

# 2. Run the full pipeline (tables + charts into outputs/)
python analysis/run_all.py

# 3. Run individual steps
python analysis/build_network.py
python analysis/centrality.py
python analysis/communities.py
python analysis/risk_score.py

# 4. Launch the dashboard
streamlit run app/app.py

# 5. Run the tests
pytest tests/ -q
```

## Project structure

```
ddi-network-analytics/
├── README.md
├── LICENSE (MIT)
├── requirements.txt
├── data/
│   ├── medicines.csv
│   ├── interactions.csv
│   └── DATA_DICTIONARY.md
├── analysis/
│   ├── generate_data.py     # deterministic dataset builder (seed 42)
│   ├── build_network.py     # graph construction + validation
│   ├── centrality.py        # degree / betweenness / eigenvector
│   ├── communities.py       # greedy modularity communities
│   ├── risk_score.py        # transparent composite risk score
│   └── run_all.py           # full pipeline + charts
├── app/
│   └── app.py               # Streamlit dashboard (4 pages)
├── tests/
│   ├── test_graph.py        # graph + data validation (12 tests)
│   └── test_risk.py         # risk-score tests (6 tests)
└── outputs/
    ├── graph_stats.json
    ├── centrality.csv
    ├── risk_scores.csv
    ├── top_hubs.csv         # top 20 hubs
    ├── medicine_communities.csv
    ├── community_summary.csv
    ├── network_by_community.png
    ├── degree_distribution.png
    └── top_hubs.png
```

## Dashboard pages

1. **Network overview** — headline stats, community network chart,
   severity mix, degree distribution.
2. **Riskiest hubs** — top-20 table + bar chart.
3. **Community explorer** — pick a cluster, see members and its dominant
   mechanism.
4. **Medicine lookup** — pick any medicine, see its interactions and risk
   score.

## Future work

- Directed, weighted edges with dose and timing information.
- Patient-regimen simulation: score a whole prescription list, not one drug.
- Temporal analysis: how the network changes as new medicines are added.
- Link prediction: flag pairs that *should* be studied, using community
  structure (common neighbours) — a genuine research extension.
- Replace the teaching dataset with a licensed clinical interaction
  database under proper terms, keeping the same pipeline.

## Disclaimer (repeated deliberately)

Educational/demo only — not medical advice. This project demonstrates
network analytics on an illustrative dataset. It does not diagnose, treat,
or recommend anything for any real person.
