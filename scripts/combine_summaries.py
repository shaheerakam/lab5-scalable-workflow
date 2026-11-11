import sys

import pandas as pd

GENES = ["EGFR", "KEAP1", "KRAS", "STK11", "TP53"]

samples_path, features_path, out_path = sys.argv[1:]
samples = pd.read_csv(samples_path, sep="\t")
features = pd.read_csv(features_path, sep="\t")

rows = [
    ("samples", "n_records", len(samples)),
    ("samples", "n_missing_sex", samples["sex"].isna().sum()),
    ("samples", "n_glucose_usable", samples["glucose_mg_dl"].notna().sum()),
    ("samples", "n_glucose_unit_mismatch", (samples["glucose_flag"] == "implausible_for_unit").sum()),
    ("samples", "n_glucose_missing", (samples["glucose_flag"] == "missing").sum()),
    ("samples", "median_glucose_mg_dl", samples["glucose_mg_dl"].median()),
    ("patients", "n_records", len(features)),
    ("patients", "n_missing_sex", features["sex"].isna().sum()),
    ("patients", "n_missing_age", features["age_at_diagnosis"].isna().sum()),
    ("patients", "median_age_at_diagnosis", features["age_at_diagnosis"].median()),
    ("patients", "median_tmb", features["tmb_nonsynonymous"].median()),
]
rows += [("patients", f"n_with_{gene}_mutation", (features[gene] > 0).sum()) for gene in GENES]

combined = pd.DataFrame(rows, columns=["dataset", "metric", "value"])
combined["value"] = combined["value"].astype(float).round(2)
combined.to_csv(out_path, sep="\t", index=False)
