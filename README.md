# Hoboken Transit Friction Map

An interactive smart-city mobility map for showing where movement through Hoboken becomes harder.

Google Maps tells you the fastest route. This project tries to show why movement through a city becomes harder in certain places.

This is an early research prototype for my work with Professor Philip Odonkor at Stevens. It is not a route planner or a finished city data platform.

## Current Status

The v0 bike friction layer works. The app pulls live Citi Bike station information and status data, filters stations near Hoboken, and scores how hard it may be to find a bike or an open dock.

Right now this is still an early prototype. The first working layer is Citi Bike friction. The next goal is to add weather and construction/road-closure data so the map starts to feel more like a real urban friction tool.

The app now has Citi Bike + weather friction. Construction is being added as a separate visual impact layer, but it is not part of the numeric score yet.

The construction layer moved from a simple marker-only CSV to `data/construction_impacts.csv`, which can represent both point projects and line/corridor impacts. The manual construction rows and approximate coordinates still need to be checked against the city updates.

## What the App Does

- loads live Citi Bike stations near Hoboken
- switches between "need a bike" and "need a dock" modes
- loads the near-term National Weather Service forecast for Hoboken
- calculates bike, weather, and combined friction scores
- colors Citi Bike stations by the combined score when weather is available
- shows a small manual construction layer with point projects and dashed street/corridor impacts
- falls back to bike friction if weather cannot be loaded

## Data Sources

- Citi Bike GBFS station information and station status
- National Weather Service forecast API
- Hoboken construction updates, manually transcribed into a point + line impact CSV for the first test layer

The full source inventory and current statuses are in `data_sources.md`.

## Planned Next Steps

- verify the manual construction rows and point/line coordinates
- decide whether construction should be automated or kept manual for the next demo
- decide how construction lines should eventually affect friction scores
- improve weather scoring after getting feedback
- investigate ArcGIS layers in the Hoboken Mapping Hub
- later add OpenStreetMap street context and transit alerts

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
python3 -m pip install -r requirements.txt
```

Run the API and CSV checks:

```bash
python3 api_tests/test_citibike.py
python3 api_tests/test_weather.py
python3 api_tests/test_construction_data.py
```

Run the app:

```bash
python3 -m streamlit run src/app.py
```

Rerunning or using the refresh button pulls the newest Citi Bike and weather data. The construction CSV does not update automatically yet.
