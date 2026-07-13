from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "construction_impacts.csv"
REQUIRED_COLUMNS = [
    "project_name",
    "responsible_party",
    "location",
    "impact_type",
    "street",
    "from_street",
    "to_street",
    "start_date",
    "end_date",
    "start_time",
    "end_time",
    "traffic_management",
    "mode_affected",
    "friction_level",
    "geometry_type",
    "lat",
    "lon",
    "start_lat",
    "start_lon",
    "end_lat",
    "end_lon",
    "source_url",
    "notes",
]


def main():
    if not DATA_PATH.exists():
        print(f"Construction impacts CSV was not found: {DATA_PATH}")
        return

    construction = pd.read_csv(DATA_PATH)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in construction.columns]

    print(f"Construction impacts CSV has {len(construction)} rows and {len(construction.columns)} columns.")
    if missing_columns:
        print(f"Missing expected columns: {', '.join(missing_columns)}")
    else:
        print("All expected columns are present.")

    point_rows = construction[construction["geometry_type"].str.lower() == "point"]
    line_rows = construction[construction["geometry_type"].str.lower() == "line"]

    missing_point_coords = point_rows[["lat", "lon"]].isna().any(axis=1).sum()
    missing_line_coords = line_rows[["start_lat", "start_lon", "end_lat", "end_lon"]].isna().any(axis=1).sum()

    if missing_point_coords:
        print(f"Warning: {missing_point_coords} point rows are missing lat/lon.")
    else:
        print("Point rows have lat/lon coordinates.")

    if missing_line_coords:
        print(f"Warning: {missing_line_coords} line rows are missing start/end coordinates.")
    else:
        print("Line rows have start/end coordinates.")

    geometry_counts = construction["geometry_type"].value_counts(dropna=False)
    print("\nGeometry types:")
    print(geometry_counts.to_string())

    print("\nSample rows:")
    print(
        construction[
            [
                "project_name",
                "geometry_type",
                "street",
                "impact_type",
                "friction_level",
            ]
        ]
        .head()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
