# Confirm PASS — 578f9d98aec938b0 on `filetypes/pe`

Cycle `20260808T224819-confirm-578f9d98aec938b0` — 2026-08-08T22:48:19Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `578f9d98aec938b0` | `a446f344ea24bbb8` | `a446f344ea24bbb8` | `a446f344ea24bbb8` |
| PR AUC | 0.9989 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9997 | 0.9997 | 0.9997 |
| Recall@L50 | — | 0.6680 | 0.7668 | 0.5281 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=578f9d98aec938b0
```
