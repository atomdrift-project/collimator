# Confirm PASS — f9bf3522cd7221f6 on `filegroups/scripts`

Cycle `20260526T051530-confirm-f9bf3522cd7221f6` — 2026-05-26T05:15:30Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f9bf3522cd7221f6` | `fa6be051c8b0809c` | `fa6be051c8b0809c` | `fa6be051c8b0809c` |
| PR AUC | 0.9978 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9976 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.7296 | 0.7323 | 0.7501 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f9bf3522cd7221f6
```
