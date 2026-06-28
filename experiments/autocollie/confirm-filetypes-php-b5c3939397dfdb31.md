# Confirm PASS — b5c3939397dfdb31 on `filetypes/php`

Cycle `20260628T080745-confirm-b5c3939397dfdb31` — 2026-06-28T08:07:45Z

PR_AUC held across 3 seeds (orig 0.9878)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b5c3939397dfdb31` | `bd0f79ed8e46d2d8` | `bd0f79ed8e46d2d8` | `bd0f79ed8e46d2d8` |
| PR AUC | 0.9878 | 0.9846 | 0.9853 | 0.9862 |
| ROC AUC | 0.9956 | 0.9958 | 0.9960 | 0.9960 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b5c3939397dfdb31
```
