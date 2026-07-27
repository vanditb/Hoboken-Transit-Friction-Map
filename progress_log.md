# Progress Log

update:

- GitHub repo organized
- data source table added
- friction score doc added
- Citi Bike API tested
- simple Citi Bike dataframe created
- basic map started

- all of the minimum update items
- Streamlit app shows Citi Bike stations near Hoboken
- stations are colored by bike availability/friction
- app has a toggle for "need a bike" vs "need a dock"

## initial setup

worked on:

- created initial project structure
- documented data sources
- created first friction score notes
- started v0 streamlit prototype using citi bike gbfs data

what works:

- citi bike station information/status sources are identified
- v0 focuses on bike friction first

issues / mistakes / things I noticed:

- at first I had a lot of possible data sources listed, but the actual v0 app only needs Citi Bike right now
- I had to separate "sources we might use later" from "sources actually used in the current prototype"
- the friction score idea could get complicated quickly, so I kept it to one simple bike-only score for now

next steps:

- test live citi bike data
- filter stations near hoboken
- add weather friction
- investigate construction/no-parking data
- eventually test nj transit data

## v0 verification

worked on:

- ran the Citi Bike API test with `python3`
- ran the National Weather Service API test with `python3`
- checked Python syntax for the app and API scripts

what works:

- Citi Bike station information/status data loaded successfully
- the Hoboken filter returned live nearby stations
- the weather test reached the National Weather Service API and printed forecast periods

notes:

- this local shell does not have `python` available, but `python3` worked
- `streamlit` is not installed in this local shell yet, so the app startup command could not be tested here
- the local Mac Python showed an urllib3/OpenSSL warning, but the API requests still worked

issues / mistakes / things I noticed:

- I originally wrote the run commands using `python`, but on this machine the command was actually `python3`
- I marked the Citi Bike sources as tested after the API script worked, but I had to make the documentation clearer that only Citi Bike is used in the actual app
- the National Weather Service API worked, but it is only a separate test right now and not part of the friction score yet
- the data source inventory from Google Sheets had more sources than the prototype uses, so I cleaned the repo version to avoid making the project look more complete than it is
- Streamlit still needs to be installed before I can fully test the app in the browser

## weather and construction sprint

worked on:

- added a first weather layer using the National Weather Service API
- combined bike friction and weather friction with a simple 70/30 weighting
- started investigating the Hoboken construction updates page
- created a manual construction CSV with the fields needed for a map layer
- added separate construction markers and a construction table to the app
- cleaned the README, source table, and scoring notes so they match the current prototype

what works:

- the app can show the near-term Hoboken forecast and a simple weather friction score
- Citi Bike still has the same need-a-bike and need-a-dock modes
- Citi Bike marker colors use the combined score when weather is available
- if the weather request fails, the app keeps working with bike friction only
- manual construction rows with coordinates can appear as separate blue markers

what was confusing / rough:

- some API fields were not named exactly how I expected, especially because wind speed arrives as text instead of one number
- I realized the construction data is not as clean as the Citi Bike API. The page has useful street closure information, but I still need to figure out whether it can be pulled from a real API or if the first version should just use a manually created CSV
- construction information can be webpage text instead of clean JSON, and one project can mention several streets or different dates
- the city page does not give coordinates for every impact, so the first construction layer uses approximate coordinates and labels them that way
- weather scoring is still simple and needs feedback; the current forecast applies one weather score across all Hoboken stations
- construction markers are displayed, but construction does not change the combined numeric score yet

next steps:

- verify the manual construction rows and approximate coordinates
- ask whether construction automation or clearer map presentation should be the next priority
- investigate whether the Hoboken Mapping Hub exposes useful ArcGIS layers
- decide how construction distance and severity should affect a station score
- get feedback on the 70/30 bike and weather weighting

## construction line impact sprint

worked on:

- changed the construction layer from marker-only to point + line impacts
- added `data/construction_impacts.csv`
- added dashed construction lines to the map for impacted street segments
- kept old `construction_layer.csv` in the repo as the earlier simple marker version
- updated the construction data test so it checks point rows and line rows differently

what works:

- point construction rows can still show as blue markers
- line/corridor construction rows can show as dashed orange or red lines
- the construction table now includes the geometry type and traffic management notes
- the numeric friction score is still just bike + weather, which is safer for now

rough parts / things I noticed:

- the city construction information is more map-like than I first realized because some impacts are dotted corridors, not just single locations
- I had to use approximate start and end coordinates for the first line segments
- the CSV is useful for testing the idea, but it is still manual and needs verification
- I still need to figure out whether the embedded map has a GIS layer or API behind it

next steps:

- verify the approximate line coordinates against the Hoboken map
- ask Professor Odonkor whether line impacts should affect nearby Citi Bike stations
- investigate whether construction lines can be pulled automatically from a GIS/API source later

## road geometry, construction scoring, and history sprint

worked on:

- audited the repository after July 13 before changing the code; there were no commits strictly after that date
- investigated the Hoboken construction map and found public ArcGIS point and line FeatureServer layers behind it
- added construction verification, active-status, geometry-method, and source-text fields to the manual CSV
- added an impact-mode filter for biking, walking, driving, and parking
- kept the old bike + weather score as the baseline and added a separate experimental construction score option
- added OSMnx road-snapping for the manual line anchors, with a straight fallback line when routing is unavailable
- added a historical Citi Bike snapshot collector and a first prediction notebook that waits for real data before training

what worked:

- the city ArcGIS line layer returned project fields and polyline geometry during the source audit
- the road graph loaded, anchor snapping worked, and a road route with multiple points was found in the road geometry test
- the construction CSV validator passed with 4 rows, 3 line rows, 1 point row, and 1 expired row
- the live Citi Bike check returned 34 Hoboken-area stations during testing
- the NWS test returned forecast periods during testing
- one real history snapshot was saved with 34 station rows on 2026-07-27
- the browser check switched between need-a-bike/need-a-dock, baseline/experimental scoring, Biking construction filtering, straight fallback lines, and live refresh without a crash

real issues I ran into:

- the first OSMnx route test failed because its nearest-node helper expected the optional scikit-learn package on an unprojected graph
- I replaced that helper with a small direct nearest-node search because Hoboken is small and I did not need to add a machine-learning package only for map routing
- I could not reproduce one exact original map-glitch crash from the committed repository, so the debugging note only documents the safeguards added and the remaining uncertainty
- the local Python still prints an urllib3/LibreSSL warning during requests, but the live Citi Bike, weather, collector, and road tests completed

next steps:

- decide with Professor Odonkor whether the public ArcGIS layer should become a reviewed automatic import or stay as a verification reference
- continue collecting 15-minute snapshots across more days before training a prediction model
- validate the experimental construction-distance assumptions against real station behavior
- review the construction rows again when the city updates change
