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
