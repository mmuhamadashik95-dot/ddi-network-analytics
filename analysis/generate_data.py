"""Generate the illustrative DDI dataset for DDI Network Analytics.

The dataset is SYNTHETIC-BUT-REALISTIC and EDUCATIONAL ONLY. It is built from
two transparent ingredients:

1. A curated list of well-known interaction pairs (textbook-level knowledge,
   e.g. warfarin + NSAIDs -> bleeding risk). These are illustrative, NOT
   verified clinical facts for any individual patient.
2. Category-level rules (e.g. anticoagulant x NSAID -> bleeding risk) sampled
   deterministically, so the network is large enough for real graph analysis.

Every output row carries the disclaimer in the data dictionary and README.
No real patient data, phone numbers, or personal emails are used anywhere.

Run:  python analysis/generate_data.py
Writes: data/medicines.csv, data/interactions.csv
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ---------------------------------------------------------------------------
# Medicines: (generic_name, category)
# ---------------------------------------------------------------------------
MEDICINES: list[tuple[str, str]] = [
    # Anticoagulants
    ("warfarin", "anticoagulant"), ("heparin", "anticoagulant"),
    ("enoxaparin", "anticoagulant"), ("apixaban", "anticoagulant"),
    ("rivaroxaban", "anticoagulant"), ("dabigatran", "anticoagulant"),
    ("edoxaban", "anticoagulant"), ("fondaparinux", "anticoagulant"),
    # Antiplatelets
    ("aspirin", "antiplatelet"), ("clopidogrel", "antiplatelet"),
    ("ticagrelor", "antiplatelet"), ("prasugrel", "antiplatelet"),
    ("dipyridamole", "antiplatelet"), ("cilostazol", "antiplatelet"),
    # NSAIDs
    ("ibuprofen", "nsaid"), ("naproxen", "nsaid"), ("diclofenac", "nsaid"),
    ("celecoxib", "nsaid"), ("indomethacin", "nsaid"), ("ketorolac", "nsaid"),
    ("meloxicam", "nsaid"), ("mefenamic acid", "nsaid"),
    # Antibiotics
    ("amoxicillin", "antibiotic"), ("ampicillin", "antibiotic"),
    ("ceftriaxone", "antibiotic"), ("cefalexin", "antibiotic"),
    ("doxycycline", "antibiotic"), ("azithromycin", "antibiotic"),
    ("clarithromycin", "antibiotic"), ("erythromycin", "antibiotic"),
    ("ciprofloxacin", "antibiotic"), ("levofloxacin", "antibiotic"),
    ("metronidazole", "antibiotic"),
    ("trimethoprim-sulfamethoxazole", "antibiotic"),
    ("nitrofurantoin", "antibiotic"), ("vancomycin", "antibiotic"),
    ("gentamicin", "antibiotic"), ("clindamycin", "antibiotic"),
    ("moxifloxacin", "antibiotic"),
    # Antifungals
    ("fluconazole", "antifungal"), ("itraconazole", "antifungal"),
    ("ketoconazole", "antifungal"), ("voriconazole", "antifungal"),
    ("terbinafine", "antifungal"), ("amphotericin B", "antifungal"),
    # ACE inhibitors / ARBs
    ("lisinopril", "ace_inhibitor"), ("enalapril", "ace_inhibitor"),
    ("ramipril", "ace_inhibitor"), ("captopril", "ace_inhibitor"),
    ("losartan", "arb"), ("valsartan", "arb"), ("telmisartan", "arb"),
    ("candesartan", "arb"),
    # Beta blockers
    ("metoprolol", "beta_blocker"), ("atenolol", "beta_blocker"),
    ("propranolol", "beta_blocker"), ("carvedilol", "beta_blocker"),
    ("bisoprolol", "beta_blocker"), ("labetalol", "beta_blocker"),
    # Calcium channel blockers
    ("amlodipine", "calcium_channel_blocker"),
    ("nifedipine", "calcium_channel_blocker"),
    ("diltiazem", "calcium_channel_blocker"),
    ("verapamil", "calcium_channel_blocker"),
    ("felodipine", "calcium_channel_blocker"),
    # Diuretics / potassium-sparing diuretics
    ("furosemide", "diuretic"), ("hydrochlorothiazide", "diuretic"),
    ("bumetanide", "diuretic"), ("chlorthalidone", "diuretic"),
    ("indapamide", "diuretic"),
    ("spironolactone", "potassium_sparing_diuretic"),
    ("amiloride", "potassium_sparing_diuretic"),
    # Statins
    ("atorvastatin", "statin"), ("simvastatin", "statin"),
    ("rosuvastatin", "statin"), ("pravastatin", "statin"),
    ("lovastatin", "statin"),
    # Antidiabetics
    ("metformin", "antidiabetic"), ("glipizide", "antidiabetic"),
    ("gliclazide", "antidiabetic"), ("glimepiride", "antidiabetic"),
    ("sitagliptin", "antidiabetic"), ("empagliflozin", "antidiabetic"),
    ("dapagliflozin", "antidiabetic"), ("insulin glargine", "antidiabetic"),
    ("pioglitazone", "antidiabetic"),
    # SSRIs / SNRIs / TCAs
    ("sertraline", "ssri"), ("fluoxetine", "ssri"), ("paroxetine", "ssri"),
    ("escitalopram", "ssri"), ("citalopram", "ssri"), ("fluvoxamine", "ssri"),
    ("venlafaxine", "snri"), ("duloxetine", "snri"),
    ("desvenlafaxine", "snri"),
    ("amitriptyline", "tca"), ("nortriptyline", "tca"),
    ("imipramine", "tca"),
    # Antiepileptics
    ("carbamazepine", "antiepileptic"), ("valproic acid", "antiepileptic"),
    ("lamotrigine", "antiepileptic"), ("levetiracetam", "antiepileptic"),
    ("phenytoin", "antiepileptic"), ("gabapentin", "antiepileptic"),
    ("pregabalin", "antiepileptic"), ("topiramate", "antiepileptic"),
    # Antipsychotics
    ("haloperidol", "antipsychotic"), ("risperidone", "antipsychotic"),
    ("olanzapine", "antipsychotic"), ("quetiapine", "antipsychotic"),
    ("aripiprazole", "antipsychotic"), ("clozapine", "antipsychotic"),
    # Opioids
    ("morphine", "opioid"), ("tramadol", "opioid"), ("codeine", "opioid"),
    ("oxycodone", "opioid"), ("fentanyl", "opioid"), ("methadone", "opioid"),
    # Benzodiazepines
    ("diazepam", "benzodiazepine"), ("lorazepam", "benzodiazepine"),
    ("alprazolam", "benzodiazepine"), ("clonazepam", "benzodiazepine"),
    ("temazepam", "benzodiazepine"),
    # PPIs
    ("omeprazole", "ppi"), ("pantoprazole", "ppi"),
    ("esomeprazole", "ppi"), ("lansoprazole", "ppi"),
    # Antihistamines
    ("cetirizine", "antihistamine"), ("loratadine", "antihistamine"),
    ("fexofenadine", "antihistamine"), ("diphenhydramine", "antihistamine"),
    ("chlorpheniramine", "antihistamine"),
    # Triptans
    ("sumatriptan", "triptan"), ("rizatriptan", "triptan"),
    # Other high-interest medicines
    ("paracetamol", "other"), ("methotrexate", "other"),
    ("lithium", "other"), ("digoxin", "other"), ("theophylline", "other"),
    ("allopurinol", "other"), ("colchicine", "other"),
    ("sildenafil", "other"), ("tamsulosin", "other"),
    ("ondansetron", "other"), ("domperidone", "other"),
    ("levothyroxine", "other"), ("alendronate", "other"),
    ("baclofen", "other"), ("cyclobenzaprine", "other"),
    ("amiodarone", "other"), ("nitroglycerin", "other"),
    ("bupropion", "other"), ("mirtazapine", "other"),
]

CATEGORY_USE: dict[str, str] = {
    "anticoagulant": "Prevents blood clots",
    "antiplatelet": "Prevents platelets clumping",
    "nsaid": "Pain and inflammation relief",
    "antibiotic": "Treats bacterial infections",
    "antifungal": "Treats fungal infections",
    "ace_inhibitor": "Lowers blood pressure",
    "arb": "Lowers blood pressure",
    "beta_blocker": "Lowers blood pressure and heart rate",
    "calcium_channel_blocker": "Lowers blood pressure",
    "diuretic": "Removes excess fluid; lowers blood pressure",
    "potassium_sparing_diuretic": "Removes fluid while sparing potassium",
    "statin": "Lowers cholesterol",
    "antidiabetic": "Lowers blood sugar",
    "ssri": "Treats depression and anxiety",
    "snri": "Treats depression and anxiety",
    "tca": "Treats depression and nerve pain",
    "antiepileptic": "Prevents seizures",
    "antipsychotic": "Treats psychosis and mood disorders",
    "opioid": "Strong pain relief",
    "benzodiazepine": "Sedation and anxiety relief",
    "ppi": "Reduces stomach acid",
    "antihistamine": "Relieves allergy symptoms",
    "triptan": "Treats migraine attacks",
    "other": "Specialist / narrow-use medicine",
}

CATEGORY_RISK: dict[str, str] = {
    "anticoagulant": "Bleeding risk; many interactions",
    "antiplatelet": "Bleeding risk in combinations",
    "nsaid": "Bleeding, kidney and stomach risk",
    "antibiotic": "Enzyme inhibition can raise other drug levels",
    "antifungal": "Strong enzyme inhibition",
    "ace_inhibitor": "Potassium and kidney monitoring",
    "arb": "Potassium and kidney monitoring",
    "beta_blocker": "Heart-rate and masking effects",
    "calcium_channel_blocker": "Enzyme and heart-rate interactions",
    "diuretic": "Electrolyte shifts",
    "potassium_sparing_diuretic": "Hyperkalemia risk",
    "statin": "Muscle toxicity when levels rise",
    "antidiabetic": "Hypoglycemia risk in combinations",
    "ssri": "Bleeding and serotonin-syndrome risk",
    "snri": "Serotonin-syndrome and blood-pressure risk",
    "tca": "Heart-rhythm and sedation risk",
    "antiepileptic": "Enzyme induction / inhibition",
    "antipsychotic": "QT prolongation and sedation",
    "opioid": "Respiratory depression in combinations",
    "benzodiazepine": "Sedation and respiratory depression",
    "ppi": "Absorption and activation interactions",
    "antihistamine": "Sedation (older agents)",
    "triptan": "Serotonin-syndrome risk in combinations",
    "other": "Narrow therapeutic window or specialist monitoring",
}

# Medicines with a known QT-prolongation flag (used by one category rule).
QT_MEDICINES = {
    "haloperidol", "citalopram", "escitalopram", "clarithromycin",
    "erythromycin", "moxifloxacin", "ondansetron", "methadone",
    "domperidone", "amiodarone", "sotalol",
}

# ---------------------------------------------------------------------------
# Curated pairs: (drug_a, drug_b, severity, mechanism, evidence_note)
# Severity in {major, moderate, minor}. Pairs are undirected.
# ---------------------------------------------------------------------------
CURATED: list[tuple[str, str, str, str, str]] = [
    ("warfarin", "ibuprofen", "major", "Increased bleeding risk",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "naproxen", "major", "Increased bleeding risk",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "aspirin", "major", "Increased bleeding risk",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "clopidogrel", "major", "Increased bleeding risk",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "metronidazole", "major", "Increased anticoagulant effect",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "trimethoprim-sulfamethoxazole", "major",
     "Increased anticoagulant effect", "Well-known textbook pair; illustrative only"),
    ("warfarin", "fluconazole", "major", "Increased anticoagulant effect",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "amiodarone", "major", "Increased anticoagulant effect",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "paracetamol", "moderate",
     "Increased anticoagulant effect with regular use",
     "Well-known textbook pair; illustrative only"),
    ("warfarin", "carbamazepine", "moderate", "Reduced anticoagulant effect",
     "Enzyme-induction pattern; illustrative only"),
    ("methotrexate", "ibuprofen", "major", "Reduced methotrexate clearance",
     "Well-known textbook pair; illustrative only"),
    ("methotrexate", "naproxen", "major", "Reduced methotrexate clearance",
     "Well-known textbook pair; illustrative only"),
    ("methotrexate", "trimethoprim-sulfamethoxazole", "major",
     "Additive antifolate toxicity", "Well-known textbook pair; illustrative only"),
    ("lithium", "ibuprofen", "major", "Increased lithium levels",
     "Well-known textbook pair; illustrative only"),
    ("lithium", "furosemide", "major", "Increased lithium levels",
     "Well-known textbook pair; illustrative only"),
    ("lithium", "hydrochlorothiazide", "major", "Increased lithium levels",
     "Well-known textbook pair; illustrative only"),
    ("lithium", "lisinopril", "moderate", "Increased lithium levels",
     "Well-known textbook pair; illustrative only"),
    ("digoxin", "verapamil", "major", "Increased digoxin levels",
     "Well-known textbook pair; illustrative only"),
    ("digoxin", "diltiazem", "major", "Increased digoxin levels",
     "Well-known textbook pair; illustrative only"),
    ("digoxin", "amiodarone", "major", "Increased digoxin levels",
     "Well-known textbook pair; illustrative only"),
    ("digoxin", "furosemide", "moderate",
     "Electrolyte shifts raise digoxin toxicity risk",
     "Well-known textbook pair; illustrative only"),
    ("tramadol", "sertraline", "major", "Serotonin syndrome and seizure risk",
     "Well-known textbook pair; illustrative only"),
    ("tramadol", "fluoxetine", "major", "Serotonin syndrome and seizure risk",
     "Well-known textbook pair; illustrative only"),
    ("tramadol", "amitriptyline", "major", "Seizure and serotonin risk",
     "Well-known textbook pair; illustrative only"),
    ("morphine", "diazepam", "major", "Respiratory depression and sedation",
     "Well-known textbook pair; illustrative only"),
    ("oxycodone", "alprazolam", "major", "Respiratory depression and sedation",
     "Well-known textbook pair; illustrative only"),
    ("fentanyl", "lorazepam", "major", "Respiratory depression and sedation",
     "Well-known textbook pair; illustrative only"),
    ("clopidogrel", "omeprazole", "moderate",
     "Reduced clopidogrel activation", "Well-known textbook pair; illustrative only"),
    ("simvastatin", "clarithromycin", "major",
     "Increased statin levels; muscle toxicity risk",
     "Well-known textbook pair; illustrative only"),
    ("simvastatin", "erythromycin", "major",
     "Increased statin levels; muscle toxicity risk",
     "Well-known textbook pair; illustrative only"),
    ("atorvastatin", "clarithromycin", "major",
     "Increased statin levels; muscle toxicity risk",
     "Well-known textbook pair; illustrative only"),
    ("atorvastatin", "itraconazole", "major",
     "Increased statin levels; muscle toxicity risk",
     "Well-known textbook pair; illustrative only"),
    ("colchicine", "clarithromycin", "major",
     "Increased colchicine toxicity", "Well-known textbook pair; illustrative only"),
    ("sildenafil", "nitroglycerin", "major",
     "Severe hypotension risk", "Well-known textbook pair; illustrative only"),
    ("theophylline", "ciprofloxacin", "moderate",
     "Increased theophylline levels", "Well-known textbook pair; illustrative only"),
    ("levothyroxine", "omeprazole", "moderate",
     "Reduced levothyroxine absorption", "Well-known textbook pair; illustrative only"),
    ("levothyroxine", "pantoprazole", "minor",
     "Possible small absorption change", "Illustrative only"),
    ("levothyroxine", "lansoprazole", "minor",
     "Possible small absorption change", "Illustrative only"),
    ("levothyroxine", "esomeprazole", "minor",
     "Possible small absorption change", "Illustrative only"),
    ("alendronate", "ibuprofen", "moderate", "Increased stomach irritation",
     "Well-known textbook pair; illustrative only"),
    ("glipizide", "fluconazole", "moderate", "Hypoglycemia risk",
     "Well-known textbook pair; illustrative only"),
    ("glimepiride", "fluconazole", "moderate", "Hypoglycemia risk",
     "Well-known textbook pair; illustrative only"),
    ("valproic acid", "lamotrigine", "major",
     "Raised lamotrigine levels; rash risk",
     "Well-known textbook pair; illustrative only"),
    ("carbamazepine", "lamotrigine", "moderate",
     "Reduced lamotrigine levels", "Enzyme-induction pattern; illustrative only"),
    ("carbamazepine", "simvastatin", "moderate",
     "Reduced statin levels", "Enzyme-induction pattern; illustrative only"),
    ("phenytoin", "warfarin", "moderate", "Unpredictable anticoagulant effect",
     "Enzyme-induction pattern; illustrative only"),
    ("clozapine", "carbamazepine", "major",
     "Reduced clozapine levels; seizure risk",
     "Well-known textbook pair; illustrative only"),
    ("methadone", "fluconazole", "major",
     "QT prolongation and raised methadone levels",
     "Well-known textbook pair; illustrative only"),
    ("methadone", "clarithromycin", "major",
     "QT prolongation and raised methadone levels",
     "Well-known textbook pair; illustrative only"),
    ("simvastatin", "amlodipine", "moderate",
     "Raised simvastatin exposure", "Well-known textbook pair; illustrative only"),
    ("tamsulosin", "sildenafil", "moderate", "Hypotension risk",
     "Well-known textbook pair; illustrative only"),
    ("paracetamol", "ibuprofen", "minor",
     "Combined use is common; illustrative caution for liver/kidney load",
     "Illustrative only"),
    ("amlodipine", "atorvastatin", "minor",
     "Small rise in statin exposure", "Illustrative only"),
    ("amlodipine", "rosuvastatin", "minor",
     "Small rise in statin exposure", "Illustrative only"),
    ("felodipine", "atorvastatin", "minor",
     "Small rise in statin exposure", "Illustrative only"),
    ("metoprolol", "verapamil", "major", "Bradycardia and heart-block risk",
     "Well-known textbook pair; illustrative only"),
    ("atenolol", "diltiazem", "major", "Bradycardia and heart-block risk",
     "Well-known textbook pair; illustrative only"),
    ("bisoprolol", "verapamil", "major", "Bradycardia and heart-block risk",
     "Well-known textbook pair; illustrative only"),
    ("sertraline", "sumatriptan", "moderate", "Serotonin syndrome risk",
     "Well-known textbook pair; illustrative only"),
    ("fluoxetine", "rizatriptan", "moderate", "Serotonin syndrome risk",
     "Well-known textbook pair; illustrative only"),
    ("citalopram", "clarithromycin", "major", "QT prolongation risk",
     "Well-known textbook pair; illustrative only"),
    ("haloperidol", "erythromycin", "major", "QT prolongation risk",
     "Well-known textbook pair; illustrative only"),
    ("ondansetron", "haloperidol", "major", "QT prolongation risk",
     "Well-known textbook pair; illustrative only"),
    ("spironolactone", "lisinopril", "moderate", "Hyperkalemia risk",
     "Well-known textbook pair; illustrative only"),
    ("amiloride", "losartan", "moderate", "Hyperkalemia risk",
     "Well-known textbook pair; illustrative only"),
    ("spironolactone", "valsartan", "moderate", "Hyperkalemia risk",
     "Well-known textbook pair; illustrative only"),
    # Sedating antihistamines + CNS depressants (additive sedation).
    ("diphenhydramine", "morphine", "moderate", "Additive sedation",
     "Illustrative only"),
    ("diphenhydramine", "diazepam", "moderate", "Additive sedation",
     "Illustrative only"),
    ("chlorpheniramine", "oxycodone", "moderate", "Additive sedation",
     "Illustrative only"),
    ("chlorpheniramine", "lorazepam", "moderate", "Additive sedation",
     "Illustrative only"),
    # Remaining isolates: plausible textbook-style pairs.
    ("venlafaxine", "sumatriptan", "moderate", "Serotonin syndrome risk",
     "Well-known textbook pair; illustrative only"),
    ("bupropion", "tramadol", "moderate", "Seizure-threshold lowering",
     "Illustrative only"),
    ("mirtazapine", "tramadol", "moderate", "Serotonin syndrome risk",
     "Illustrative only"),
    ("baclofen", "diazepam", "moderate", "Additive sedation",
     "Illustrative only"),
    ("baclofen", "morphine", "moderate", "Additive sedation",
     "Illustrative only"),
    ("cyclobenzaprine", "tramadol", "moderate",
     "Serotonin syndrome and seizure risk", "Illustrative only"),
    ("allopurinol", "ampicillin", "moderate", "Rash risk",
     "Well-known textbook pair; illustrative only"),
    ("allopurinol", "amoxicillin", "moderate", "Rash risk",
     "Well-known textbook pair; illustrative only"),
]

# Category-level rules: (category_a, category_b, severity, mechanism).
# Sampled deterministically after the curated pairs, skipping duplicates.
RULES: list[tuple[str, str, str, str]] = [
    ("anticoagulant", "nsaid", "major", "Increased bleeding risk"),
    ("anticoagulant", "antiplatelet", "major", "Increased bleeding risk"),
    ("anticoagulant", "ssri", "moderate", "Increased bleeding risk"),
    ("nsaid", "ssri", "moderate", "Increased bleeding risk"),
    ("nsaid", "ace_inhibitor", "moderate",
     "Reduced blood-pressure control and kidney strain"),
    ("nsaid", "diuretic", "moderate",
     "Reduced diuretic effect and kidney strain"),
    ("nsaid", "arb", "moderate",
     "Reduced blood-pressure control and kidney strain"),
    ("ace_inhibitor", "potassium_sparing_diuretic", "moderate",
     "Hyperkalemia risk"),
    ("arb", "potassium_sparing_diuretic", "moderate", "Hyperkalemia risk"),
    ("opioid", "benzodiazepine", "major",
     "Respiratory depression and sedation"),
    ("ssri", "triptan", "moderate", "Serotonin syndrome risk"),
    ("ssri", "tca", "moderate", "Serotonin syndrome risk"),
    ("snri", "triptan", "moderate", "Serotonin syndrome risk"),
    ("antibiotic", "nsaid", "moderate",
     "Seizure-threshold lowering (fluoroquinolone pattern)"),
    ("antipsychotic", "benzodiazepine", "moderate",
     "Additive sedation and hypotension"),
    ("antiepileptic", "benzodiazepine", "moderate", "Additive sedation"),
    ("beta_blocker", "calcium_channel_blocker", "moderate",
     "Bradycardia and heart-block risk"),
    ("diuretic", "ace_inhibitor", "moderate",
     "First-dose hypotension and kidney monitoring"),
    ("diuretic", "arb", "moderate",
     "First-dose hypotension and kidney monitoring"),
    ("statin", "antifungal", "major",
     "Increased statin levels; muscle toxicity risk"),
    ("antidiabetic", "antifungal", "moderate", "Hypoglycemia risk"),
    ("ppi", "antiepileptic", "moderate",
     "Changed absorption / enzyme effects"),
]

TARGET_PAIRS = 500
SEED = 42


def _pair_key(a: str, b: str) -> tuple[str, str]:
    """Undirected pair key (alphabetical) so A-B and B-A dedupe."""
    return (a, b) if a <= b else (b, a)


def build_interactions() -> list[tuple[str, str, str, str, str]]:
    """Return the full interaction list (curated + rule-sampled)."""
    by_name = {name: cat for name, cat in MEDICINES}
    seen: set[tuple[str, str]] = set()
    rows: list[tuple[str, str, str, str, str]] = []

    def add(a: str, b: str, severity: str, mechanism: str, note: str) -> bool:
        if a == b or a not in by_name or b not in by_name:
            return False
        key = _pair_key(a, b)
        if key in seen:
            return False
        seen.add(key)
        rows.append((key[0], key[1], severity, mechanism, note))
        return True

    for a, b, sev, mech, note in CURATED:
        add(a, b, sev, mech, note)

    # QT-prolonger x QT-prolonger rule (subset, not a category).
    qt = sorted(m for m in QT_MEDICINES if m in by_name)
    qt_pairs = [(qt[i], qt[j]) for i in range(len(qt)) for j in range(i + 1, len(qt))]
    rng = random.Random(SEED)
    rng.shuffle(qt_pairs)
    for a, b in qt_pairs:
        if len(rows) >= TARGET_PAIRS:
            break
        add(a, b, "major", "QT prolongation risk",
            "Rule-based illustrative pair (QT-prolonger pattern)")

    # Category rules, shuffled deterministically, sampled to the target.
    rule_pairs: list[tuple[str, str, str, str]] = []
    for cat_a, cat_b, sev, mech in RULES:
        group_a = [n for n, c in MEDICINES if c == cat_a]
        group_b = [n for n, c in MEDICINES if c == cat_b]
        for a in group_a:
            for b in group_b:
                if a != b:
                    rule_pairs.append((a, b, sev, mech))
    rng.shuffle(rule_pairs)
    for a, b, sev, mech in rule_pairs:
        if len(rows) >= TARGET_PAIRS:
            break
        add(a, b, sev, mech, "Rule-based illustrative pair (category pattern)")

    return rows


def main() -> None:
    """Write data/medicines.csv and data/interactions.csv."""
    DATA.mkdir(parents=True, exist_ok=True)
    assert 150 <= len(MEDICINES) <= 200, f"medicine count {len(MEDICINES)}"
    assert len({n for n, _ in MEDICINES}) == len(MEDICINES), "duplicate medicine"

    with open(DATA / "medicines.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["medicine_id", "generic_name", "category",
                         "typical_use", "risk_note"])
        for i, (name, cat) in enumerate(MEDICINES, start=1):
            writer.writerow([f"M{i:03d}", name, cat,
                             CATEGORY_USE[cat], CATEGORY_RISK[cat]])

    interactions = build_interactions()
    assert 400 <= len(interactions) <= 600, f"pair count {len(interactions)}"
    with open(DATA / "interactions.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["drug_a", "drug_b", "severity", "mechanism",
                         "evidence_note"])
        writer.writerows(interactions)

    print(f"medicines: {len(MEDICINES)}")
    print(f"interactions: {len(interactions)}")


if __name__ == "__main__":
    main()
