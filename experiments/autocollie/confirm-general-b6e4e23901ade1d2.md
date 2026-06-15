# Confirm PASS — b6e4e23901ade1d2 on `general`

Cycle `20260615T081712-confirm-b6e4e23901ade1d2` — 2026-06-15T08:17:12Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b6e4e23901ade1d2` | `7c051c49ad19816e` | `7c051c49ad19816e` | `7c051c49ad19816e` |
| PR AUC | 0.9979 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9978 | 0.9993 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b6e4e23901ade1d2
```
