# Confirm PASS — 00b7d5c46b9106ff on `filetypes/macho`

Cycle `20260526T223814-confirm-00b7d5c46b9106ff` — 2026-05-26T22:38:14Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `00b7d5c46b9106ff` | `f942d0c5b77c4ae3` | `f942d0c5b77c4ae3` | `f942d0c5b77c4ae3` |
| PR AUC | 0.9995 | 0.9971 | 0.9973 | 0.9968 |
| ROC AUC | 0.9999 | 0.9994 | 0.9994 | 0.9994 |
| Recall@3FPM | — | 0.8571 | 0.8947 | 0.7744 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=00b7d5c46b9106ff
```
