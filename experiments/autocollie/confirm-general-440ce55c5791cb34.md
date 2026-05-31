# Confirm PASS — 440ce55c5791cb34 on `general`

Cycle `20260530T160430-confirm-440ce55c5791cb34` — 2026-05-30T16:04:30Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `440ce55c5791cb34` | `db70f6911d71f337` | `db70f6911d71f337` | `db70f6911d71f337` |
| PR AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9997 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.6372 | 0.6940 | 0.6873 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=440ce55c5791cb34
```
