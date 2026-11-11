import re
import sys
from datetime import date

import numpy as np
import pandas as pd

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
SEX_CODES = {"m": "M", "male": "M", "f": "F", "female": "F"}
MG_DL_PER_MMOL_L = 18.016
PLAUSIBLE_MG_DL = (20, 600)


def parse_dob(text):
    text = text.strip()
    if m := re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", text):
        month, day, year = map(int, m.groups())
    elif m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text):
        year, month, day = map(int, m.groups())
    elif m := re.fullmatch(r"(\d{2})-([A-Za-z]{3})-(\d{4})", text):
        day, year = int(m[1]), int(m[3])
        month = MONTHS.index(m[2].lower()) + 1
    elif m := re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", text):
        month, day, yy = map(int, m.groups())
        # births in this file start in 1950, so a two-digit year of 50-99 is 19xx
        year = 1900 + yy if yy >= 50 else 2000 + yy
    else:
        return None
    return date(year, month, day).isoformat()


raw_path, out_path = sys.argv[1:]
raw = pd.read_csv(raw_path, dtype=str, keep_default_na=False)

value = pd.to_numeric(raw["glucose_value"].str.rstrip("*"), errors="coerce")
unit = raw["glucose_unit"].str.strip().str.lower().map({"mg/dl": "mg/dL", "mmol/l": "mmol/L"})
mg_dl = value * unit.map({"mg/dL": 1.0, "mmol/L": MG_DL_PER_MMOL_L})
plausible = mg_dl.between(*PLAUSIBLE_MG_DL)

# values labeled mmol/L are 70-250, far above real mmol/L glucose, so converting
# them gives thousands of mg/dL; they are flagged and left blank instead
flag = np.select(
    [value.isna(), ~plausible, raw["glucose_value"].str.endswith("*")],
    ["missing", "implausible_for_unit", "trailing_asterisk"],
    default="ok",
)

clean = pd.DataFrame({
    "sample_id": "S" + raw["sample_id"].str.extract(r"^[sS]-?(\d+)$")[0],
    "dob": raw["dob"].map(parse_dob),
    "sex": raw["sex"].str.strip().str.lower().map(SEX_CODES),
    "site": "Site " + raw["enrollment_site"].str.extract(r"(?i)site[\s_-]*([abc])")[0].str.upper(),
    "glucose_value": value,
    "glucose_unit": unit,
    "glucose_mg_dl": mg_dl.where(plausible),
    "glucose_flag": flag,
    "notes": raw["notes"].replace("", pd.NA),
})
clean.to_csv(out_path, sep="\t", index=False, na_rep="NA")
