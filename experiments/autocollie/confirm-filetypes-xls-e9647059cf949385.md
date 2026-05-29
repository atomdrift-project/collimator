# Confirm PASS — e9647059cf949385 on `filetypes/xls`

Cycle `20260525T193743-confirm-e9647059cf949385` — 2026-05-25T19:37:43Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e9647059cf949385` | `c43a2d44b6312cca` | `c43a2d44b6312cca` | `c43a2d44b6312cca` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.9887 | 0.9887 | 0.9864 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e9647059cf949385
```
