# Confirm PASS — 1d66e069eddefa6f on `filetypes/gz`

Cycle `20260526T205259-confirm-1d66e069eddefa6f` — 2026-05-26T20:52:59Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1d66e069eddefa6f` | `c0fc0be8cbd24bc2` | `c0fc0be8cbd24bc2` | `c0fc0be8cbd24bc2` |
| PR AUC | 1.0000 | 0.9984 | 0.9985 | 0.9985 |
| ROC AUC | 1.0000 | 0.9978 | 0.9980 | 0.9980 |
| Recall@3FPM | — | 0.9826 | 0.9913 | 0.9913 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1d66e069eddefa6f
```
