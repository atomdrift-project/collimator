# Confirm PASS — 93f42142e90e8cf0 on `filegroups/config`

Cycle `20260704T125212-confirm-93f42142e90e8cf0` — 2026-07-04T12:52:12Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `93f42142e90e8cf0` | `73b9344f5857c159` | `73b9344f5857c159` | `73b9344f5857c159` |
| PR AUC | 0.9998 | 0.9980 | 0.9980 | 0.9981 |
| ROC AUC | 0.9996 | 0.9980 | 0.9980 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=93f42142e90e8cf0
```
