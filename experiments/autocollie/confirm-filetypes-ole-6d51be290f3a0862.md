# Confirm PASS — 6d51be290f3a0862 on `filetypes/ole`

Cycle `20260606T014454-confirm-6d51be290f3a0862` — 2026-06-06T01:44:54Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6d51be290f3a0862` | `b2d33c27cbac5d96` | `b2d33c27cbac5d96` | `b2d33c27cbac5d96` |
| PR AUC | 0.9979 | 0.9978 | 0.9971 | 0.9978 |
| ROC AUC | 0.9974 | 0.9973 | 0.9965 | 0.9972 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6d51be290f3a0862
```
