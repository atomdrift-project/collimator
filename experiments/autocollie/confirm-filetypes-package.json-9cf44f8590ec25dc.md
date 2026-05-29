# Confirm PASS — 9cf44f8590ec25dc on `filetypes/package.json`

Cycle `20260526T183041-confirm-9cf44f8590ec25dc` — 2026-05-26T18:30:41Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9cf44f8590ec25dc` | `ddacf34629937b8a` | `ddacf34629937b8a` | `ddacf34629937b8a` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9996 |
| ROC AUC | 0.9995 | 0.9996 | 0.9995 | 0.9990 |
| Recall@3FPM | — | 0.9603 | 0.9678 | 0.9691 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9cf44f8590ec25dc
```
