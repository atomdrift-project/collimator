# Confirm PASS — 1af517c58a0108b8 on `filetypes/rtf`

Cycle `20260704T164707-confirm-1af517c58a0108b8` — 2026-07-04T16:47:07Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1af517c58a0108b8` | `4aa487f2a40743f3` | `4aa487f2a40743f3` | `4aa487f2a40743f3` |
| PR AUC | 0.9998 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9984 | 0.9975 | 0.9978 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1af517c58a0108b8
```
