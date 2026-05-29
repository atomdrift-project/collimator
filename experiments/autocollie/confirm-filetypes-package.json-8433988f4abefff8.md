# Confirm PASS — 8433988f4abefff8 on `filetypes/package.json`

Cycle `20260526T172225-confirm-8433988f4abefff8` — 2026-05-26T17:22:25Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8433988f4abefff8` | `116ab1d39ef4e9a8` | `116ab1d39ef4e9a8` | `116ab1d39ef4e9a8` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9996 |
| ROC AUC | 0.9996 | 0.9997 | 0.9995 | 0.9991 |
| Recall@3FPM | — | 0.9563 | 0.9678 | 0.9660 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8433988f4abefff8
```
