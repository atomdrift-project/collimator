# Confirm PASS — 67aca28202ffd6d5 on `filetypes/go`

Cycle `20260713T015811-confirm-67aca28202ffd6d5` — 2026-07-13T01:58:11Z

PR_AUC held across 3 seeds (orig 0.9480)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `67aca28202ffd6d5` | `c87b084ef1b1d7da` | `c87b084ef1b1d7da` | `c87b084ef1b1d7da` |
| PR AUC | 0.9480 | 0.9479 | 0.9470 | 0.9451 |
| ROC AUC | 0.9748 | 0.9764 | 0.9746 | 0.9734 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=67aca28202ffd6d5
```
