# Confirm PASS — 57326091ccf12436 on `filetypes/pdf`

Cycle `20260718T135011-confirm-57326091ccf12436` — 2026-07-18T13:50:11Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `57326091ccf12436` | `99f6ff881cbcdb1a` | `99f6ff881cbcdb1a` | `99f6ff881cbcdb1a` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9992 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=57326091ccf12436
```
