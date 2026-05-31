# Confirm PASS — 88e86b9befcc8c30 on `general`

Cycle `20260530T221153-confirm-88e86b9befcc8c30` — 2026-05-30T22:11:53Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `88e86b9befcc8c30` | `86988e8c29120326` | `86988e8c29120326` | `86988e8c29120326` |
| PR AUC | 0.9996 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9995 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.6083 | 0.6649 | 0.6936 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=88e86b9befcc8c30
```
