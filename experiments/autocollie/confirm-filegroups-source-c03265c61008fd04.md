# Confirm PASS — c03265c61008fd04 on `filegroups/source`

Cycle `20260606T145959-confirm-c03265c61008fd04` — 2026-06-06T14:59:59Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c03265c61008fd04` | `633ab7d09268e0ce` | `633ab7d09268e0ce` | `633ab7d09268e0ce` |
| PR AUC | 0.9991 | 0.9986 | 0.9984 | 0.9985 |
| ROC AUC | 0.9983 | 0.9980 | 0.9977 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c03265c61008fd04
```
