# Construction Data Investigation

## Goal

Figure out whether the Hoboken construction updates can be accessed automatically and turned into a reliable map layer.

Source: https://www.hobokennj.gov/hoboken-construction-updates

## What I Found

The page has useful details such as project names, affected streets, road closures, no-parking rules, work hours, detours, and short descriptions. The page says the schedule can change because of weather and construction logistics.

The difficult part is that the details are written as sections and bullet points on a webpage. They are not returned as one clean JSON table like Citi Bike. A single project can also list several streets, dates, and different impacts.

I manually entered a few rows in `data/construction_layer.csv` to test the fields and map display. The latitude and longitude values are approximate points near the affected street segments, not official construction coordinates.

