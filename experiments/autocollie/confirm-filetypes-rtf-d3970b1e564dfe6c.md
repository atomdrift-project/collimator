# Confirm PASS — d3970b1e564dfe6c on `filetypes/rtf`

Cycle `20260723T023047-confirm-d3970b1e564dfe6c` — 2026-07-23T02:30:47Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d3970b1e564dfe6c` | `a4fd148f0a64b76a` | `a4fd148f0a64b76a` | `a4fd148f0a64b76a` |
| PR AUC | 0.9993 | 0.9984 | 0.9994 | 0.9991 |
| ROC AUC | 0.9962 | 0.9913 | 0.9963 | 0.9944 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d3970b1e564dfe6c
```
