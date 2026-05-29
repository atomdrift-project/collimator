# Confirm PASS — 1fac79200e861f20 on `filetypes/zip`

Cycle `20260526T234939-confirm-1fac79200e861f20` — 2026-05-26T23:49:39Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1fac79200e861f20` | `9fd28ac8932ed592` | `9fd28ac8932ed592` | `9fd28ac8932ed592` |
| PR AUC | 0.9998 | 0.9996 | 0.9996 | 0.9997 |
| ROC AUC | 0.9961 | 0.9938 | 0.9934 | 0.9943 |
| Recall@3FPM | — | 0.6413 | 0.6715 | 0.7340 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1fac79200e861f20
```
