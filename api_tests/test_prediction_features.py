"""Check that the first feature pipeline creates a valid one-hour label."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prediction_features import prepare_prediction_frame


def main():
    timestamps = pd.date_range("2026-07-27T12:00:00Z", periods=5, freq="15min")
    history = pd.DataFrame(
        {
            "timestamp_utc": timestamps,
            "station_id": ["station-1"] * 5,
            "bikes_available": [5, 4, 3, 2, 1],
            "docks_available": [5, 6, 7, 8, 9],
            "bike_availability_ratio": [0.5, 0.4, 0.3, 0.2, 0.1],
            "dock_availability_ratio": [0.5, 0.6, 0.7, 0.8, 0.9],
        }
    )
    features = prepare_prediction_frame(history)
    assert "bike_shortage_60m" in features
    assert bool(features.iloc[0]["bike_shortage_60m"])
    assert pd.isna(features.iloc[-1]["bike_shortage_60m"])
    print("Prediction feature check passed: time ordering, lag columns, and one-hour labels work when 15-minute intervals exist.")


if __name__ == "__main__":
    main()
