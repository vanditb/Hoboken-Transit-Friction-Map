# Construction Data Investigation

## Goal

Figure out whether the Hoboken construction updates can be accessed automatically and turned into a reliable map layer.

Source: https://www.hobokennj.gov/hoboken-construction-updates

## What I Found

The page has useful details such as project names, affected streets, road closures, no-parking rules, work hours, detours, and short descriptions. The page says the schedule can change because of weather and construction logistics.

The difficult part is that the details are written as sections and bullet points on a webpage. They are not returned as one clean JSON table like Citi Bike. A single project can also list several streets, dates, and different impacts.

I manually entered a few rows in `data/construction_layer.csv` to test the fields and map display. The latitude and longitude values are approximate points near the affected street segments, not official construction coordinates.

## Questions

- Is there a public API behind the construction page?
- Is any embedded or linked map using ArcGIS feature layers?
- Can a useful layer be downloaded from the Hoboken Mapping Hub?
- Would scraping this changing webpage be responsible and allowed?
- What fields do we actually need for the research question?
- Should one project with several street impacts become several CSV rows?
- How often would a manual or automated layer need to refresh?

## Current Conclusion

Citi Bike data is clean and already structured for code. Construction data seems less clean and changes in a more human-written format. For the first prototype, a manual CSV is probably the safest way to test the map and decide which fields matter.

Later I can try automated extraction if I find a stable API, ArcGIS layer, or page structure. I should check that direction with Professor Odonkor before spending too much time building a scraper.
