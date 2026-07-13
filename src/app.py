import re
from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium


STATION_INFO_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"
NWS_POINTS_URL = "https://api.weather.gov/points/40.7433,-74.0324"
NWS_HEADERS = {
    "User-Agent": "Hoboken Transit Friction Map student prototype (contact: vanditb)",
}
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CONSTRUCTION_IMPACTS_PATH = DATA_DIR / "construction_impacts.csv"
OLD_CONSTRUCTION_LAYER_PATH = DATA_DIR / "construction_layer.csv"

HOBOKEN_CENTER = [40.7433, -74.0324]
HOBOKEN_LAT_MIN = 40.730
HOBOKEN_LAT_MAX = 40.760
HOBOKEN_LON_MIN = -74.050
HOBOKEN_LON_MAX = -74.010

MODE_NEED_BIKE = "already in area — need a bike"
MODE_NEED_DOCK = "coming into area — need a dock"


def fetch_json(url, headers=None):
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60)
def load_citibike_data():
    station_info = fetch_json(STATION_INFO_URL)
    station_status = fetch_json(STATION_STATUS_URL)

    info_df = pd.DataFrame(station_info["data"]["stations"])
    status_df = pd.DataFrame(station_status["data"]["stations"])

    merged = info_df.merge(status_df, on="station_id", how="inner")

    hoboken_stations = merged[
        (merged["lat"].between(HOBOKEN_LAT_MIN, HOBOKEN_LAT_MAX))
        & (merged["lon"].between(HOBOKEN_LON_MIN, HOBOKEN_LON_MAX))
    ].copy()

    return hoboken_stations


@st.cache_data(ttl=900)
def load_weather_data():
    point_data = fetch_json(NWS_POINTS_URL, headers=NWS_HEADERS)
    forecast_url = point_data["properties"]["forecast"]
    forecast_data = fetch_json(forecast_url, headers=NWS_HEADERS)
    return forecast_data["properties"]["periods"][0]


@st.cache_data
def load_construction_data():
    if CONSTRUCTION_IMPACTS_PATH.exists():
        return pd.read_csv(CONSTRUCTION_IMPACTS_PATH)
    if OLD_CONSTRUCTION_LAYER_PATH.exists():
        return pd.read_csv(OLD_CONSTRUCTION_LAYER_PATH)
    return pd.DataFrame()


def clamp_score(value):
    return max(0, min(100, value))


def is_station_offline(row):
    return row.get("is_renting") == 0 or row.get("is_returning") == 0


def calculate_friction(row, mode):
    if is_station_offline(row):
        return 100

    capacity = row.get("capacity")
    if pd.isna(capacity) or capacity <= 0:
        return None

    if mode == MODE_NEED_BIKE:
        available = row.get("num_bikes_available")
    else:
        available = row.get("num_docks_available")

    if pd.isna(available):
        return None

    score = 100 * (1 - available / capacity)
    return round(clamp_score(score), 1)


def parse_wind_speed(wind_text):
    speeds = re.findall(r"\d+", str(wind_text))
    return max([int(speed) for speed in speeds], default=0)


def calculate_weather_friction(period):
    score = 10
    forecast = period.get("shortForecast", "").lower()

    if any(word in forecast for word in ["rain", "shower", "thunderstorm", "snow"]):
        score += 30
    if any(word in forecast for word in ["heavy", "storm", "blizzard"]):
        score += 30

    wind_speed = parse_wind_speed(period.get("windSpeed", ""))
    if wind_speed >= 25:
        score += 30
    elif wind_speed >= 15:
        score += 15

    temperature = period.get("temperature")
    if isinstance(temperature, (int, float)):
        if temperature >= 95 or temperature <= 25:
            score += 25
        elif temperature >= 85 or temperature <= 40:
            score += 10

    return round(clamp_score(score), 1)


def calculate_combined_friction(bike_friction, weather_friction):
    if pd.isna(bike_friction):
        return None
    if weather_friction is None:
        return bike_friction
    return round(0.7 * bike_friction + 0.3 * weather_friction, 1)


def friction_color(row):
    if is_station_offline(row) or pd.isna(row["combined_friction"]):
        return "gray"
    if row["combined_friction"] < 35:
        return "green"
    if row["combined_friction"] < 70:
        return "orange"
    return "red"


def create_map(stations, construction, mode):
    transit_map = folium.Map(location=HOBOKEN_CENTER, zoom_start=14, tiles="CartoDB positron")

    bike_layer = folium.FeatureGroup(name="Citi Bike stations", show=True)

    for _, station in stations.iterrows():
        popup_html = f"""
        <b>{station["name"]}</b><br>
        Bikes available: {station["num_bikes_available"]}<br>
        Docks available: {station["num_docks_available"]}<br>
        Capacity: {station["capacity"]}<br>
        Bike friction: {station["bike_friction"] if pd.notna(station["bike_friction"]) else "unknown"}<br>
        Combined friction: {station["combined_friction"] if pd.notna(station["combined_friction"]) else "unknown"}<br>
        Mode: {mode}
        """

        folium.CircleMarker(
            location=[station["lat"], station["lon"]],
            radius=7,
            color=friction_color(station),
            fill=True,
            fill_color=friction_color(station),
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(bike_layer)

    bike_layer.add_to(transit_map)

    if not construction.empty:
        construction_layer = folium.FeatureGroup(name="Manual construction layer", show=True)
        for _, project in construction.dropna(subset=["lat", "lon"]).iterrows():
            popup_html = f"""
            <b>{project["project_name"]}</b><br>
            Street: {project["street"]}<br>
            Impact: {project["impact_type"]}<br>
            Hours: {project["start_time"]} to {project["end_time"]}<br>
            {project["description"]}<br>
            <i>Manually entered; verify with city source.</i>
            """
            folium.Marker(
                location=[project["lat"], project["lon"]],
                tooltip=f"Construction: {project['street']}",
                popup=folium.Popup(popup_html, max_width=320),
                icon=folium.Icon(color="blue", icon="wrench", prefix="fa"),
            ).add_to(construction_layer)
        construction_layer.add_to(transit_map)

    folium.LayerControl(collapsed=False).add_to(transit_map)

    return transit_map


def show_metrics(stations, weather_friction):
    valid_scores = stations["combined_friction"].dropna()

    station_count = len(stations)
    average_friction = round(valid_scores.mean(), 1) if not valid_scores.empty else "unknown"

    if valid_scores.empty:
        highest_station = "unknown"
    else:
        highest_row = stations.loc[stations["combined_friction"].idxmax()]
        highest_station = f"{highest_row['name']} ({highest_row['combined_friction']})"

    col1, col2, col3 = st.columns(3)
    col1.metric("Stations", station_count)
    col2.metric("Weather friction", weather_friction if weather_friction is not None else "N/A")
    col3.metric("Average combined friction", average_friction)
    st.metric("Highest friction station", highest_station)


def main():
    st.set_page_config(page_title="Hoboken Transit Friction Map", layout="wide")

    st.title("Hoboken Transit Friction Map")
    st.write(
        "Google Maps tells you the fastest route. This project tries to show why movement "
        "through a city becomes harder in certain places."
    )
    st.write(
        "This early prototype uses live Citi Bike and National Weather Service data. A small "
        "manual construction layer is included to test how street impacts could appear."
    )

    mode = st.radio(
        "Bike friction mode",
        [MODE_NEED_BIKE, MODE_NEED_DOCK],
        help="This changes whether the score focuses on bikes available or docks available.",
    )

    if st.button("Refresh live data"):
        st.cache_data.clear()
        st.rerun()

    st.caption("Rerunning or refreshing pulls the latest Citi Bike and weather data.")

    st.subheader("Hoboken weather")
    weather_period = None
    weather_friction = None
    try:
        weather_period = load_weather_data()
        weather_friction = calculate_weather_friction(weather_period)
        st.write(
            f"**{weather_period.get('name', 'Near-term forecast')}:** "
            f"{weather_period.get('temperature', 'Unknown')}°"
            f"{weather_period.get('temperatureUnit', '')}, "
            f"{weather_period.get('shortForecast', 'Forecast unavailable')}. "
            f"Wind: {weather_period.get('windSpeed', 'unknown')} "
            f"{weather_period.get('windDirection', '')}."
        )
        st.caption(f"Simple weather friction score: {weather_friction}/100")
    except (requests.RequestException, KeyError, IndexError) as error:
        st.warning(f"Weather data is not available right now: {error}")
        st.caption("Combined scores are using bike friction only until weather data returns.")

    try:
        stations = load_citibike_data()
    except (requests.RequestException, KeyError) as error:
        st.error(f"Could not load live Citi Bike data: {error}")
        st.stop()

    if stations.empty:
        st.warning("No Citi Bike stations were found in the Hoboken filter area.")
        st.stop()

    stations["bike_friction"] = stations.apply(lambda row: calculate_friction(row, mode), axis=1)
    stations["combined_friction"] = stations["bike_friction"].apply(
        lambda score: calculate_combined_friction(score, weather_friction)
    )
    construction = load_construction_data()

    show_metrics(stations, weather_friction)

    display_columns = [
        "name",
        "lat",
        "lon",
        "num_bikes_available",
        "num_docks_available",
        "capacity",
        "bike_friction",
        "combined_friction",
    ]

    st.subheader("Stations near Hoboken")
    st.dataframe(
        stations[display_columns].sort_values("combined_friction", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Map")
    st.caption(
        "Bike circles are colored by combined friction when weather is available. "
        "Blue tool markers are manually entered construction impacts."
    )
    st_folium(
        create_map(stations, construction, mode),
        width=None,
        height=600,
    )

    if not construction.empty:
        st.subheader("Construction layer")
        st.caption("These rows were manually transcribed and use approximate map coordinates.")
        construction_columns = [
            "project_name",
            "street",
            "start_date",
            "end_date",
            "impact_type",
            "description",
            "notes",
        ]
        st.dataframe(
            construction[construction_columns],
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
