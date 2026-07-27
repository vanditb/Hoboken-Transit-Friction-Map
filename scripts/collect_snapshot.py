"""Collect Citi Bike and near-term weather observations for future prediction work."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
from zoneinfo import ZoneInfo

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from scoring import calculate_construction_friction, calculate_weather_friction


STATION_INFO_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"
NWS_POINTS_URL = "https://api.weather.gov/points/40.7433,-74.0324"
NWS_HEADERS = {"User-Agent": "Hoboken Transit Friction Map student prototype (contact: vanditb)"}
HISTORY_DIR = PROJECT_ROOT / "data" / "history"
CONSTRUCTION_PATH = PROJECT_ROOT / "data" / "construction_impacts.csv"
HOBOKEN_LAT_MIN, HOBOKEN_LAT_MAX = 40.730, 40.760
HOBOKEN_LON_MIN, HOBOKEN_LON_MAX = -74.050, -74.010
LOCAL_TIMEZONE = ZoneInfo("America/New_York")
REQUEST_TIMEOUT_SECONDS = 20


def fetch_json(url, headers=None):
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def fetch_stations():
    info = pd.DataFrame(fetch_json(STATION_INFO_URL)["data"]["stations"])
    status = pd.DataFrame(fetch_json(STATION_STATUS_URL)["data"]["stations"])
    stations = info.merge(status, on="station_id", how="inner")
    return stations[
        stations["lat"].between(HOBOKEN_LAT_MIN, HOBOKEN_LAT_MAX)
        & stations["lon"].between(HOBOKEN_LON_MIN, HOBOKEN_LON_MAX)
    ].copy()


def fetch_weather():
    point_data = fetch_json(NWS_POINTS_URL, headers=NWS_HEADERS)
    forecast_url = point_data["properties"]["forecast"]
    period = fetch_json(forecast_url, headers=NWS_HEADERS)["properties"]["periods"][0]
    return period, calculate_weather_friction(period)


def load_construction():
    if CONSTRUCTION_PATH.exists():
        return pd.read_csv(CONSTRUCTION_PATH)
    return pd.DataFrame()


def log_failure(message):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with (HISTORY_DIR / "collector_errors.log").open("a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} | {message}\n")


def snapshot_rows(stations, weather_period, weather_friction, construction, now_utc, now_local):
    active_verified = construction[
        (construction.get("active_status", pd.Series(dtype=str)) == "active")
        & (construction.get("verification_status", pd.Series(dtype=str)) == "verified")
    ] if not construction.empty else construction

    rows = []
    for _, station in stations.iterrows():
        construction_result = calculate_construction_friction(station, construction, "All")
        capacity = station.get("capacity")
        bikes = station.get("num_bikes_available")
        docks = station.get("num_docks_available")
        rows.append(
            {
                "timestamp_utc": now_utc.isoformat(),
                "timestamp_local": now_local.isoformat(),
                "station_id": station["station_id"],
                "station_name": station.get("name"),
                "lat": station.get("lat"),
                "lon": station.get("lon"),
                "bikes_available": bikes,
                "docks_available": docks,
                "capacity": capacity,
                "station_status": station.get("station_status"),
                "bike_availability_ratio": bikes / capacity if pd.notna(bikes) and pd.notna(capacity) and capacity > 0 else None,
                "dock_availability_ratio": docks / capacity if pd.notna(docks) and pd.notna(capacity) and capacity > 0 else None,
                "temperature": weather_period.get("temperature") if weather_period else None,
                "short_forecast": weather_period.get("shortForecast") if weather_period else None,
                "precipitation_related": bool(weather_period and any(word in str(weather_period.get("shortForecast", "")).lower() for word in ["rain", "shower", "snow", "storm"])),
                "wind": weather_period.get("windSpeed") if weather_period else None,
                "weather_friction": weather_friction,
                "active_verified_construction_projects": len(active_verified),
                "nearest_relevant_construction_distance_m": construction_result["nearest_distance_m"],
            }
        )
    return pd.DataFrame(rows)


def collect_once():
    """Fetch a consistent snapshot, then append it to one local daily file."""
    now_utc = datetime.now(timezone.utc).replace(microsecond=0)
    now_local = now_utc.astimezone(LOCAL_TIMEZONE)
    try:
        stations = fetch_stations()
        try:
            weather_period, weather_friction = fetch_weather()
        except (requests.RequestException, KeyError, IndexError, ValueError) as error:
            log_failure(f"Weather unavailable; snapshot saved without weather: {error}")
            weather_period, weather_friction = None, None
        construction = load_construction()
        snapshot = snapshot_rows(stations, weather_period, weather_friction, construction, now_utc, now_local)
    except (requests.RequestException, KeyError, ValueError) as error:
        log_failure(f"Citi Bike snapshot failed: {error}")
        print(f"Snapshot was not saved because Citi Bike data failed: {error}")
        return False

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = HISTORY_DIR / f"{now_local.date().isoformat()}.csv"
    if path.exists():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, snapshot], ignore_index=True)
        combined = combined.drop_duplicates(subset=["timestamp_utc", "station_id"], keep="first")
    else:
        combined = snapshot
    combined.to_csv(path, index=False)
    print(f"Saved {len(snapshot)} station rows to {path}.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Collect Citi Bike history for the Hoboken prototype.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="Collect one snapshot and exit.")
    mode.add_argument("--loop", action="store_true", help="Keep collecting until Ctrl+C.")
    parser.add_argument("--interval-minutes", type=int, default=15, help="Minutes between loop snapshots.")
    args = parser.parse_args()

    if args.once:
        collect_once()
        return
    if args.interval_minutes <= 0:
        parser.error("--interval-minutes must be greater than zero")

    print(f"Collecting every {args.interval_minutes} minutes. Press Ctrl+C to stop.")
    try:
        while True:
            collect_once()
            time.sleep(args.interval_minutes * 60)
    except KeyboardInterrupt:
        print("Collector stopped cleanly.")


if __name__ == "__main__":
    main()
