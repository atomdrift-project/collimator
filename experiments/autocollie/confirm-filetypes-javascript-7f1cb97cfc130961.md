# Confirm PASS — 7f1cb97cfc130961 on `filetypes/javascript`

Cycle `20260613T220519-confirm-7f1cb97cfc130961` — 2026-06-13T22:05:19Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7f1cb97cfc130961` | `1a95b74f1a216acc` | `1a95b74f1a216acc` | `1a95b74f1a216acc` |
| PR AUC | 0.9976 | 0.9985 | 0.9985 | 0.9985 |
| ROC AUC | 0.9971 | 0.9979 | 0.9979 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7f1cb97cfc130961
```
