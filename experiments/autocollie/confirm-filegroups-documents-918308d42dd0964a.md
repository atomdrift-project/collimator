# Confirm PASS — 918308d42dd0964a on `filegroups/documents`

Cycle `20260523T172445-confirm-918308d42dd0964a` — 2026-05-23T17:24:45Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `918308d42dd0964a` | `f6fc01da1e63b1d0` | `f6fc01da1e63b1d0` | `f6fc01da1e63b1d0` |
| PR AUC | 1.0000 | 0.9986 | 0.9986 | 0.9986 |
| ROC AUC | 0.9987 | 0.8989 | 0.8989 | 0.8989 |
| Recall@3FPM | — | 0.5075 | 0.5075 | 0.5075 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=918308d42dd0964a
```
