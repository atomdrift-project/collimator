# Confirm PASS — 8daced550c7b61df on `filegroups/documents`

Cycle `20260523T204320-confirm-8daced550c7b61df` — 2026-05-23T20:43:20Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8daced550c7b61df` | `cd5db1b958632cc4` | `cd5db1b958632cc4` | `cd5db1b958632cc4` |
| PR AUC | 1.0000 | 0.9996 | 0.9996 | 0.9995 |
| ROC AUC | 0.9985 | 0.9668 | 0.9679 | 0.9599 |
| Recall@3FPM | — | 0.7039 | 0.7039 | 0.6532 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8daced550c7b61df
```
