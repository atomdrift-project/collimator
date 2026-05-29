# Confirm PASS — b097fdfc8a5fd19e on `filegroups/source`

Cycle `20260528T092105-confirm-b097fdfc8a5fd19e` — 2026-05-28T09:21:05Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b097fdfc8a5fd19e` | `f6c3c2e27d25a516` | `f6c3c2e27d25a516` | `f6c3c2e27d25a516` |
| PR AUC | 0.9990 | 0.9989 | 0.9989 | 0.9990 |
| ROC AUC | 0.9982 | 0.9980 | 0.9980 | 0.9981 |
| Recall@3FPM | — | 0.9337 | 0.9297 | 0.9137 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b097fdfc8a5fd19e
```
