# Confirm PASS — d165ae74ced07286 on `filegroups/native`

Cycle `20260606T061228-confirm-d165ae74ced07286` — 2026-06-06T06:12:28Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d165ae74ced07286` | `e73c3a418ad62e60` | `e73c3a418ad62e60` | `e73c3a418ad62e60` |
| PR AUC | 0.9994 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d165ae74ced07286
```
