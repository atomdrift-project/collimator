# Confirm PASS — 1c3b3831d0898590 on `general`

Cycle `20260530T190723-confirm-1c3b3831d0898590` — 2026-05-30T19:07:23Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1c3b3831d0898590` | `5680971aac58e87e` | `5680971aac58e87e` | `5680971aac58e87e` |
| PR AUC | 0.9998 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9995 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.5438 | 0.5705 | 0.5860 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1c3b3831d0898590
```
