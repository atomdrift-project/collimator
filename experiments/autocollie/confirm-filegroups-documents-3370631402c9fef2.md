# Confirm PASS — 3370631402c9fef2 on `filegroups/documents`

Cycle `20260528T114411-confirm-3370631402c9fef2` — 2026-05-28T11:44:11Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3370631402c9fef2` | `75faf49da5fc2eab` | `75faf49da5fc2eab` | `75faf49da5fc2eab` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9997 | 0.9998 | 0.9997 |
| Recall@3FPM | — | 0.9743 | 0.9867 | 0.9818 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3370631402c9fef2
```
