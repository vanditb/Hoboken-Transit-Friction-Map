# Historical Data Collection

## Why This Is Needed

The live Citi Bike feed only shows what is happening now. To predict whether a station will run low on bikes or docks in the next hour, I need repeated snapshots over time.

## Run Once

```bash
python3 scripts/collect_snapshot.py --once
```

## Run Every 15 Minutes

```bash
python3 scripts/collect_snapshot.py --loop --interval-minutes 15
```

Press `Ctrl+C` to stop the loop cleanly.

## What Gets Saved

Daily CSV files are written to `data/history/YYYY-MM-DD.csv`. Each row contains station availability, station location, the near-term weather fields, weather friction, and the nearest eligible construction distance when available.

The collector checks for duplicate station and timestamp pairs before writing. If Citi Bike fails, it does not write a partial snapshot. If weather fails but Citi Bike works, it saves the station data with blank weather fields and writes a local error log.

## Important Limitation

This only collects while the script is running. If the laptop sleeps, closes, loses internet, or the process stops, those snapshots will be missing. The history folder is ignored by Git so real collected data is not pushed into the repository.
