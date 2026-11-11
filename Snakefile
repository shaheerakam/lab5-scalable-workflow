rule all:
    input:
        "results/summary_report.md",
        "results/summary_figure.png",


rule clean_samples:
    input:
        script="scripts/clean_samples.py",
        raw="data/raw/messy_samples.csv",
    output:
        "results/samples_clean.tsv",
    shell:
        "python {input.script} {input.raw} {output}"


rule query_features:
    input:
        script="scripts/query_features.py",
        db="data/raw/cohort.db",
    output:
        "results/patient_features.tsv",
    shell:
        "python {input.script} {input.db} {output}"


rule combine_summaries:
    input:
        script="scripts/combine_summaries.py",
        samples="results/samples_clean.tsv",
        features="results/patient_features.tsv",
    output:
        "results/combined_summary.tsv",
    shell:
        "python {input.script} {input.samples} {input.features} {output}"


rule make_report:
    input:
        script="scripts/make_report.py",
        samples="results/samples_clean.tsv",
        features="results/patient_features.tsv",
        combined="results/combined_summary.tsv",
    output:
        report="results/summary_report.md",
        figure="results/summary_figure.png",
    shell:
        "python {input.script} {input.samples} {input.features} {input.combined} {output.report} {output.figure}"
