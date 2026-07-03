# Confirm PASS — eb5684e12cb37776 on `filegroups/native`

Cycle `20260703T030129-confirm-eb5684e12cb37776` — 2026-07-03T03:01:29Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eb5684e12cb37776` | `bdf70b455a3e2db2` | `bdf70b455a3e2db2` | `bdf70b455a3e2db2` |
| PR AUC | 0.9989 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9989 | 0.9976 | 0.9977 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eb5684e12cb37776
```
