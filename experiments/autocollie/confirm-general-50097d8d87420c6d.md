# Confirm PASS — 50097d8d87420c6d on `general`

Cycle `20260530T151739-confirm-50097d8d87420c6d` — 2026-05-30T15:17:39Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `50097d8d87420c6d` | `4d461b2c8aa05df8` | `4d461b2c8aa05df8` | `4d461b2c8aa05df8` |
| PR AUC | 0.9988 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9988 | 0.9993 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.6440 | 0.6975 | 0.6742 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=50097d8d87420c6d
```
