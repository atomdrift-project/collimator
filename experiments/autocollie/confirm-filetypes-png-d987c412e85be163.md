# Confirm PASS — d987c412e85be163 on `filetypes/png`

Cycle `20261029T030002-confirm-d987c412e85be163` — 2026-10-29T03:00:02Z

PR_AUC held across 3 seeds (orig 0.9617)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d987c412e85be163` | `20a820b26696738e` | `20a820b26696738e` | `20a820b26696738e` |
| PR AUC | 0.9617 | 0.9692 | 0.9702 | 0.9708 |
| ROC AUC | 0.9898 | 0.9920 | 0.9931 | 0.9921 |
| Recall@L50 | — | 0.5276 | 0.4360 | 0.5088 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d987c412e85be163
```
