import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

GENES = ["EGFR", "KEAP1", "KRAS", "STK11", "TP53"]

samples_path, features_path, combined_path, report_path, figure_path = sys.argv[1:]
samples = pd.read_csv(samples_path, sep="\t")
features = pd.read_csv(features_path, sep="\t")
combined = pd.read_csv(combined_path, sep="\t")
stat = {(r.dataset, r.metric): r.value for r in combined.itertuples()}

fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.5))

usable = samples.dropna(subset=["glucose_mg_dl"])
sites = sorted(usable["site"].unique())
left.boxplot([usable.loc[usable["site"] == s, "glucose_mg_dl"] for s in sites])
left.set_xticks(range(1, len(sites) + 1), sites)
left.set_xlabel("Enrollment site")
left.set_ylabel("Glucose (mg/dL)")
left.set_title("Usable glucose readings by site")

percent_mutated = [100 * stat[("patients", f"n_with_{g}_mutation")] / stat[("patients", "n_records")] for g in GENES]
right.bar(GENES, percent_mutated)
right.set_xlabel("Gene")
right.set_ylabel("Patients with a protein-altering mutation (%)")
right.set_title("Mutation frequency in the LUAD cohort")

fig.tight_layout()
fig.savefig(figure_path, dpi=150)

report = f"""# Summary report

Numbers below are read from `combined_summary.tsv`, which the pipeline builds from the cleaned samples table and the patient feature table.

## Samples (messy_samples.csv)

- {stat[("samples", "n_records")]:.0f} records cleaned; {stat[("samples", "n_missing_sex")]:.0f} have no usable sex value.
- {stat[("samples", "n_glucose_usable")]:.0f} glucose readings are usable. {stat[("samples", "n_glucose_unit_mismatch")]:.0f} were labeled mmol/L but hold values of 70-250, which cannot be real mmol/L glucose, so they were left blank instead of converted. {stat[("samples", "n_glucose_missing")]:.0f} had no value ("N/A").
- Median usable glucose: {stat[("samples", "median_glucose_mg_dl")]:.1f} mg/dL.

## Patients (cohort.db)

- {stat[("patients", "n_records")]:.0f} patients, one row each. {stat[("patients", "n_missing_sex")]:.0f} are missing sex and {stat[("patients", "n_missing_age")]:.0f} are missing age at diagnosis.
- Median age at diagnosis: {stat[("patients", "median_age_at_diagnosis")]:.0f} years. Median tumor mutation burden: {stat[("patients", "median_tmb")]:.1f}.
- Share of patients with at least one protein-altering mutation: {", ".join(f"{g} {p:.0f}%" for g, p in zip(GENES, percent_mutated))}.

![Summary figure]({figure_path.rsplit("/", 1)[-1]})
"""
with open(report_path, "w") as f:
    f.write(report)
