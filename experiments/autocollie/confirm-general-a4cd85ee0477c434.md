# Confirm PASS — a4cd85ee0477c434 on `general`

Cycle `20260528T013212-confirm-a4cd85ee0477c434` — 2026-05-28T01:32:12Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a4cd85ee0477c434` | `7d2b23f980972c43` | `7d2b23f980972c43` | `7d2b23f980972c43` |
| PR AUC | 0.9986 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9987 | 0.9995 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.6317 | 0.6466 | 0.6042 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a4cd85ee0477c434
```
