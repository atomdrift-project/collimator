# Confirm PASS — 956e522f2c6a5ae2 on `filegroups/scripts`

Cycle `20260525T074031-confirm-956e522f2c6a5ae2` — 2026-05-25T07:40:31Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `956e522f2c6a5ae2` | `4b4b4b572ed39a36` | `4b4b4b572ed39a36` | `4b4b4b572ed39a36` |
| PR AUC | 0.9981 | 0.9993 | 0.9992 | 0.9992 |
| ROC AUC | 0.9979 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.6830 | 0.6876 | 0.7201 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=956e522f2c6a5ae2
```
