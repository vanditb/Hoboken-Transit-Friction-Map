# Hoboken Transit Friction Map

An early smart-city mobility map for showing where movement through Hoboken becomes harder and why.

Google Maps tells you the fastest route. This project tries to show why movement through a city becomes harder in certain places.

This is an early research prototype for my work with Professor Philip Odonkor at Stevens. It is not a route planner or a finished city data platform.

## Current Status

The Citi Bike layer works with live station information and status data. The app also loads a near-term National Weather Service forecast, and construction is represented as a reviewed manual point and line layer.

Right now this is still an early prototype. The first working layer was Citi Bike friction. Weather is now included, and construction is available as both a visual layer and an optional experimental score component.

## What the App Does

- loads live Citi Bike stations near Hoboken
- switches between need-a-bike and need-a-dock availability friction
- shows near-term NWS weather and a simple weather friction score
- offers a baseline bike + weather score and an experimental bike + weather + construction score
- lets the user filter construction relevance for biking, walking, driving, or parking
- shows manual construction points and dashed corridors
- tries to road-snap corridor anchors to OpenStreetMap public streets when OSMnx can load the local graph
- falls back to a labeled straight line if road snapping fails
- keeps expired and unverified construction rows out of experimental friction by default

The road-snapped display is an OpenStreetMap-based approximation, not official Hoboken construction geometry.

## Simple Architecture

```text
data sources
-> validation and historical collection
-> bike, weather, and construction friction components
-> baseline or experimental combined score
-> interactive map
-> future shortage prediction model
```

## Construction Status

`data/construction_impacts.csv` is a small reviewed prototype dataset. It keeps source URLs, verification status, active status, and notes about approximate coordinates.

The City of Hoboken construction page links to public ArcGIS point and line layers. Those layers were inspected, but the project does not automatically import them yet because active-status review still needs a clear rule. See `notes/construction_source_audit.md`.

## Historical Data and Prediction

The collector saves real station snapshots locally by date. The history folder is ignored by Git.

```bash
python3 scripts/collect_snapshot.py --once
python3 scripts/collect_snapshot.py --loop --interval-minutes 15
```

`notebooks/friction_prediction_baseline.ipynb` is a Colab-compatible starting notebook. It prepares 15, 30, and 60-minute features and one-hour bike/dock shortage labels. It does not report model results until enough real history is available.

## Tech Stack

- Python
- Streamlit
- pandas
- requests
- Folium and streamlit-folium
- OSMnx 2.x for optional road-snapped construction display

## How to Run

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the checks:

```bash
python3 api_tests/test_citibike.py
python3 api_tests/test_weather.py
python3 api_tests/test_construction_data.py
python3 api_tests/test_scoring.py
python3 api_tests/test_road_geometry.py
python3 api_tests/test_snapshot_schema.py
python3 api_tests/test_prediction_features.py
```

Run the app:

```bash
python3 -m streamlit run src/app.py
```

Open the notebook locally in Jupyter or upload `notebooks/friction_prediction_baseline.ipynb` and the collected `data/history` files to Google Colab.

For Streamlit Community Cloud setup, see `notes/streamlit_deployment.md`.

## Limitations and Next Steps

- Construction CSV coordinates and manual statuses still need continued review.
- The city ArcGIS service works as a source reference, but automatic import is not built yet.
- Construction score weights are prototype assumptions, not validated results.
- Road snapping needs a first OpenStreetMap graph download and may fall back if that request fails.
- No historical snapshots or valid prediction model results exist in the repository yet.

## Attribution

Road context and road-snapped display geometry use OpenStreetMap data. © OpenStreetMap contributors.
