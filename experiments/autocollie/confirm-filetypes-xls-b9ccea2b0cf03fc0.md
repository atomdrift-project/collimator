# Confirm PASS — b9ccea2b0cf03fc0 on `filetypes/xls`

Cycle `20260526T174219-confirm-b9ccea2b0cf03fc0` — 2026-05-26T17:42:19Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b9ccea2b0cf03fc0` | `3fd51891edff5254` | `3fd51891edff5254` | `3fd51891edff5254` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.9879 | 0.9887 | 0.9864 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b9ccea2b0cf03fc0
```
