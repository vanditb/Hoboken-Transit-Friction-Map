"""Feature and label preparation shared by the first prediction notebook and its test."""

import pandas as pd


def prepare_prediction_frame(history):
    """Create time-ordered station features and one-hour shortage labels when intervals allow."""
    frame = history.copy()
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    frame = frame.dropna(subset=["timestamp_utc", "station_id"]).sort_values(["station_id", "timestamp_utc"])
    frame["hour_of_day"] = frame["timestamp_utc"].dt.hour
    frame["day_of_week"] = frame["timestamp_utc"].dt.dayofweek

    groups = []
    for _, station in frame.groupby("station_id", group_keys=False):
        station = station.sort_values("timestamp_utc").copy()
        station["previous_bikes"] = station["bikes_available"].shift(1)
        station["previous_docks"] = station["docks_available"].shift(1)
        station["bike_change_15m"] = station["bikes_available"] - station["previous_bikes"]
        station["dock_change_15m"] = station["docks_available"] - station["previous_docks"]
        station["bike_ratio_rolling_60m"] = station["bike_availability_ratio"].rolling(4, min_periods=1).mean()
        station["dock_ratio_rolling_60m"] = station["dock_availability_ratio"].rolling(4, min_periods=1).mean()

        for minutes, steps in [(15, 1), (30, 2), (60, 4)]:
            future_time = station["timestamp_utc"].shift(-steps)
            valid_interval = (future_time - station["timestamp_utc"]).dt.total_seconds().between(minutes * 60 - 8 * 60, minutes * 60 + 8 * 60)
            station[f"bikes_plus_{minutes}m"] = station["bikes_available"].shift(-steps).where(valid_interval)
            station[f"docks_plus_{minutes}m"] = station["docks_available"].shift(-steps).where(valid_interval)

        station["bike_shortage_60m"] = (station["bikes_plus_60m"] <= 2).where(station["bikes_plus_60m"].notna())
        station["dock_shortage_60m"] = (station["docks_plus_60m"] <= 2).where(station["docks_plus_60m"].notna())
        groups.append(station)

    return pd.concat(groups, ignore_index=True) if groups else frame
