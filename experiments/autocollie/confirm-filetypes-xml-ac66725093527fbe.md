# Confirm PASS — ac66725093527fbe on `filetypes/xml`

Cycle `20260526T195235-confirm-ac66725093527fbe` — 2026-05-26T19:52:35Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ac66725093527fbe` | `2da9d3370047ca4d` | `2da9d3370047ca4d` | `2da9d3370047ca4d` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ac66725093527fbe
```
