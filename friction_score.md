# Friction Score Notes

The scoring is supposed to stay simple enough that I can explain why a station received its score.

## Overall Idea

The longer-term baseline is:

```text
friction score = bike friction + weather friction + construction friction + transit friction
```

The original v0 used bike friction only. The current baseline combines bike and weather:

```text
overall friction = 0.7 * bike friction + 0.3 * weather friction
```

This is a first simple weighting system, not final. The weights are just a starting point so the app can show how weather changes the friction score.

## Baseline and Experimental Scores

The baseline stays the same:

```text
baseline = 0.70 * bike friction + 0.30 * weather friction
```

There is also an optional experimental score:

```text
experimental = 0.60 * bike friction + 0.20 * weather friction + 0.20 * construction friction
```

These are prototype assumptions, not validated scientific weights. If weather or another component is unavailable, the app renormalizes the weights across the components that are available.

## Bike Friction

Professor Odonkor suggested a future toggle based on what the user is trying to do:

- already in the area: cares more about available bikes
- coming into the area: cares more about available docks, parking, or access into the area

Already in area:

```text
bike friction = 100 * (1 - bikes available / capacity)
```

Coming into area:

```text
dock friction = 100 * (1 - docks available / capacity)
```

An offline station gets 100. Missing or zero capacity is treated as unknown, and all scores are clamped from 0 to 100.

## Weather Friction

The app starts at 10 for normal conditions and adds points for forecast words, wind, and uncomfortable temperatures.

- normal weather: low friction
- rain, strong wind, or uncomfortable heat/cold: medium friction
- storm, heavy rain, snow, or weather alerts: high friction

This logic is intentionally rough. It uses the first NWS forecast period and still needs feedback on which weather conditions matter most for Hoboken movement.

## Construction Friction

The first idea is:

- no construction nearby: low friction
- nearby construction or no parking: medium friction
- road closure, full closure, or detour: high friction

Construction is shown as a separate reviewed visual layer. It supports point projects and line/corridor impacts. The baseline score does not use it, but the experimental option can use it.

For the experiment, construction friction uses a project severity and projected distance in meters:

```text
distance decay = max(0, 1 - distance_m / 300)
construction friction = 100 * severity factor * distance decay
```

- low = 0.25
- medium = 0.50
- high = 0.75
- severe = 1.00

The effect is strongest within 50 meters and reaches zero after 300 meters. Expired and unverified projects do not affect the score. The impact-mode filter also has to match.

The construction geometry is still not official construction geometry. The map can road-snap the approximate anchors to OpenStreetMap streets for display, but that remains an approximation. Future work should compare this distance method with verified city GIS geometry and get feedback before treating it as a research result.

## Future Validation

The next validation step is to collect station snapshots, then check whether stations near verified active impacts actually have different availability patterns. The weights should be adjusted only after there is enough history to compare them.

## Fallback

If weather is unavailable, the app uses bike friction by itself and says that clearly. It does not make up weather data.
