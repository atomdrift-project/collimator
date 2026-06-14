# Confirm PASS — d17dfd3b5b8f42be on `filetypes/package.json`

Cycle `20260613T014949-confirm-d17dfd3b5b8f42be` — 2026-06-13T01:49:49Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d17dfd3b5b8f42be` | `9aa1d9e19db02e88` | `9aa1d9e19db02e88` | `9aa1d9e19db02e88` |
| PR AUC | 0.9987 | 0.9991 | 0.9989 | 0.9989 |
| ROC AUC | 0.9979 | 0.9987 | 0.9983 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d17dfd3b5b8f42be
```
