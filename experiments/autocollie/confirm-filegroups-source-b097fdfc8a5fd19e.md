# Confirm PASS — b097fdfc8a5fd19e on `filegroups/source`

Cycle `20260601T143535-confirm-b097fdfc8a5fd19e` — 2026-06-01T14:35:35Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b097fdfc8a5fd19e` | `6f2cff0f4f41bd38` | `6f2cff0f4f41bd38` | `6f2cff0f4f41bd38` |
| PR AUC | 0.9990 | 0.9986 | 0.9986 | 0.9985 |
| ROC AUC | 0.9982 | 0.9977 | 0.9977 | 0.9975 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b097fdfc8a5fd19e
```
