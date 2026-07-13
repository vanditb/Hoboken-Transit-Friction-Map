from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "construction_layer.csv"
REQUIRED_COLUMNS = [
    "project_name",
    "street",
    "from_street",
    "to_street",
    "start_date",
    "end_date",
    "start_time",
    "end_time",
    "impact_type",
    "description",
    "friction_level",
    "lat",
    "lon",
    "source_url",
    "notes",
]


def main():
    if not DATA_PATH.exists():
        print(f"Construction CSV was not found: {DATA_PATH}")
        return

    construction = pd.read_csv(DATA_PATH)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in construction.columns]

    print(f"Construction CSV has {len(construction)} rows and {len(construction.columns)} columns.")
    if missing_columns:
        print(f"Missing expected columns: {', '.join(missing_columns)}")
    else:
        print("All expected columns are present.")

    missing_coordinates = construction[["lat", "lon"]].isna().any(axis=1).sum()
    if missing_coordinates:
        print(f"Warning: {missing_coordinates} rows are missing latitude or longitude.")
