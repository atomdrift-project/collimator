# Confirm PASS — 5808fc0fa5be621e on `filetypes/java`

Cycle `20260715T053833-confirm-5808fc0fa5be621e` — 2026-07-15T05:38:33Z

PR_AUC held across 3 seeds (orig 0.9351)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5808fc0fa5be621e` | `03bea2611dca69c3` | `03bea2611dca69c3` | `03bea2611dca69c3` |
| PR AUC | 0.9351 | 0.9436 | 0.9329 | 0.9179 |
| ROC AUC | 0.9900 | 0.9946 | 0.9877 | 0.9895 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5808fc0fa5be621e
```
