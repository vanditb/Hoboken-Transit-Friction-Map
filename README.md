# Hoboken Transit Friction Map

An interactive smart-city mobility map for showing where movement through Hoboken becomes harder.

Google Maps tells you the fastest route. This project tries to show why movement through a city becomes harder in certain places.

This is an early research prototype for my work with Professor Philip Odonkor at Stevens. It is not a route planner or a finished city data platform.

## Current Status

The v0 bike friction layer works. The app pulls live Citi Bike station information and status data, filters stations near Hoboken, and scores how hard it may be to find a bike or an open dock.

Right now this is still an early prototype. The first working layer is Citi Bike friction. The next goal is to add weather and construction/road-closure data so the map starts to feel more like a real urban friction tool.

This sprint adds a simple National Weather Service score and combines it with bike friction. It also includes a first manually entered construction CSV and construction markers. Those construction rows and approximate coordinates still need to be checked against the city updates.

## What the App Does

- loads live Citi Bike stations near Hoboken
- switches between "need a bike" and "need a dock" modes
- loads the near-term National Weather Service forecast for Hoboken
- calculates bike, weather, and combined friction scores
- colors Citi Bike stations by the combined score when weather is available
- shows a small manual construction layer with separate blue markers
- falls back to bike friction if weather cannot be loaded

## Data Sources

- Citi Bike GBFS station information and station status
- National Weather Service forecast API
- Hoboken construction updates, manually transcribed for the first test layer

The full source inventory and current statuses are in `data_sources.md`.

## Planned Next Steps

- verify the manual construction rows and coordinates
