# Data dictionary — DDI Network Analytics

> **Educational/demo only — not medical advice.** This dataset is
> synthetic-but-realistic and built for learning network analytics. No pair
> in it is a verified clinical fact, and nothing here should guide real
> prescribing, dispensing, or self-medication decisions. Always consult a
> qualified pharmacist or doctor for real medicine questions.

## medicines.csv (152 rows)

| Column | Meaning |
|---|---|
| `medicine_id` | Stable ID, `M001`–`M152` |
| `generic_name` | Generic (non-brand) medicine name, lowercase |
| `category` | Pharmacological category (24 values, e.g. `nsaid`, `ssri`, `statin`) |
| `typical_use` | One-line plain-language use for the category |
| `risk_note` | One-line category-level caution |

## interactions.csv (500 rows)

| Column | Meaning |
|---|---|
| `drug_a`, `drug_b` | The interacting pair, alphabetically ordered (undirected) |
| `severity` | `major` (156), `moderate` (337), or `minor` (7) |
| `mechanism` | Plain-language mechanism, e.g. "Increased bleeding risk" |
| `evidence_note` | Provenance: "Well-known textbook pair; illustrative only" for
curated pairs, or "Rule-based illustrative pair (category/QT pattern)" for
pairs sampled from category-level rules |

## How the data was built

`analysis/generate_data.py` (seed 42, deterministic) combines:

1. **~80 curated pairs** — well-known textbook-level interactions
   (warfarin + NSAIDs, statin + clarithromycin, opioid + benzodiazepine…).
2. **Category rules** — e.g. anticoagulant × NSAID → bleeding risk,
   SSRI × triptan → serotonin-syndrome risk, QT-prolonger × QT-prolonger →
   QT risk — sampled until the dataset reaches exactly 500 pairs.

## Known limitations (state these in any write-up)

- Illustrative only: severities and mechanisms are simplified teaching
  labels, not clinical guidance.
- No doses, patient factors, or timing — real interaction risk depends on
  all three.
- Three medicines are network isolates (cetirizine, loratadine,
  fexofenadine): second-generation antihistamines with few documented
  interactions in this teaching set. That is a finding, not a bug.
- The network is undirected and unweighted beyond severity (major = 3,
  moderate = 2, minor = 1).
