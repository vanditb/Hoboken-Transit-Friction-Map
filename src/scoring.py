"""Small, explainable friction-score helpers for the prototype."""

import math
import re

import pandas as pd


BASELINE_WEIGHTS = {"bike": 0.70, "weather": 0.30}
EXPERIMENTAL_WEIGHTS = {"bike": 0.60, "weather": 0.20, "construction": 0.20}
SEVERITY_FACTORS = {"low": 0.25, "medium": 0.50, "high": 0.75, "severe": 1.00}


def clamp_score(value):
    """Keep a score inside the 0 to 100 range."""
    return max(0.0, min(100.0, float(value)))


def calculate_bike_friction(row, need_bike):
    """Score low bike or dock availability at one Citi Bike station."""
    if row.get("is_renting") == 0 or row.get("is_returning") == 0:
        return 100.0

    capacity = row.get("capacity")
    available = row.get("num_bikes_available" if need_bike else "num_docks_available")
    if pd.isna(capacity) or pd.isna(available) or capacity <= 0:
        return None

    return round(clamp_score(100 * (1 - available / capacity)), 1)


def parse_wind_speed(wind_text):
    speeds = re.findall(r"\d+", str(wind_text))
    return max((int(speed) for speed in speeds), default=0)


def calculate_weather_friction(period):
    """Use the near-term NWS period for a simple, visible weather assumption."""
    score = 10
    forecast = str(period.get("shortForecast", "")).lower()

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


def normalize_modes(value):
    """Turn inconsistent manual mode text into a predictable set of labels."""
    text = str(value or "").lower()
    if not text or text == "nan":
        return set()
    if "all" in text:
        return {"walking", "biking", "driving", "parking"}

    modes = set()
    if any(word in text for word in ["bike", "biking", "bicycle", "cycl"]):
        modes.add("biking")
    if any(word in text for word in ["walk", "pedestrian", "sidewalk"]):
        modes.add("walking")
    if any(word in text for word in ["drive", "driving", "vehicle", "traffic"]):
        modes.add("driving")
    if "park" in text:
        modes.add("parking")
    return modes


def project_affects_mode(project, selected_mode):
    """Return whether a construction row matters for the selected impact mode."""
    if selected_mode == "All":
        return True
    return selected_mode.lower() in normalize_modes(project.get("mode_affected"))


def _web_mercator(lat, lon):
    """Project WGS84 coordinates to Web Mercator meters for local distance checks."""
    radius = 6378137.0
    lat = max(min(float(lat), 89.5), -89.5)
    x = radius * math.radians(float(lon))
    y = radius * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def _point_to_segment_distance(point, start, end):
    px, py = point
    ax, ay = start
    bx, by = end
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    position = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    position = max(0.0, min(1.0, position))
    return math.hypot(px - (ax + position * dx), py - (ay + position * dy))


def project_distance_m(station_lat, station_lon, project):
    """Find point-to-point or point-to-line distance using projected meter coordinates."""
    point = _web_mercator(station_lat, station_lon)
    geometry_type = str(project.get("geometry_type", "point")).lower()
    try:
        if geometry_type == "line":
            start = _web_mercator(project["start_lat"], project["start_lon"])
            end = _web_mercator(project["end_lat"], project["end_lon"])
            return _point_to_segment_distance(point, start, end)
        location = _web_mercator(project["lat"], project["lon"])
        return math.hypot(point[0] - location[0], point[1] - location[1])
    except (KeyError, TypeError, ValueError):
        return None


def project_is_score_eligible(project, selected_mode):
    """Manual rows must be current and at least partially checked before scoring."""
    verification = str(project.get("verification_status", "unverified")).lower()
    active = str(project.get("active_status", "unknown")).lower()
    return (
        verification in {"verified", "partially_verified"}
        and active == "active"
        and project_affects_mode(project, selected_mode)
    )


def calculate_construction_friction(station, construction, selected_mode):
    """Return experimental construction friction and the nearest eligible project."""
    best_score = 0.0
    nearest_name = None
    nearest_distance = None

    for _, project in construction.iterrows():
        if not project_is_score_eligible(project, selected_mode):
            continue
        distance_m = project_distance_m(station["lat"], station["lon"], project)
        if distance_m is None:
            continue

        if nearest_distance is None or distance_m < nearest_distance:
            nearest_distance = distance_m
            nearest_name = project.get("project_name", "unknown")

        severity = SEVERITY_FACTORS.get(str(project.get("friction_level", "")).lower(), 0.0)
        distance_decay = max(0.0, 1 - distance_m / 300.0)
        score = 100 * severity * distance_decay
        best_score = max(best_score, score)

    return {
        "score": round(clamp_score(best_score), 1),
        "nearest_project": nearest_name,
        "nearest_distance_m": round(nearest_distance, 1) if nearest_distance is not None else None,
    }


def combine_scores(components, weights):
    """Combine available components and renormalize their prototype weights."""
    available = {
        name: value
        for name, value in components.items()
        if value is not None and not pd.isna(value) and name in weights
    }
    if not available:
        return None

    total_weight = sum(weights[name] for name in available)
    score = sum(available[name] * weights[name] / total_weight for name in available)
    return round(clamp_score(score), 1)
