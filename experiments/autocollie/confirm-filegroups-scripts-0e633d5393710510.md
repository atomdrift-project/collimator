# Confirm PASS — 0e633d5393710510 on `filegroups/scripts`

Cycle `20260526T052754-confirm-0e633d5393710510` — 2026-05-26T05:27:54Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0e633d5393710510` | `dcc8873581e85f3b` | `dcc8873581e85f3b` | `dcc8873581e85f3b` |
| PR AUC | 0.9978 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9977 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.7447 | 0.7870 | 0.7633 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0e633d5393710510
```
