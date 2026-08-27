import csv
import os

import pandas as pd  # handles both .xls and .xlsx cleanly


def parse_uploaded_file(file):
    name = file.name.lower()
    ext = os.path.splitext(name)[1]

    if ext == ".csv":
        decoded = file.read().decode("utf-8").splitlines()
        return list(csv.DictReader(decoded))

    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file)
        return df.to_dict(orient="records")

    else:
        raise ValueError("Unsupported file type")
