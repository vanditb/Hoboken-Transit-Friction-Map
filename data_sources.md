# Data Sources

This is my working source inventory. The statuses describe what is actually being used or tested, not what I hope to add later.

| Source | Link | What it gives | Type | Access difficulty | Friction use | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Citi Bike station information | https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json | Station IDs, names, coordinates, and capacity | Changing slowly | Easy public JSON | Gives station location and capacity for the bike score | Tested / works in app |
| Citi Bike station status | https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json | Available bikes, docks, and operating status | Live | Easy public JSON | Low bike or dock availability raises bike friction | Tested / works in app |
| National Weather Service API | https://www.weather.gov/documentation/services-web-api | Forecast periods with temperature, conditions, and wind | Live forecast | Easy public API with User-Agent | Rain, snow, wind, and extreme temperatures raise weather friction | Tested / works; now integrated |
| Hoboken construction updates | https://www.hobokennj.gov/hoboken-construction-updates | Current projects, road closures, no-parking areas, closure hours, affected streets, and some corridor-style impacts | Weekly/changing webpage | Medium | Nearby construction could be medium; closures, detours, and impacted corridors could be high | Used as a reviewed manual source |
| Hoboken construction ArcGIS layers | https://services8.arcgis.com/LDmC4ZVHdfKcEzxl/arcgis/rest/services/Construction/FeatureServer/0 | Public line geometry plus project name, responsible party, traffic management, hours, work period, and related fields | Changing public GIS service | Medium; public query worked during audit | Can verify corridor geometry and construction details | Investigated; not automatically imported yet |
| Hoboken Mapping Hub | https://hoboken-mapping-hub-cityofhoboken.hub.arcgis.com/ | Possible public GIS maps and downloadable city layers | Depends on layer | Medium | Could provide more reliable geometry for projects or street impacts | Investigating / possible GIS layers |
| OpenStreetMap | https://www.openstreetmap.org/ | Roads, paths, bike lanes, sidewalks, and amenities | Community-maintained | Easy public data | Adds street context and could support distance-to-impact calculations | Planned |
| OSMnx | https://osmnx.readthedocs.io/ | Python access to OpenStreetMap street networks | Tool/static downloads | Medium | Road-snaps approximate construction anchors for a display approximation | Added for the prototype; needs first graph download |
| NJ Transit developer portal | https://www.njtransit.com/developer-tools | Transit data and developer access | Live/changing | Harder; may require access and terms review | Delays and alerts could raise transit friction | Later / harder |
| GTFS Realtime reference | https://gtfs.org/documentation/realtime/reference/ | Standard fields for transit alerts, vehicles, and trip updates | Format reference | Medium | Helps interpret future transit feeds | Later |
| PATH | https://www.panynj.gov/path/en/index.html | PATH service information and alerts | Live/changing | Unknown for a reusable public feed | Service changes near Hoboken Terminal could raise transit friction | Stretch |
| 511NJ | https://www.511nj.org/ | Regional traffic incidents, construction, and road conditions | Live/changing | Needs investigation | Could add regional road closures or incidents | Stretch |

## Construction Notes

The Hoboken construction page has the information I need, but it is mixed into webpage text instead of clean JSON. The city page and map also show that some impacts are corridor/line-based, not just point-based projects. The current prototype uses manual extraction into `data/construction_impacts.csv` so I can represent both point projects and impacted street segments.

The current manual rows keep the city source URL, status fields, and a note when coordinates are approximate. The audit found public ArcGIS point and line FeatureServer layers behind the city map. Future work is to decide how to review active status before using that service automatically.
