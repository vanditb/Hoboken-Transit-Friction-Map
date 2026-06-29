# Hoboken Transit Friction Map

An interactive smart-city mobility map for showing where movement through Hoboken becomes harder.

Google Maps tells you the fastest route. This project tries to show why movement through a city becomes harder in certain places.

This is an early v0 research prototype for my work with Professor Philip Odonkor at Stevens. The goal is not to build a full route planner. The goal is to make a simple, explainable map that can start combining live urban data into a "friction" score.

## Current Prototype Goal

The current version focuses on Citi Bike stations near Hoboken. It pulls live GBFS station data, filters stations around Hoboken, and calculates a basic bike friction score.

For v0, bike friction has two modes:

- already in area: friction is high when available bikes are low
- coming into area: friction is high when available docks are low

## Current Data Sources

- Citi Bike GBFS station information
- Citi Bike GBFS station status
- National Weather Service API is being tested separately

More data sources are documented in `data_sources.md`.

## Planned Next Layers

- weather friction
- construction friction
- transit friction
- street/network context from OpenStreetMap
- possible no-parking or lane closure data from Hoboken sources

## Tech Stack

- Python
- Streamlit
- pandas
- requests
- Folium
- streamlit-folium

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

On some Macs, use `pip3` and `python3` instead of `pip` and `python`.

Run the API tests:

```bash
python api_tests/test_citibike.py
python api_tests/test_weather.py
```

Run the Streamlit app:

```bash
streamlit run src/app.py
```

The app fetches the latest Citi Bike data each time it reruns.
