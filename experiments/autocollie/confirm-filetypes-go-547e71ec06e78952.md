# Confirm PASS — 547e71ec06e78952 on `filetypes/go`

Cycle `20260628T173432-confirm-547e71ec06e78952` — 2026-06-28T17:34:32Z

PR_AUC held across 3 seeds (orig 0.9214)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `547e71ec06e78952` | `87299b065570518e` | `87299b065570518e` | `87299b065570518e` |
| PR AUC | 0.9214 | 0.9191 | 0.9233 | 0.9212 |
| ROC AUC | 0.9731 | 0.9704 | 0.9722 | 0.9715 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=547e71ec06e78952
```
