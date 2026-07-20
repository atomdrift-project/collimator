# Confirm PASS — 777bb72d1657485f on `filetypes/vbs`

Cycle `20260716T105541-confirm-777bb72d1657485f` — 2026-07-16T10:55:41Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `777bb72d1657485f` | `c013b7e95933aa04` | `c013b7e95933aa04` | `c013b7e95933aa04` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9971 | 0.9966 | 0.9970 | 0.9960 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=777bb72d1657485f
```
