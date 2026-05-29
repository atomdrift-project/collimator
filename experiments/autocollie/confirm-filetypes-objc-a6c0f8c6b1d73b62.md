# Confirm PASS — a6c0f8c6b1d73b62 on `filetypes/objc`

Cycle `20260527T072511-confirm-a6c0f8c6b1d73b62` — 2026-05-27T07:25:11Z

PR_AUC held across 3 seeds (orig 0.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a6c0f8c6b1d73b62` | `470b0d0abd85b0bc` | `470b0d0abd85b0bc` | `470b0d0abd85b0bc` |
| PR AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ROC AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a6c0f8c6b1d73b62
```
