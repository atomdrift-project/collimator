# Confirm PASS — 3c05a7ec6a568d12 on `filegroups/source`

Cycle `20260528T051630-confirm-3c05a7ec6a568d12` — 2026-05-28T05:16:30Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3c05a7ec6a568d12` | `40529244ecd891d8` | `40529244ecd891d8` | `40529244ecd891d8` |
| PR AUC | 0.9991 | 0.9991 | 0.9992 | 0.9991 |
| ROC AUC | 0.9984 | 0.9982 | 0.9985 | 0.9983 |
| Recall@3FPM | — | 0.9367 | 0.9174 | 0.9226 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3c05a7ec6a568d12
```
