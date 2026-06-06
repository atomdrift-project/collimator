# Confirm PASS — 1892b3a81a651262 on `general`

Cycle `20260606T091818-confirm-1892b3a81a651262` — 2026-06-06T09:18:18Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1892b3a81a651262` | `475fe486ea57c6dc` | `475fe486ea57c6dc` | `475fe486ea57c6dc` |
| PR AUC | 0.9984 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9983 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1892b3a81a651262
```
