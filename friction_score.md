# Friction Score Notes

The scoring is supposed to stay simple enough that I can explain why a station received its score.

## Overall Idea

The longer-term baseline is:

```text
friction score = bike friction + weather friction + construction friction + transit friction
```

The original v0 used bike friction only. The current v1 idea starts combining bike and weather:

```text
overall friction = 0.7 * bike friction + 0.3 * weather friction
```

This is a first simple weighting system, not final. The weights are just a starting point so the app can show how weather changes the friction score.

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
