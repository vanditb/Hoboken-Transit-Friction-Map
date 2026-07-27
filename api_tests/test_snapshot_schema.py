"""Check the historical snapshot columns without collecting live data."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect_snapshot import snapshot_rows


def main():
    stations = pd.DataFrame([{"station_id": "1", "name": "Example", "lat": 40.7433, "lon": -74.0324, "num_bikes_available": 3, "num_docks_available": 7, "capacity": 10, "station_status": "active"}])
    construction = pd.DataFrame(columns=["active_status", "verification_status"])
    result = snapshot_rows(stations, {"temperature": 70, "shortForecast": "Sunny", "windSpeed": "5 mph"}, 10, construction, pd.Timestamp("2026-07-27T12:00:00Z").to_pydatetime(), pd.Timestamp("2026-07-27T08:00:00-04:00").to_pydatetime())
    required = {"timestamp_utc", "station_id", "bike_availability_ratio", "weather_friction", "nearest_relevant_construction_distance_m"}
    assert required.issubset(result.columns)
    assert len(result) == 1
    assert result.iloc[0]["bike_availability_ratio"] == 0.3
    print("Historical snapshot schema check passed.")


if __name__ == "__main__":
    main()
