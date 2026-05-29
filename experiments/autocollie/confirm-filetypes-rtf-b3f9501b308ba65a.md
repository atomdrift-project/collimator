# Confirm PASS — b3f9501b308ba65a on `filetypes/rtf`

Cycle `20260527T073211-confirm-b3f9501b308ba65a` — 2026-05-27T07:32:11Z

PR_AUC held across 3 seeds (orig 0.9780)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b3f9501b308ba65a` | `50f886d215f794ab` | `50f886d215f794ab` | `50f886d215f794ab` |
| PR AUC | 0.9780 | 0.9784 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b3f9501b308ba65a
```
