import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium


STATION_INFO_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"

HOBOKEN_CENTER = [40.7433, -74.0324]
HOBOKEN_LAT_MIN = 40.730
HOBOKEN_LAT_MAX = 40.760
HOBOKEN_LON_MIN = -74.050
HOBOKEN_LON_MAX = -74.010

MODE_NEED_BIKE = "already in area — need a bike"
MODE_NEED_DOCK = "coming into area — need a dock"


def fetch_json(url):
    response = requests.get(url, timeout=20)
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


def friction_color(row):
    if is_station_offline(row) or pd.isna(row["friction"]):
        return "gray"
    if row["friction"] < 35:
        return "green"
    if row["friction"] < 70:
        return "orange"
    return "red"


def create_map(stations, mode):
    transit_map = folium.Map(location=HOBOKEN_CENTER, zoom_start=14, tiles="CartoDB positron")

    for _, station in stations.iterrows():
        popup_html = f"""
        <b>{station["name"]}</b><br>
        Bikes available: {station["num_bikes_available"]}<br>
        Docks available: {station["num_docks_available"]}<br>
        Capacity: {station["capacity"]}<br>
        Friction score: {station["friction"] if pd.notna(station["friction"]) else "unknown"}<br>
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
        ).add_to(transit_map)

    return transit_map


def show_metrics(stations):
    valid_scores = stations["friction"].dropna()

    station_count = len(stations)
    average_friction = round(valid_scores.mean(), 1) if not valid_scores.empty else "unknown"

    if valid_scores.empty:
        highest_station = "unknown"
    else:
        highest_row = stations.loc[stations["friction"].idxmax()]
        highest_station = f"{highest_row['name']} ({highest_row['friction']})"

    col1, col2, col3 = st.columns(3)
    col1.metric("Stations", station_count)
    col2.metric("Average friction", average_friction)
    col3.metric("Highest friction station", highest_station)


def main():
    st.set_page_config(page_title="Hoboken Transit Friction Map", layout="wide")

    st.title("Hoboken Transit Friction Map")
    st.write(
        "Google Maps tells you the fastest route. This project tries to show why movement "
        "through a city becomes harder in certain places."
    )
    st.write(
        "This v0 prototype uses live Citi Bike GBFS data near Hoboken and calculates a simple "
        "bike friction score."
    )

    mode = st.radio(
        "Bike friction mode",
        [MODE_NEED_BIKE, MODE_NEED_DOCK],
        help="This changes whether the score focuses on bikes available or docks available.",
    )

    if st.button("Refresh Citi Bike data"):
        st.cache_data.clear()
        st.rerun()

    st.caption("Rerunning or refreshing the app pulls the latest Citi Bike data.")

    try:
        stations = load_citibike_data()
    except (requests.RequestException, KeyError) as error:
        st.error(f"Could not load live Citi Bike data: {error}")
        st.stop()

    if stations.empty:
        st.warning("No Citi Bike stations were found in the Hoboken filter area.")
        st.stop()

    stations["friction"] = stations.apply(lambda row: calculate_friction(row, mode), axis=1)

    show_metrics(stations)

    display_columns = [
        "name",
        "lat",
        "lon",
        "num_bikes_available",
        "num_docks_available",
        "capacity",
        "friction",
    ]

    st.subheader("Stations near Hoboken")
    st.dataframe(
        stations[display_columns].sort_values("friction", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Map")
    st_folium(create_map(stations, mode), width=None, height=600)


if __name__ == "__main__":
    main()
