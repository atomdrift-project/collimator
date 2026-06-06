# Confirm PASS — 9937b0fe64a93bce on `filegroups/scripts`

Cycle `20260606T075739-confirm-9937b0fe64a93bce` — 2026-06-06T07:57:39Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9937b0fe64a93bce` | `d1d79b588536aa2b` | `d1d79b588536aa2b` | `d1d79b588536aa2b` |
| PR AUC | 0.9970 | 0.9989 | 0.9989 | 0.9989 |
| ROC AUC | 0.9964 | 0.9985 | 0.9985 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9937b0fe64a93bce
```
