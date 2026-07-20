# Confirm PASS — ecfceb97cefc49a5 on `filetypes/makefile`

Cycle `20260718T153349-confirm-ecfceb97cefc49a5` — 2026-07-18T15:33:49Z

PR_AUC held across 3 seeds (orig 0.7019)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ecfceb97cefc49a5` | `0fc0ace316bf51fa` | `0fc0ace316bf51fa` | `0fc0ace316bf51fa` |
| PR AUC | 0.7019 | 0.8228 | 0.5208 | 0.3966 |
| ROC AUC | 0.9317 | 0.9588 | 0.8715 | 0.8815 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ecfceb97cefc49a5
```
