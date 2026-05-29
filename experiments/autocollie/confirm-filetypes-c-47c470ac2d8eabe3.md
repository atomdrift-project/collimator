# Confirm PASS — 47c470ac2d8eabe3 on `filetypes/c`

Cycle `20260526T035310-confirm-47c470ac2d8eabe3` — 2026-05-26T03:53:10Z

PR_AUC held across 3 seeds (orig 0.9917)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `47c470ac2d8eabe3` | `a4475c2a6d4169c2` | `a4475c2a6d4169c2` | `a4475c2a6d4169c2` |
| PR AUC | 0.9917 | 0.9921 | 0.9916 | 0.9925 |
| ROC AUC | 0.9955 | 0.9958 | 0.9954 | 0.9959 |
| Recall@3FPM | — | 0.8125 | 0.8264 | 0.8171 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=47c470ac2d8eabe3
```
