# Confirm PASS — b097fdfc8a5fd19e on `filegroups/source`

Cycle `20260606T133645-confirm-b097fdfc8a5fd19e` — 2026-06-06T13:36:45Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b097fdfc8a5fd19e` | `6ca896fc955dcc33` | `6ca896fc955dcc33` | `6ca896fc955dcc33` |
| PR AUC | 0.9990 | 0.9985 | 0.9984 | 0.9984 |
| ROC AUC | 0.9982 | 0.9979 | 0.9977 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b097fdfc8a5fd19e
```
