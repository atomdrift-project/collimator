# Confirm PASS — 2d76e27134d2db9e on `filetypes/kotlin`

Cycle `20260713T051949-confirm-2d76e27134d2db9e` — 2026-07-13T05:19:49Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2d76e27134d2db9e` | `85e95fdcd4744a8f` | `85e95fdcd4744a8f` | `85e95fdcd4744a8f` |
| PR AUC | 1.0000 | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9988 | 0.9965 | 0.9989 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2d76e27134d2db9e
```
