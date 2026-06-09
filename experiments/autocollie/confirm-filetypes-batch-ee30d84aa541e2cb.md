# Confirm PASS — ee30d84aa541e2cb on `filetypes/batch`

Cycle `20260609T102815-confirm-ee30d84aa541e2cb` — 2026-06-09T10:28:15Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ee30d84aa541e2cb` | `995496f3ac0b383e` | `995496f3ac0b383e` | `995496f3ac0b383e` |
| PR AUC | 0.9996 | 0.9997 | 0.9997 | 0.9996 |
| ROC AUC | 0.9972 | 0.9975 | 0.9977 | 0.9967 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ee30d84aa541e2cb
```
