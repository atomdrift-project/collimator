# Confirm PASS — 3a6f1db03980c138 on `general`

Cycle `20260530T025314-confirm-3a6f1db03980c138` — 2026-05-30T02:53:14Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3a6f1db03980c138` | `aac1a08fe0a3b01d` | `aac1a08fe0a3b01d` | `aac1a08fe0a3b01d` |
| PR AUC | 0.9979 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9980 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.5912 | 0.6901 | 0.6857 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3a6f1db03980c138
```
