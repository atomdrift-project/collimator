# Confirm PASS — 284d75b298227636 on `filetypes/go`

Cycle `20260706T030139-confirm-284d75b298227636` — 2026-07-06T03:01:39Z

PR_AUC held across 3 seeds (orig 0.9546)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `284d75b298227636` | `4e2d6be5868f3c30` | `4e2d6be5868f3c30` | `4e2d6be5868f3c30` |
| PR AUC | 0.9546 | 0.9522 | 0.9472 | 0.9526 |
| ROC AUC | 0.9770 | 0.9757 | 0.9741 | 0.9765 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=284d75b298227636
```
