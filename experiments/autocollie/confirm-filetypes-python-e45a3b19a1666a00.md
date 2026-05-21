# Confirm PASS — e45a3b19a1666a00 on `filetypes/python`

Cycle `20260521T091006-confirm-e45a3b19a1666a00` — 2026-05-21T09:10:06Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e45a3b19a1666a00` | `af9163dbb4d0e7ea` | `af9163dbb4d0e7ea` | `af9163dbb4d0e7ea` |
| PR AUC | 0.9984 | 0.9985 | 0.9985 | 0.9985 |
| ROC AUC | 0.9986 | 0.9987 | 0.9987 | 0.9987 |
| Recall@3FPM | — | 0.8024 | 0.8050 | 0.8366 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e45a3b19a1666a00
```
