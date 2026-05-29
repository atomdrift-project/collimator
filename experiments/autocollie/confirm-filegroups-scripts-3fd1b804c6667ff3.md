# Confirm PASS — 3fd1b804c6667ff3 on `filegroups/scripts`

Cycle `20260526T044519-confirm-3fd1b804c6667ff3` — 2026-05-26T04:45:19Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3fd1b804c6667ff3` | `f682ac9c385c7e80` | `f682ac9c385c7e80` | `f682ac9c385c7e80` |
| PR AUC | 0.9977 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9975 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.8194 | 0.8415 | 0.7474 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3fd1b804c6667ff3
```
