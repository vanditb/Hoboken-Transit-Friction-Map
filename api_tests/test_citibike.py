import requests
import pandas as pd


STATION_INFO_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"

HOBOKEN_LAT_MIN = 40.730
HOBOKEN_LAT_MAX = 40.760
HOBOKEN_LON_MIN = -74.050
HOBOKEN_LON_MAX = -74.010


def fetch_json(url):
    """Fetch JSON from a URL and raise a clear error if the request fails."""
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def clamp_score(value):
    return max(0, min(100, value))


def calculate_bike_friction(row):
    if row.get("is_renting") == 0 or row.get("is_returning") == 0:
        return 100

    capacity = row.get("capacity")
    bikes_available = row.get("num_bikes_available")

    if pd.isna(capacity) or capacity <= 0 or pd.isna(bikes_available):
        return None

    score = 100 * (1 - bikes_available / capacity)
    return round(clamp_score(score), 1)


def main():
    try:
        station_info = fetch_json(STATION_INFO_URL)
        station_status = fetch_json(STATION_STATUS_URL)
    except requests.RequestException as error:
        print(f"Could not fetch Citi Bike data: {error}")
        return

    info_df = pd.DataFrame(station_info["data"]["stations"])
    status_df = pd.DataFrame(station_status["data"]["stations"])

    merged = info_df.merge(status_df, on="station_id", how="inner")

    hoboken_stations = merged[
        (merged["lat"].between(HOBOKEN_LAT_MIN, HOBOKEN_LAT_MAX))
        & (merged["lon"].between(HOBOKEN_LON_MIN, HOBOKEN_LON_MAX))
    ].copy()

    hoboken_stations["friction"] = hoboken_stations.apply(calculate_bike_friction, axis=1)

    columns = [
        "name",
        "lat",
        "lon",
        "num_bikes_available",
        "num_docks_available",
        "capacity",
        "friction",
    ]

    print(f"Found {len(hoboken_stations)} Citi Bike stations near Hoboken.")
    print(hoboken_stations[columns].sort_values("friction", ascending=False).head(15).to_string(index=False))


if __name__ == "__main__":
    main()
