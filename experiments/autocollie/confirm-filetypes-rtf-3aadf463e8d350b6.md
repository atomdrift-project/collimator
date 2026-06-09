# Confirm PASS — 3aadf463e8d350b6 on `filetypes/rtf`

Cycle `20260609T053711-confirm-3aadf463e8d350b6` — 2026-06-09T05:37:11Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3aadf463e8d350b6` | `12e00a09a0b1f7cd` | `12e00a09a0b1f7cd` | `12e00a09a0b1f7cd` |
| PR AUC | 0.9996 | 0.9996 | 0.9997 | 0.9998 |
| ROC AUC | 0.9969 | 0.9970 | 0.9978 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3aadf463e8d350b6
```
