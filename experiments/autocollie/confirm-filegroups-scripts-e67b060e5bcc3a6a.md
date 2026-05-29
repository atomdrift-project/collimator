# Confirm PASS — e67b060e5bcc3a6a on `filegroups/scripts`

Cycle `20260525T184633-confirm-e67b060e5bcc3a6a` — 2026-05-25T18:46:33Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `2b909e7b127047e7` | `2b909e7b127047e7` | `2b909e7b127047e7` |
| PR AUC | 0.9979 | 0.9993 | 0.9992 | 0.9993 |
| ROC AUC | 0.9977 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.7542 | 0.8201 | 0.7580 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e67b060e5bcc3a6a
```
