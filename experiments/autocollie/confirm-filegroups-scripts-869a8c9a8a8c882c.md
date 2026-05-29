# Confirm PASS — 869a8c9a8a8c882c on `filegroups/scripts`

Cycle `20260526T042853-confirm-869a8c9a8a8c882c` — 2026-05-26T04:28:53Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `869a8c9a8a8c882c` | `c4079c88a61fb8be` | `c4079c88a61fb8be` | `c4079c88a61fb8be` |
| PR AUC | 0.9978 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9977 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.7795 | 0.8282 | 0.6939 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=869a8c9a8a8c882c
```
