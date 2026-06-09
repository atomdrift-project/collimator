# Confirm PASS — 9445b9b1b5c81388 on `filetypes/c`

Cycle `20260609T162818-confirm-9445b9b1b5c81388` — 2026-06-09T16:28:18Z

PR_AUC held across 3 seeds (orig 0.9848)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9445b9b1b5c81388` | `c9db1b6fe94498d8` | `c9db1b6fe94498d8` | `c9db1b6fe94498d8` |
| PR AUC | 0.9848 | 0.9847 | 0.9838 | 0.9848 |
| ROC AUC | 0.9928 | 0.9929 | 0.9922 | 0.9926 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9445b9b1b5c81388
```
