# Data Sources

This table tracks possible data sources for the Hoboken Transit Friction Map.

For the current v0 app, the only data source actually used in the Streamlit map is Citi Bike GBFS station information and station status. The other sources are kept here as a research inventory for later layers.

| Source | Link | What it gives | Live/static/changing | Access difficulty | How it could affect friction score | Current status |
| --- | --- | --- | --- | --- | --- | --- |
| Citi Bike GBFS feed | https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json | Main GBFS feed that points to Citi Bike station information, station status, bike status, and alerts | Live/changing | Easy/public JSON | Helps identify the Citi Bike GBFS feeds | Reference for v0 |
| Citi Bike station information | https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json | Station names, station IDs, locations, and capacity | Mostly static, updated when stations change | Easy/public JSON | Capacity is used as the denominator for bike/dock friction | Used in v0 app |
| Citi Bike station status | https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json | Available bikes, available docks, station status, and last update time | Live/changing | Easy/public JSON | Low bikes or low docks creates higher bike friction | Used in v0 app |
| National Weather Service API | https://www.weather.gov/documentation/services-web-api | Weather forecasts, alerts, observations, rain, wind, temperature, and storm conditions | Live/forecast | Easy/public API | Bad weather could increase walking, biking, and transit friction | Tested separately |
| OpenStreetMap | https://www.openstreetmap.org/ | Street network, walking paths, bike lanes, roads, sidewalks, amenities, and map features | Mostly static, community-maintained | Easy/public data | Could help understand street network, sidewalks, bike lanes, and barriers | Future layer |
| OSMnx | https://osmnx.readthedocs.io/ | Python tool for downloading and analyzing OpenStreetMap street networks | Static data tool | Medium/Python package | Could support network-based friction instead of just station points | Future layer |
| Hoboken construction updates | https://www.hobokennj.gov/hoboken-construction-updates | Construction projects and street disruption updates | Changing | Medium | Active construction could increase local movement friction | Not tested |
| Hoboken mapping hub | https://hoboken-mapping-hub-cityofhoboken.hub.arcgis.com/ | City GIS maps and public mapping layers | Changing/static depending on layer | Medium | Could provide local infrastructure, closures, or planning layers | Not tested |
| NJ Transit developer portal | https://www.njtransit.com/developer-tools | NJ Transit developer access and transit data | Live/changing | Harder, may need account/API key | Delays or service changes could add transit friction | Stretch |
| NJ Transit developer terms | https://developer.njtransit.com/terms/ | Rules for using NJ Transit developer data | Static/legal | Medium | Needed before using NJ Transit data in the project | Not tested |
| GTFS realtime reference | https://gtfs.org/documentation/realtime/reference/ | Standard for real-time transit updates | Live data format reference | Medium | Could help interpret trip updates, vehicle positions, and service alerts | Stretch |

## Quick Priority List

1. Citi Bike station information + station status: best first live data source because it is public, simple, and directly useful.
2. National Weather Service API: good second source because weather directly affects walking, biking, and transit.
3. OpenStreetMap / OSMnx: useful later for street network context.
4. Hoboken construction updates: important for construction friction, but may require manual or semi-manual extraction.
5. NJ Transit / GTFS realtime: important for transit friction, but likely harder because it may require developer access and has more rules.
