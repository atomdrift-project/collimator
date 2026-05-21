# Confirm PASS — 0d1e6d95d9a9871f on `filegroups/portable`

Cycle `20260521T035824-confirm-0d1e6d95d9a9871f` — 2026-05-21T03:58:24Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0d1e6d95d9a9871f` | `b5c995537519c26b` | `b5c995537519c26b` | `b5c995537519c26b` |
| PR AUC | 0.9968 | 0.9942 | 0.9959 | 0.9963 |
| ROC AUC | 0.9992 | 0.9987 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.5867 | 0.7733 | 0.8533 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0d1e6d95d9a9871f
```
