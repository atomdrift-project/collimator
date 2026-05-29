# Confirm PASS — f20041fa3a244200 on `filetypes/data`

Cycle `20260526T211719-confirm-f20041fa3a244200` — 2026-05-26T21:17:19Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f20041fa3a244200` | `f299942cb13d14f4` | `f299942cb13d14f4` | `f299942cb13d14f4` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f20041fa3a244200
```
