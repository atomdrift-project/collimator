# Confirm PASS — b660c4e4d0bea14d on `filegroups/source`

Cycle `20260525T183524-confirm-b660c4e4d0bea14d` — 2026-05-25T18:35:24Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b660c4e4d0bea14d` | `7e9252b76aa81f4f` | `7e9252b76aa81f4f` | `7e9252b76aa81f4f` |
| PR AUC | 0.9988 | 0.9991 | 0.9991 | 0.9991 |
| ROC AUC | 0.9981 | 0.9983 | 0.9983 | 0.9984 |
| Recall@3FPM | — | 0.9094 | 0.9162 | 0.9162 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b660c4e4d0bea14d
```
