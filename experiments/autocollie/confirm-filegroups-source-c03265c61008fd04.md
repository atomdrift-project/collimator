# Confirm PASS — c03265c61008fd04 on `filegroups/source`

Cycle `20260613T183048-confirm-c03265c61008fd04` — 2026-06-13T18:30:48Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c03265c61008fd04` | `188b379f99798867` | `188b379f99798867` | `188b379f99798867` |
| PR AUC | 0.9991 | 0.9967 | 0.9967 | 0.9966 |
| ROC AUC | 0.9983 | 0.9961 | 0.9961 | 0.9961 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c03265c61008fd04
```
