# Confirm PASS — e0e2633b4afa7d21 on `filetypes/package.json`

Cycle `20260526T171446-confirm-e0e2633b4afa7d21` — 2026-05-26T17:14:46Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e0e2633b4afa7d21` | `5ed8e12ca3a0ceb6` | `5ed8e12ca3a0ceb6` | `5ed8e12ca3a0ceb6` |
| PR AUC | 0.9996 | 0.9998 | 0.9998 | 0.9995 |
| ROC AUC | 0.9991 | 0.9997 | 0.9995 | 0.9989 |
| Recall@3FPM | — | 0.9695 | 0.9700 | 0.9687 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e0e2633b4afa7d21
```
