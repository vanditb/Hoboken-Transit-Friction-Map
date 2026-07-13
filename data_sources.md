# Data Sources

This is my working source inventory. The statuses describe what is actually being used or tested, not what I hope to add later.

| Source | Link | What it gives | Type | Access difficulty | Friction use | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Citi Bike station information | https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json | Station IDs, names, coordinates, and capacity | Changing slowly | Easy public JSON | Gives station location and capacity for the bike score | Tested / works in app |
| Citi Bike station status | https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json | Available bikes, docks, and operating status | Live | Easy public JSON | Low bike or dock availability raises bike friction | Tested / works in app |
| National Weather Service API | https://www.weather.gov/documentation/services-web-api | Forecast periods with temperature, conditions, and wind | Live forecast | Easy public API with User-Agent | Rain, snow, wind, and extreme temperatures raise weather friction | Tested / works; now integrated |
| Hoboken construction updates | https://www.hobokennj.gov/hoboken-construction-updates | Current projects, road closures, no-parking areas, closure hours, and affected streets | Weekly/changing webpage | Medium; no clean API found yet | Nearby construction could be medium; closures and detours could be high | Investigating; first version manually extracted to CSV |
| Hoboken Mapping Hub | https://hoboken-mapping-hub-cityofhoboken.hub.arcgis.com/ | Possible public GIS maps and downloadable city layers | Depends on layer | Medium | Could provide more reliable geometry for projects or street impacts | Investigating / possible GIS layers |
| OpenStreetMap | https://www.openstreetmap.org/ | Roads, paths, bike lanes, sidewalks, and amenities | Community-maintained | Easy public data | Adds street context and could support distance-to-impact calculations | Planned |
