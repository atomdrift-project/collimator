# Confirm PASS — 53d95921fb387b22 on `filetypes/png`

Cycle `20260525T211442-confirm-53d95921fb387b22` — 2026-05-25T21:14:42Z

PR_AUC held across 3 seeds (orig 0.9838)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `53d95921fb387b22` | `ddbea59e76bf3375` | `ddbea59e76bf3375` | `ddbea59e76bf3375` |
| PR AUC | 0.9838 | 0.9698 | 0.9804 | 0.9834 |
| ROC AUC | 0.9692 | 0.9496 | 0.9601 | 0.9663 |
| Recall@3FPM | — | 0.9231 | 0.9231 | 0.9231 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=53d95921fb387b22
```
