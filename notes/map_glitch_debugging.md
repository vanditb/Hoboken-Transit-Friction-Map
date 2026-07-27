# Map Glitch Debugging

## Symptom

The project notes said the map could sometimes glitch when weather, construction, and Streamlit reruns happened together.

## Reproduction Attempt

I reviewed the existing map code and ran the construction CSV check before changing the app. I did not have a saved error message or a repeatable crash case in the repository, so I could not prove one exact cause.

## Likely Causes Checked

- Citi Bike and weather requests were made again whenever Streamlit reran unless Streamlit caching applied.
- The original map component did not have an explicit stable `st_folium` key.
- Construction line rows could have blank coordinate fields, which could make Folium line creation fragile.
- The map was rebuilt during reruns, but there was no one clear place that explained that this was intentional.

## Changes Made

- Citi Bike and weather fetches now use named `st.cache_data` functions with TTL values and request timeouts.
- The OSM street graph is held with `st.cache_resource` once it loads.
- The Folium component now uses the stable key `hoboken_friction_map_v2`.
- The app builds one fresh Folium map per rerun, instead of reusing a previous map object.
- Construction lines are skipped when their required anchors are blank, and road-snapping failures fall back to the existing straight line.
- Refresh clears only the live Citi Bike and weather caches, then reruns once.

## Actual Cause

No single original cause was reproduced from the committed repository, so this is still unknown.

## Remaining Uncertainty

Road-snapping adds a larger external OpenStreetMap request the first time the graph is needed. The app handles a failed request by keeping the straight fallback lines, but it still needs more manual testing on the normal deployment environment.
