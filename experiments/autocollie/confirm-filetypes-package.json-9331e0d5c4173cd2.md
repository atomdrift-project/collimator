# Confirm PASS — 9331e0d5c4173cd2 on `filetypes/package.json`

Cycle `20260526T180936-confirm-9331e0d5c4173cd2` — 2026-05-26T18:09:36Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9331e0d5c4173cd2` | `940405eeee7167f8` | `940405eeee7167f8` | `940405eeee7167f8` |
| PR AUC | 0.9998 | 0.9999 | 0.9998 | 0.9996 |
| ROC AUC | 0.9996 | 0.9998 | 0.9997 | 0.9992 |
| Recall@3FPM | — | 0.9665 | 0.9673 | 0.9678 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9331e0d5c4173cd2
```
