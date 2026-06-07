# Confirm PASS — b0d6f9295501a29b on `filegroups/scripts`

Cycle `20260606T135136-confirm-b0d6f9295501a29b` — 2026-06-06T13:51:36Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b0d6f9295501a29b` | `3671e424e0c1729a` | `3671e424e0c1729a` | `3671e424e0c1729a` |
| PR AUC | 0.9978 | 0.9987 | 0.9987 | 0.9987 |
| ROC AUC | 0.9976 | 0.9983 | 0.9983 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b0d6f9295501a29b
```
