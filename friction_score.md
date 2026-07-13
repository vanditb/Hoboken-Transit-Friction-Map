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
