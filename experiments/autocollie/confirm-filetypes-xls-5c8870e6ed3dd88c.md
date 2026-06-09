# Confirm PASS — 5c8870e6ed3dd88c on `filetypes/xls`

Cycle `20260609T004035-confirm-5c8870e6ed3dd88c` — 2026-06-09T00:40:35Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5c8870e6ed3dd88c` | `a361b0d6820a426c` | `a361b0d6820a426c` | `a361b0d6820a426c` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9980 | 0.9984 | 0.9983 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5c8870e6ed3dd88c
```
