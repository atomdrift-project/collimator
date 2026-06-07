# Confirm PASS — e67b060e5bcc3a6a on `filegroups/scripts`

Cycle `20260606T154050-confirm-e67b060e5bcc3a6a` — 2026-06-06T15:40:50Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `f0310ae5577896bb` | `f0310ae5577896bb` | `f0310ae5577896bb` |
| PR AUC | 0.9979 | 0.9986 | 0.9986 | 0.9986 |
| ROC AUC | 0.9977 | 0.9982 | 0.9982 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e67b060e5bcc3a6a
```
