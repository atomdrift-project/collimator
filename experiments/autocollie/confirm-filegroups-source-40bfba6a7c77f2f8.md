# Confirm PASS — 40bfba6a7c77f2f8 on `filegroups/source`

Cycle `20260525T024201-confirm-40bfba6a7c77f2f8` — 2026-05-25T02:42:01Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `40bfba6a7c77f2f8` | `758b3d7304b3fdc6` | `758b3d7304b3fdc6` | `758b3d7304b3fdc6` |
| PR AUC | 0.9987 | 0.9991 | 0.9990 | 0.9991 |
| ROC AUC | 0.9980 | 0.9983 | 0.9982 | 0.9983 |
| Recall@3FPM | — | 0.9178 | 0.9288 | 0.9181 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=40bfba6a7c77f2f8
```
