# Confirm PASS — 71f9b035f44e125e on `filetypes/perl`

Cycle `20260526T194037-confirm-71f9b035f44e125e` — 2026-05-26T19:40:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `71f9b035f44e125e` | `766b51b38748e5ef` | `766b51b38748e5ef` | `766b51b38748e5ef` |
| PR AUC | 1.0000 | 0.9924 | 0.9959 | 0.9924 |
| ROC AUC | 1.0000 | 0.9992 | 0.9996 | 0.9992 |
| Recall@3FPM | — | 0.9524 | 0.9524 | 0.9524 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=71f9b035f44e125e
```
