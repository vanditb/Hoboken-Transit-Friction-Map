# First Prediction Plan

The first prediction question should be specific: will a Citi Bike station have two or fewer bikes, or two or fewer docks, about one hour from now?

That is stronger than asking an LLM to invent one friction score. A normal model can learn from station history, time of day, weather, and later construction context. An LLM could eventually help explain a model result in plain language, but it should not make up the numeric prediction.

The first notebook uses snapshots collected by this project and compares a simple persistence baseline with small CPU-friendly models. It uses a time-based split because future data should not leak into the past.

Longer-term prediction would need more history and better construction schedules. Colab is useful for convenience and sharing experiments, not because this first model needs a GPU.
