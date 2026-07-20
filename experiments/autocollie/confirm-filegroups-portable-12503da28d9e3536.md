# Confirm PASS — 12503da28d9e3536 on `filegroups/portable`

Cycle `20260716T032635-confirm-12503da28d9e3536` — 2026-07-16T03:26:35Z

PR_AUC held across 3 seeds (orig 0.9920)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12503da28d9e3536` | `ec9b93e3c7f21bbe` | `ec9b93e3c7f21bbe` | `ec9b93e3c7f21bbe` |
| PR AUC | 0.9920 | 0.9935 | 0.9926 | 0.9917 |
| ROC AUC | 0.9976 | 0.9983 | 0.9983 | 0.9974 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12503da28d9e3536
```
