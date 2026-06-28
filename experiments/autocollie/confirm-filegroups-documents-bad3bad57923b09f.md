# Confirm PASS — bad3bad57923b09f on `filegroups/documents`

Cycle `20260628T103019-confirm-bad3bad57923b09f` — 2026-06-28T10:30:19Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bad3bad57923b09f` | `806400d841b6d288` | `806400d841b6d288` | `806400d841b6d288` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9992 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bad3bad57923b09f
```
