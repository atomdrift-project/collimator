# Confirm PASS — 956e522f2c6a5ae2 on `filegroups/scripts`

Cycle `20260704T081709-confirm-956e522f2c6a5ae2` — 2026-07-04T08:17:09Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `956e522f2c6a5ae2` | `34eee463147e0095` | `34eee463147e0095` | `34eee463147e0095` |
| PR AUC | 0.9981 | 0.9931 | 0.9931 | 0.9932 |
| ROC AUC | 0.9979 | 0.9941 | 0.9941 | 0.9942 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=956e522f2c6a5ae2
```
