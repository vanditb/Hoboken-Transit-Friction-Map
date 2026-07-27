# Construction Source Audit

## What I Inspected

I checked the City of Hoboken construction updates page and followed its `Active Construction Projects` link.

Source page: https://www.hobokennj.gov/hoboken-construction-updates

## What Was Found

The city page links to a public ArcGIS Web App called `Active Construction Projects`.

- Web App item: `47966f4b671e4d8686c8cadcbcf580fc`
- Web Map item: `9ba276c14dd144cdb3b6596350c75603`
- Line layer: `https://services8.arcgis.com/LDmC4ZVHdfKcEzxl/arcgis/rest/services/Construction/FeatureServer/0`
- Point layer: `https://services8.arcgis.com/LDmC4ZVHdfKcEzxl/arcgis/rest/services/Construction_Project_Point/FeatureServer/0`

The line layer answered a public query during this audit. It is a polyline layer and includes fields such as responsible party, project name, location description, purpose, description, traffic management, hours, contact, website, and work period. It also returned geometry paths.

## What This Means

There is a better official source than a webpage scraper for project text and map geometry. The current prototype still keeps its manual CSV because it needs reviewable statuses, approximate anchors for road-snapping experiments, and a small stable dataset for testing.

The public service worked during this audit, but I did not yet build an automatic import. The data includes records with missing dates or older-looking information, so it should be checked before treating every returned feature as currently active.

## Recommendation

For the next prototype step, keep the reviewed manual CSV for the score and use the FeatureServer as a verification reference. An automatic importer should only be added after deciding how to identify active versus outdated projects and how to preserve the source text without overwriting manual review notes.
