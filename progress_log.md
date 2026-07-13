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

