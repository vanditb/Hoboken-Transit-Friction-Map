# Friction Score Notes

This is the first simple version of the scoring idea.

## Current Baseline

The overall project idea is:

```text
friction score = bike friction + weather friction + construction friction + transit friction
```

For v0, the app starts with bike friction only.

## Bike Friction Idea

The important thing is that "friction" depends on what someone is trying to do.

If someone is already in an area, they probably care more about whether there are bikes available. If they are coming into an area, they probably care more about whether there are docks available.

This connects to a future toggle idea from Professor Odonkor:

- already in area: need a bike
- coming into area: need a dock

For now, the score should be simple and explainable instead of trying to be too advanced.

## V0 Scoring

Use station capacity when available.

Already in area bike friction:

```text
bike friction = 100 * (1 - bikes_available / capacity)
```

Coming into area dock friction:

```text
dock friction = 100 * (1 - docks_available / capacity)
```

Rules:

- if a station is offline, friction should be 100
- clamp scores between 0 and 100
- if capacity is missing or 0, handle it safely
- if data is missing, mark the station as unknown instead of making up a value

This gives a simple first score where 0 means low friction and 100 means high friction.
