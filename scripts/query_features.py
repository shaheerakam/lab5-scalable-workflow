import sqlite3
import sys

import pandas as pd

GENE_COUNTS_SQL = """
WITH target_genes(gene_symbol) AS (
  VALUES ('TP53'), ('KRAS'), ('EGFR'), ('STK11'), ('KEAP1')
),
patient_gene AS (
  SELECT p.patient_id, g.gene_symbol
  FROM patients p
  CROSS JOIN target_genes g
)
SELECT pg.patient_id, pg.gene_symbol, COUNT(m.mutation_id) AS mutation_count
FROM patient_gene pg
LEFT JOIN samples s ON s.patient_id = pg.patient_id
LEFT JOIN mutations m
  ON m.sample_id = s.sample_id
  AND m.gene_symbol = pg.gene_symbol
  AND m.variant_classification != 'Silent'
GROUP BY pg.patient_id, pg.gene_symbol
ORDER BY pg.patient_id, pg.gene_symbol
"""

PATIENTS_SQL = """
SELECT p.patient_id, p.sex, p.age_at_diagnosis, p.stage,
       s.tissue_source_site, s.tmb_nonsynonymous
FROM patients p
LEFT JOIN samples s ON s.patient_id = p.patient_id
ORDER BY p.patient_id
"""

db_path, out_path = sys.argv[1:]
con = sqlite3.connect(db_path)
gene_counts = pd.read_sql_query(GENE_COUNTS_SQL, con)
patients = pd.read_sql_query(PATIENTS_SQL, con)
n_patients = con.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
con.close()

gene_wide = (
    gene_counts.pivot(index="patient_id", columns="gene_symbol", values="mutation_count")
    .rename_axis(columns=None)
    .reset_index()
)
features = patients.merge(gene_wide, on="patient_id", how="left")
features["age_at_diagnosis"] = features["age_at_diagnosis"].astype("Int64")

assert len(features) == n_patients, f"{len(features)} rows for {n_patients} patients"
features.to_csv(out_path, sep="\t", index=False, na_rep="NA")
