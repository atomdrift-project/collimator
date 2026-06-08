# Confirm PASS — b5ebf65854cd925c on `filetypes/ole`

Cycle `20260608T093740-confirm-b5ebf65854cd925c` — 2026-06-08T09:37:40Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b5ebf65854cd925c` | `926c8b9ba18a5cfb` | `926c8b9ba18a5cfb` | `926c8b9ba18a5cfb` |
| PR AUC | 0.9966 | 0.9973 | 0.9965 | 0.9973 |
| ROC AUC | 0.9960 | 0.9966 | 0.9958 | 0.9966 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b5ebf65854cd925c
```
