# Confirm PASS — 59606d768307469f on `filetypes/xml`

Cycle `20260715T044847-confirm-59606d768307469f` — 2026-07-15T04:48:47Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `59606d768307469f` | `897074a9400f7f84` | `897074a9400f7f84` | `897074a9400f7f84` |
| PR AUC | 1.0000 | 0.9990 | 0.9976 | 0.9995 |
| ROC AUC | 1.0000 | 0.9997 | 0.9993 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=59606d768307469f
```
