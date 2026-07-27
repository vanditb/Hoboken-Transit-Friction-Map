"""Streamlit entry point for the Hoboken Transit Friction Map prototype."""

from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

from road_geometry import load_hoboken_graph, route_between_anchors
from scoring import (
    BASELINE_WEIGHTS,
    EXPERIMENTAL_WEIGHTS,
    calculate_bike_friction,
    calculate_construction_friction,
    calculate_weather_friction,
    combine_scores,
    project_affects_mode,
)


STATION_INFO_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"
NWS_POINTS_URL = "https://api.weather.gov/points/40.7433,-74.0324"
NWS_HEADERS = {"User-Agent": "Hoboken Transit Friction Map student prototype (contact: vanditb)"}
REQUEST_TIMEOUT_SECONDS = 20

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CONSTRUCTION_IMPACTS_PATH = DATA_DIR / "construction_impacts.csv"
OLD_CONSTRUCTION_LAYER_PATH = DATA_DIR / "construction_layer.csv"

HOBOKEN_CENTER = [40.7433, -74.0324]
HOBOKEN_LAT_MIN = 40.730
HOBOKEN_LAT_MAX = 40.760
HOBOKEN_LON_MIN = -74.050
HOBOKEN_LON_MAX = -74.010

MODE_NEED_BIKE = "already in area - need a bike"
MODE_NEED_DOCK = "coming into area - need a dock"
BASELINE_MODE = "Baseline: bike + weather"
EXPERIMENTAL_MODE = "Experimental: bike + weather + construction"


def fetch_json(url, headers=None):
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60)
def fetch_citibike_data():
    """Fetch and merge live GBFS feeds, then keep only the Hoboken study area."""
    station_info = fetch_json(STATION_INFO_URL)
    station_status = fetch_json(STATION_STATUS_URL)
    info_df = pd.DataFrame(station_info["data"]["stations"])
    status_df = pd.DataFrame(station_status["data"]["stations"])
    stations = info_df.merge(status_df, on="station_id", how="inner")
    return stations[
        stations["lat"].between(HOBOKEN_LAT_MIN, HOBOKEN_LAT_MAX)
        & stations["lon"].between(HOBOKEN_LON_MIN, HOBOKEN_LON_MAX)
    ].copy()


@st.cache_data(ttl=900)
def fetch_weather_data():
    """Fetch one near-term NWS period for Hoboken."""
    point_data = fetch_json(NWS_POINTS_URL, headers=NWS_HEADERS)
    forecast_url = point_data["properties"]["forecast"]
    forecast_data = fetch_json(forecast_url, headers=NWS_HEADERS)
    return forecast_data["properties"]["periods"][0]


@st.cache_data(ttl=300)
def load_construction_data():
    """Use the newer point-and-line CSV, with the old point CSV as a fallback."""
    if CONSTRUCTION_IMPACTS_PATH.exists():
        return pd.read_csv(CONSTRUCTION_IMPACTS_PATH)
    if OLD_CONSTRUCTION_LAYER_PATH.exists():
        return pd.read_csv(OLD_CONSTRUCTION_LAYER_PATH)
    return pd.DataFrame()


@st.cache_resource
def get_hoboken_graph():
    """Keep the OSM street graph in the Streamlit session once it is loaded."""
    return load_hoboken_graph()


def is_station_offline(row):
    return row.get("is_renting") == 0 or row.get("is_returning") == 0


def score_color(row):
    score = row.get("combined_friction")
    if is_station_offline(row) or pd.isna(score):
        return "gray"
    if score < 35:
        return "green"
    if score < 70:
        return "orange"
    return "red"


def value_or_unknown(row, column):
    value = row.get(column)
    if pd.isna(value) or value == "":
        return "unknown"
    return value


def construction_popup(project, geometry_note):
    return f"""
    <b>{value_or_unknown(project, 'project_name')}</b><br>
    Responsible party: {value_or_unknown(project, 'responsible_party')}<br>
    Location: {value_or_unknown(project, 'location')}<br>
    Impact: {value_or_unknown(project, 'impact_type')}<br>
    Traffic management: {value_or_unknown(project, 'traffic_management')}<br>
    Hours: {value_or_unknown(project, 'start_time')} to {value_or_unknown(project, 'end_time')}<br>
    Mode affected: {value_or_unknown(project, 'mode_affected')}<br>
    Verification: {value_or_unknown(project, 'verification_status')}<br>
    Geometry: {geometry_note}<br>
    Notes: {value_or_unknown(project, 'confidence_notes')}<br>
    """


def line_color(project):
    return "red" if str(project.get("friction_level", "")).lower() in {"high", "severe"} else "orange"


def build_map(stations, construction, bike_mode, use_road_geometry):
    """Build a new Folium map each rerun so layers cannot duplicate across reruns."""
    transit_map = folium.Map(location=HOBOKEN_CENTER, zoom_start=14, tiles="CartoDB positron")
    bike_layer = folium.FeatureGroup(name="Citi Bike stations", show=True)

    for _, station in stations.iterrows():
        popup_html = f"""
        <b>{station['name']}</b><br>
        Bikes available: {station['num_bikes_available']}<br>
        Docks available: {station['num_docks_available']}<br>
        Capacity: {station['capacity']}<br>
        Bike friction: {station['bike_friction'] if pd.notna(station['bike_friction']) else 'unknown'}<br>
        Weather friction: {station['weather_friction'] if pd.notna(station['weather_friction']) else 'unavailable'}<br>
        Construction friction: {station['construction_friction']}<br>
        Combined friction: {station['combined_friction'] if pd.notna(station['combined_friction']) else 'unknown'}<br>
        Bike mode: {bike_mode}
        """
        folium.CircleMarker(
            location=[station["lat"], station["lon"]], radius=7, color=score_color(station),
            fill=True, fill_color=score_color(station), fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(bike_layer)
    bike_layer.add_to(transit_map)

    graph = None
    graph_error = None
    if use_road_geometry and not construction.empty and (construction["geometry_type"].str.lower() == "line").any():
        graph, graph_error = get_hoboken_graph()

    if not construction.empty:
        construction_layer = folium.FeatureGroup(name="Construction impacts", show=True)
        for _, project in construction.iterrows():
            geometry_type = str(project.get("geometry_type", "point")).lower()
            if geometry_type == "line":
                columns = ["start_lat", "start_lon", "end_lat", "end_lon"]
                if any(pd.isna(project.get(column)) for column in columns):
                    continue

                coordinates = [[project["start_lat"], project["start_lon"]], [project["end_lat"], project["end_lon"]]]
                geometry_note = "straight approximate anchor line"
                if graph is not None:
                    route, route_error = route_between_anchors(
                        graph, project["start_lat"], project["start_lon"], project["end_lat"], project["end_lon"]
                    )
                    if route:
                        coordinates = route["coordinates"]
                        geometry_note = f"road-snapped OpenStreetMap route ({route['route_length_m']} m)"
                    else:
                        geometry_note = f"straight fallback: {route_error}"
                elif use_road_geometry:
                    geometry_note = f"straight fallback: {graph_error}"

                folium.PolyLine(
                    locations=coordinates, color=line_color(project), weight=5, opacity=0.85,
                    dash_array="8, 8", tooltip=f"Construction impact: {value_or_unknown(project, 'street')}",
                    popup=folium.Popup(construction_popup(project, geometry_note), max_width=380),
                ).add_to(construction_layer)
            else:
                if pd.isna(project.get("lat")) or pd.isna(project.get("lon")):
                    continue
                folium.Marker(
                    location=[project["lat"], project["lon"]],
                    tooltip=f"Construction: {value_or_unknown(project, 'street')}",
                    popup=folium.Popup(construction_popup(project, "manual point coordinate"), max_width=380),
                    icon=folium.Icon(color="blue", icon="wrench", prefix="fa"),
                ).add_to(construction_layer)
        construction_layer.add_to(transit_map)

    folium.LayerControl(collapsed=False).add_to(transit_map)
    return transit_map, graph_error


def add_scores(stations, weather_friction, construction, bike_mode, impact_mode, score_mode):
    need_bike = bike_mode == MODE_NEED_BIKE
    stations = stations.copy()
    stations["bike_friction"] = stations.apply(lambda row: calculate_bike_friction(row, need_bike), axis=1)
    stations["weather_friction"] = weather_friction

    construction_results = stations.apply(
        lambda row: calculate_construction_friction(row, construction, impact_mode), axis=1
    )
    stations["construction_friction"] = construction_results.apply(lambda result: result["score"])
    stations["nearest_construction_project"] = construction_results.apply(lambda result: result["nearest_project"])
    stations["nearest_construction_distance_m"] = construction_results.apply(lambda result: result["nearest_distance_m"])

    weights = BASELINE_WEIGHTS if score_mode == BASELINE_MODE else EXPERIMENTAL_WEIGHTS
    stations["combined_friction"] = stations.apply(
        lambda row: combine_scores(
            {
                "bike": row["bike_friction"], "weather": weather_friction,
                "construction": row["construction_friction"] if score_mode == EXPERIMENTAL_MODE else None,
            }, weights
        ), axis=1,
    )
    return stations


def show_metrics(stations, weather_friction, score_mode):
    valid_scores = stations["combined_friction"].dropna()
    highest = "unknown"
    if not valid_scores.empty:
        row = stations.loc[stations["combined_friction"].idxmax()]
        highest = f"{row['name']} ({row['combined_friction']})"
    columns = st.columns(4)
    columns[0].metric("Stations", len(stations))
    columns[1].metric("Weather friction", weather_friction if weather_friction is not None else "N/A")
    columns[2].metric("Average combined friction", round(valid_scores.mean(), 1) if not valid_scores.empty else "unknown")
    columns[3].metric("Scoring mode", "baseline" if score_mode == BASELINE_MODE else "experimental")
    st.caption(f"Highest friction station: {highest}")


def main():
    st.set_page_config(page_title="Hoboken Transit Friction Map", layout="wide")
    st.title("Hoboken Transit Friction Map")
    st.write("Google Maps tells you the fastest route. This project tries to show why movement through a city becomes harder in certain places.")
    st.caption("Early research prototype: live Citi Bike and weather data, plus a reviewed manual construction layer.")

    with st.sidebar:
        st.header("Controls")
        bike_mode = st.radio("Citi Bike availability mode", [MODE_NEED_BIKE, MODE_NEED_DOCK])
        impact_mode = st.selectbox("Travel or impact mode", ["All", "Biking", "Walking", "Driving", "Parking"])
        score_mode = st.radio("Scoring mode", [BASELINE_MODE, EXPERIMENTAL_MODE])
        use_road_geometry = st.checkbox("Try road-snapped construction lines", value=True)
        if st.button("Refresh live Citi Bike and weather data"):
            fetch_citibike_data.clear()
            fetch_weather_data.clear()
            st.rerun()
        st.caption("The Citi Bike control changes station availability friction. The impact-mode filter changes which construction rows are relevant.")

    weather_period = None
    weather_friction = None
    st.subheader("Hoboken weather")
    try:
        weather_period = fetch_weather_data()
        weather_friction = calculate_weather_friction(weather_period)
        st.write(
            f"**{weather_period.get('name', 'Near-term forecast')}:** {weather_period.get('temperature', 'Unknown')}°"
            f"{weather_period.get('temperatureUnit', '')}, {weather_period.get('shortForecast', 'Forecast unavailable')}. "
            f"Wind: {weather_period.get('windSpeed', 'unknown')} {weather_period.get('windDirection', '')}."
        )
        st.caption(f"Simple weather friction score: {weather_friction}/100")
    except (requests.RequestException, KeyError, IndexError, ValueError) as error:
        st.warning(f"Weather component is unavailable right now: {error}")
        st.caption("Scores automatically use the remaining available components.")

    try:
        stations = fetch_citibike_data()
    except (requests.RequestException, KeyError, ValueError) as error:
        st.error(f"Citi Bike component is unavailable right now: {error}")
        st.stop()
    if stations.empty:
        st.warning("No Citi Bike stations were found in the Hoboken filter area.")
        st.stop()

    construction = load_construction_data()
    filtered_construction = construction[
        construction.apply(lambda project: project_affects_mode(project, impact_mode), axis=1)
    ].copy() if not construction.empty else construction
    stations = add_scores(stations, weather_friction, filtered_construction, bike_mode, impact_mode, score_mode)
    show_metrics(stations, weather_friction, score_mode)

    st.subheader("Stations near Hoboken")
    station_columns = [
        "name", "num_bikes_available", "num_docks_available", "capacity", "bike_friction",
        "weather_friction", "construction_friction", "combined_friction",
        "nearest_construction_project", "nearest_construction_distance_m",
    ]
    st.dataframe(stations[station_columns].sort_values("combined_friction", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("Map")
    st.caption("Station colors use the selected score. Construction points are blue; dashed lines are road-snapped when possible, otherwise labeled as straight fallbacks. Map data © OpenStreetMap contributors.")
    transit_map, graph_error = build_map(stations, filtered_construction, bike_mode, use_road_geometry)
    if graph_error and use_road_geometry:
        st.info(f"Road-snapped construction lines are unavailable right now. Straight fallback lines are shown instead. {graph_error}")
    st_folium(transit_map, width=None, height=620, key="hoboken_friction_map_v2")

    if not filtered_construction.empty:
        st.subheader("Construction impacts")
        st.caption("Filtered for the selected impact mode. Rows are manually maintained; verification and active status are shown before they affect experimental scoring.")
        construction_columns = [
            "project_name", "geometry_type", "street", "impact_type", "mode_affected", "active_status",
            "verification_status", "geometry_method", "confidence_notes",
        ]
        st.dataframe(filtered_construction[[column for column in construction_columns if column in filtered_construction]], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
