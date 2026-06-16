# Confirm PASS — 809b93a511734463 on `filetypes/tar`

Cycle `20260616T055954-confirm-809b93a511734463` — 2026-06-16T05:59:54Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `809b93a511734463` | `e9ba6b14b032c066` | `e9ba6b14b032c066` | `e9ba6b14b032c066` |
| PR AUC | 0.9993 | 0.9995 | 0.9997 | 0.9996 |
| ROC AUC | 0.9994 | 0.9996 | 0.9997 | 0.9996 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=809b93a511734463
```
