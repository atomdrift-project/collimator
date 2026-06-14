# Confirm PASS — e37f927afbd32e67 on `filegroups/scripts`

Cycle `20260613T190738-confirm-e37f927afbd32e67` — 2026-06-13T19:07:38Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e37f927afbd32e67` | `bd6c7568313c5192` | `bd6c7568313c5192` | `bd6c7568313c5192` |
| PR AUC | 0.9970 | 0.9972 | 0.9972 | 0.9973 |
| ROC AUC | 0.9964 | 0.9968 | 0.9968 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e37f927afbd32e67
```
