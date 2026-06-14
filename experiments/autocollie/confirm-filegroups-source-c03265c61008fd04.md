# Confirm PASS — c03265c61008fd04 on `filegroups/source`

Cycle `20260614T201156-confirm-c03265c61008fd04` — 2026-06-14T20:11:56Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c03265c61008fd04` | `a42cb9796a825a68` | `a42cb9796a825a68` | `a42cb9796a825a68` |
| PR AUC | 0.9991 | 0.9977 | 0.9977 | 0.9977 |
| ROC AUC | 0.9983 | 0.9973 | 0.9974 | 0.9973 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c03265c61008fd04
```
