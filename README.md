# Lab 5: Scalable Analysis Workflow

A Snakemake workflow that cleans a messy sample table (Lab 3 data), builds patient-level features from the LUAD cohort database (Lab 4 data), summarizes both, and writes a short report with a figure.

## Setup

    conda env create -f environment.yml
    conda activate lab5-workflow

The raw inputs are in `data/raw/`: `messy_samples.csv` and `cohort.db`, both copied from the class repository.

## How to run

Clean run, from scratch (this first deletes everything in `results/`):

    snakemake --cores 1 --delete-all-output
    snakemake --cores 1

Partial re-run: change one value in `data/raw/messy_samples.csv` (for example S0001's glucose from 145.9 to 150.0), then run:

    snakemake --cores 1

Only the steps that depend on the changed file run again. `query_features` is skipped because the database did not change.

Dry run (shows what would run, changes nothing):

    snakemake --cores 1 -n

## Workflow stages

| Rule | Reads | Writes |
|---|---|---|
| `clean_samples` | `data/raw/messy_samples.csv` | `results/samples_clean.tsv` |
| `query_features` | `data/raw/cohort.db` | `results/patient_features.tsv` |
| `combine_summaries` | the two tables above | `results/combined_summary.tsv` |
| `make_report` | the three tables above | `results/summary_report.md`, `results/summary_figure.png` |

Each script is listed as an input of its rule, so editing a script also triggers a re-run. The diagram is in `evidence/dag.png`.

## About the merge stage

The class README crossed out the stage that merges the two datasets, because the sample table and the patient database share no key, so there is no honest way to join them record by record. `combine_summaries` does not join patients. It stacks summary numbers from each dataset (counts, medians, missing values) into one table, so the workflow still has a stage that brings both datasets together. It can be removed without affecting the other rules.

## Cleaning decisions

- Sample IDs such as `s-0003` become `S0003`.
- Dates arrive in four formats and are written as YYYY-MM-DD. In the `MM.DD.YY` format, a row like `11.24.53` shows the month comes first, since 24 cannot be a month. Two-digit years 50-99 are read as 19xx and 00-49 as 20xx, because the dates in this file start in 1950.
- Sex is M or F; anything else (U, unknown, blank) becomes NA.
- Site names are standardized to Site A, B, or C.
- Glucose values labeled mmol/L are all between 70 and 250, which cannot be real mmol/L glucose. They are flagged `implausible_for_unit` and left blank in `glucose_mg_dl` instead of being converted.
- `patient_name` is dropped because the analysis does not need it.

## Results

See `results/summary_report.md` and `results/summary_figure.png`. Evidence of the runs is in `evidence/`: `1_clean_run.txt`, `2_partial_rerun.txt`, and `dag.png`.

## My interpretation

The glucose sample file had some messy data because 13 readings were labeled as mmol/L but had values that did not correlate to that unit. Instead of guessing by converting them, I left those blank so that I don't introduce incorrect, falsified values. One thing that stood out to me was that TP53 was much more common than the other mutations, appearing in about 51% of patients, which correlates to real-life data (that I've learnt about in some of my biology courses). However, I would want to look at more information about the patients before making any final conclusions about why it was so common. One other major limitation is that some patient information was missing, such as age and sex. This could affect how complete the results are and how accurate everything is overal. Another limitation is that there were only about 15 glucose readings per, so the differences between sites might not be reliable. Using Snakemake was helpful because when I changed one value, I could see that it skipped `query_features` because that step did not need to run again, which saved me a lot time.
