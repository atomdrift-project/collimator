# Confirm PASS — d82d4e0c91c60f91 on `filetypes/python-bytecode`

Cycle `20260526T225257-confirm-d82d4e0c91c60f91` — 2026-05-26T22:52:57Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d82d4e0c91c60f91` | `873d8b2e082cf6d6` | `873d8b2e082cf6d6` | `873d8b2e082cf6d6` |
| PR AUC | 0.9992 | 0.9983 | 0.9982 | 0.9987 |
| ROC AUC | 0.9949 | 0.9930 | 0.9927 | 0.9948 |
| Recall@3FPM | — | 0.8939 | 0.8857 | 0.9224 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d82d4e0c91c60f91
```
