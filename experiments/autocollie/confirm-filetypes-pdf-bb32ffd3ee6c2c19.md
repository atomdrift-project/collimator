# Confirm PASS — bb32ffd3ee6c2c19 on `filetypes/pdf`

Cycle `20260601T124433-confirm-bb32ffd3ee6c2c19` — 2026-06-01T12:44:33Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bb32ffd3ee6c2c19` | `10e951bc6357cda1` | `10e951bc6357cda1` | `10e951bc6357cda1` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9993 | 0.9991 | 0.9981 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bb32ffd3ee6c2c19
```
