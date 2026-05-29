# Confirm PASS — d5b481af6e1c51cf on `filetypes/python-bytecode`

Cycle `20260526T224854-confirm-d5b481af6e1c51cf` — 2026-05-26T22:48:54Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d5b481af6e1c51cf` | `d6c82578902f1848` | `d6c82578902f1848` | `d6c82578902f1848` |
| PR AUC | 0.9985 | 0.9983 | 0.9981 | 0.9987 |
| ROC AUC | 0.9898 | 0.9925 | 0.9924 | 0.9947 |
| Recall@3FPM | — | 0.9388 | 0.8612 | 0.9184 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d5b481af6e1c51cf
```
