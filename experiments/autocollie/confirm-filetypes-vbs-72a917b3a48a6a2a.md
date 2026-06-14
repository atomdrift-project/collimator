# Confirm PASS — 72a917b3a48a6a2a on `filetypes/vbs`

Cycle `20260614T044917-confirm-72a917b3a48a6a2a` — 2026-06-14T04:49:17Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72a917b3a48a6a2a` | `f10ff0c8eccbcb59` | `f10ff0c8eccbcb59` | `f10ff0c8eccbcb59` |
| PR AUC | 0.9978 | 0.9971 | 0.9976 | 0.9975 |
| ROC AUC | 0.9926 | 0.9894 | 0.9913 | 0.9908 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=72a917b3a48a6a2a
```
