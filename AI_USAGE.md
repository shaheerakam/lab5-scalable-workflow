# AI Usage

## Tool and model

Claude Sonnet 5.5 (Anthropic), used in a chat and coding session.

## What the AI did

- Claude walked me through step-by-step how to write the Snakefile and the four Python scripts in `scripts/` (cleaning, the SQL query, the combined summary, and the report/figure). I am relatively new to coding and used Claude to guide me through writing them from scratch.
- The SQL in `query_features.py` is the same query from my Lab 4, which I also built with Claude's help.
- Claude suggested the `combine_summaries` and the idea of flagging mmol/L values instead of converting them, which I originally did not think of.
- Claude walked me through setup one step at a time, debugging as we went along.

## What I did myself

- Wrote the code, via Claude's guidance 
- Created the repo, cloned it, and built the conda environment.
- Ran the workflow on my own computer: dry run, clean run, and a partial re-run after changing one value, saving the output in `evidence/`.
- Checked the results (see "How I verified" below).
- Wrote the interpretation in the README.

## Errors and fixes

1. `cd: no such file or directory: /Users/shaheerakamin/Documents/GitHub/lab5-workflow-kamin`. This means Terminal looked for a folder that does not exist. I had named my repo `lab5-scalable-workflow`, but I fixed it by using my real folder name.
2. My file listing showed only three of the four scripts. `query_features.py` was missing because the paste that creates it did not work the first time. Without it, Snakemake would have stopped with a missing-input error. I pasted it again and confirmed all five files with `ls -l`.
3. A mistake in the AI-written report: it said the other glucose values "were missing (N/A)", but my raw file has no N/A glucose values. This means the report would have stated something false about the data. It was fixed by counting missing values from the flag column. My `combined_summary.tsv` shows `n_glucose_missing` is 0.0.

## How I verified

- `messy_samples.csv` and `samples_clean.tsv` both have 61 lines (header + 60 samples), so no rows were lost.
- `combined_summary.tsv` shows 566 patients, one row per patient, and the script stops with an error if the row count differs from the number of patients in the database.
- I compared raw rows to cleaned rows by hand: `s-0003,11.24.53,MG/DL` became `S0003, 1953-11-24, mg/dL`, and `S0011,07.09.61,Male,SITE-A,165.0,mmol/L` became `1961-07-09, M, Site A`, with the glucose blank and flagged.
- I changed one glucose value, re-ran, and confirmed from `evidence/2_partial_rerun.txt` that `query_features` did not run, then restored the value.
