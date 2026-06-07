# Confirm PASS — 956e522f2c6a5ae2 on `filegroups/scripts`

Cycle `20260606T151648-confirm-956e522f2c6a5ae2` — 2026-06-06T15:16:48Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `956e522f2c6a5ae2` | `45c79bf81d382e9f` | `45c79bf81d382e9f` | `45c79bf81d382e9f` |
| PR AUC | 0.9981 | 0.9985 | 0.9985 | 0.9985 |
| ROC AUC | 0.9979 | 0.9981 | 0.9980 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=956e522f2c6a5ae2
```
